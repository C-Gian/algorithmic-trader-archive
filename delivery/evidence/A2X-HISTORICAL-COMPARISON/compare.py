"""Descriptive historical comparison v0.6 / v0.6-a2x: tabulation from the two journals and passive traces only.

No engine is run by the tabulation (``--selftest`` builds small synthetic runs through the test harness). Conventions
are those registered in ``DESIGN.md``; this script implements them literally:

* population: every scenario whose first record is BIRTH, by the BIRTH clock time: evaluation [2025-09-01,
  2026-01-01), warmup (earlier, reported separately), tail (later); successors are attempts of their impulse;
* matching key (fixed before any result), from the trace facts at the scenario's first record:
  A = (A, direction, complete ordered source bars, impulse A, impulse B, S15, zone);
  B/C = (family, direction, complete ordered source bars, S15, zone, box low/up/mid);
  a key held by more than one scenario in a policy matches nothing (NON_UNIQUE); identifiers are never used;
* a successor is linked to its impulse by lineage (setup.impulse_id = lineage[1] = trace impulse), never by time;
* chains compared after removing envelopes (except the clock time) and the 12-hex rules-identity suffix of ids;
* an unmatched A birth is explained only by the other policy's traced birth-step state at the same dispatch and
  direction (Q_A, latch, owner); "deferred" needs the variant's deferral at that source close (record or trace).

Outputs in <out_dir>: results.json, impulses.csv, divergences.csv (deterministic; sha256 printed).

  .venv/Scripts/python.exe delivery/evidence/A2X-HISTORICAL-COMPARISON/compare.py <v06_run_dir> <a2x_run_dir> <out_dir>
  .venv/Scripts/python.exe delivery/evidence/A2X-HISTORICAL-COMPARISON/compare.py --selftest
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

WINDOW = ("2025-09-01T00:00:00Z", "2026-01-01T00:00:00Z")
ID_HASH = re.compile(r"(\d{2}:\d{2}:\d{2}(?:\+00:00|Z)?)-[0-9a-f]{12}(?![0-9a-f])")
CODE_SEG = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
A2X_OBS = "a_second_attempt"
REVIEW_CATS = ("REVIEW_OPEN", "REVIEW_NOT_OPENED", "REVIEW_CLOSED", "SUCCESSOR_ARMED",
               "RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL")
DNAME = {1: "LONG", -1: "SHORT"}


def zt(s: str | None) -> str | None:
    return None if s is None else s.replace("+00:00", "Z")


def norm_ids(s: str) -> str:
    return ID_HASH.sub(r"\1-*", s)


def code(reason: str | None) -> str | None:
    """Reason code: the leading upper-case segments (ids, bars and levels removed)."""
    if reason is None:
        return None
    out = []
    for seg in reason.split(":"):
        if not CODE_SEG.match(seg):
            break
        out.append(seg)
    return ":".join(out) if out else "<id>"


def drop_env(x):
    if isinstance(x, dict):
        return {k: drop_env(v) for k, v in x.items() if k != "env"}
    if isinstance(x, list):
        return [drop_env(v) for v in x]
    return x


def norm_record(e: dict) -> tuple:
    r = e["record"]
    return (e["kind"], zt(r["env"]["clock_time"]), norm_ids(json.dumps(drop_env(r), sort_keys=True, default=str)))


def khash(key) -> str | None:
    return None if key is None else hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16]


def window_of(t: str) -> str:
    return "warmup" if t < WINDOW[0] else "evaluation" if t < WINDOW[1] else "tail"


# ----------------------------------------------------------------------------------------------------------------------
# one policy
# ----------------------------------------------------------------------------------------------------------------------

class Policy:
    def __init__(self, name: str, journal: list[dict], trace: list[dict]) -> None:
        self.name = name
        self.journal = journal
        self.first: dict[str, dict] = {}
        self.qa: dict[tuple[str, int], dict] = {}
        self.qa_seq: dict[int, list[dict]] = defaultdict(list)
        self.deferrals: list[dict] = []
        for ev in trace:
            if ev["ev"] == "scenario_first":
                self.first[ev["sid"]] = ev
            elif ev["ev"] == "qa":
                ev = {**ev, "t": zt(ev["t"])}
                self.qa[(ev["t"], ev["d"])] = ev  # the LAST Q_A of the birth step decides (latch read before update)
                self.qa_seq[ev["d"]].append(ev)
            elif ev["ev"] == "deferral":
                self.deferrals.append({**ev, "t": zt(ev["t"])})
        self.scen: dict[str, list[dict]] = defaultdict(list)
        self.entries: dict[str, list[dict]] = defaultdict(list)
        self.calls: dict[str, dict] = {}
        self.revisions: dict[str, list[dict]] = defaultdict(list)
        self.obs: list[dict] = []
        self.entries_raw: dict[str, list[dict]] = defaultdict(list)
        for e in journal:
            r, k = e["record"], e["kind"]
            if k == "scenario":
                self.scen[r["scenario_id"]].append(e)
            elif k == "entry_attempt":
                self.entries[r["scenario_id"]].append(e)
            elif k == "call":
                self.calls[r["call_id"]] = e
            elif k == "call_revision":
                self.revisions[r["call_id"]].append(e)
            elif k == "observation" and r["name"] == A2X_OBS:
                self.obs.append(e)
        self.calls_by_sid: dict[str, list[dict]] = defaultdict(list)
        for e in self.calls.values():
            self.calls_by_sid[e["record"]["scenario_id"]].append(e)

    # -- identity ------------------------------------------------------------------------------------------------------

    def facts(self, sid: str) -> dict | None:
        return (self.first.get(sid) or {}).get("facts")

    def is_successor(self, sid: str | None) -> bool:
        f = self.facts(sid) if sid else None
        return bool(f and f["family"] == "A" and f["attempt"] == 2)

    def births(self) -> list[str]:
        """Every scenario that is not a successor (its first transition is checked to be BIRTH)."""
        return [sid for sid, recs in self.scen.items() if recs[0]["record"]["setup"].get("attempt") != "2"]

    def successors(self) -> list[str]:
        return [sid for sid, recs in self.scen.items() if recs[0]["record"]["setup"].get("attempt") == "2"]

    def birth_time(self, sid: str) -> str:
        return zt(self.scen[sid][0]["record"]["env"]["clock_time"])

    def key(self, sid: str):
        f = self.facts(sid)
        if f is None:
            return None
        if f["family"] == "A":
            if f["attempt"] != 1:
                return None
            return ["A", f["d"], f["sources"], f["impulse_A"], f["impulse_B"], f["s15"], f["z"]]
        b = f["box"]
        return [f["family"], f["d"], f["sources"], f["s15"], f["z"], None if b is None else [b["low"], b["up"], b["mid"]]]

    # -- chains --------------------------------------------------------------------------------------------------------

    def chain(self, sid: str) -> list[tuple]:
        es = list(self.scen[sid]) + list(self.entries.get(sid, []))
        for c in self.calls_by_sid.get(sid, []):
            es += [c] + self.revisions.get(c["record"]["call_id"], [])
        es.sort(key=lambda e: e["seq"])
        return [norm_record(e) for e in es]

    def summary(self, sid: str) -> dict:
        recs = [e["record"] for e in self.scen[sid]]
        trans = [r["transition"] for r in recs]
        last = recs[-1]
        terminal = (f"{last['terminal_state']}:{code(last['reason'])}" if last["status"] == "TERMINAL"
                    else "OPEN_AT_END")
        stage = "CONFIRMED" if "CONFIRM" in trans else "ARMED_NOT_CONFIRMED" if "ARM" in trans else "NO_ARM"
        out = {"stage": stage, "terminal": terminal,
               "v_failure_after_confirmation": stage == "CONFIRMED" and last["status"] == "TERMINAL"
               and last["terminal_state"] == "INVALIDATED" and code(last["reason"]) == "V_CONTACT",
               "confirmed_at": next((zt(r["confirmed_at"]) for r in recs if r["transition"] == "CONFIRM"), None),
               "terminal_at": zt(last["env"]["clock_time"]) if last["status"] == "TERMINAL" else None}
        out["child"] = self.child(sid) if stage == "CONFIRMED" else None
        out["calls"] = len(self.calls_by_sid.get(sid, []))
        return out

    def child(self, sid: str) -> str:
        if self.calls_by_sid.get(sid):
            return "ISSUED"
        es = self.entries.get(sid, [])
        if not es:
            return "NO_CHILD_RECORD"
        last = es[-1]["record"]
        if last["state"] == "TERMINAL":
            return f"NOT_ISSUED:{code(last['reason'])}"
        return f"CHILD_OPEN_AT_END:{last['state']}"

    # -- variant observations --------------------------------------------------------------------------------------

    def review_of(self, impulse: str) -> dict:
        got: dict = {"opened": None, "not_opened": None, "closed": None, "successor": None, "excluded": []}
        for e in self.obs:
            r = e["record"]
            v = r["values"]
            if v.get("impulse_id") != impulse:
                continue
            c, t = r["category"], zt(r["env"]["clock_time"])
            if c == "REVIEW_OPEN":
                got["opened"] = t
            elif c == "REVIEW_NOT_OPENED":
                got["not_opened"] = {"t": t, "reason": code(v["reason"])}
            elif c == "REVIEW_CLOSED":
                got["closed"] = {"t": t, "state": v["state"], "reason": code(v["reason"])}
            elif c == "SUCCESSOR_ARMED":
                got["successor"] = {"t": t, "sid": v["successor_id"]}
            elif c == "RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL":
                got["excluded"].append(t)
        return got


# ----------------------------------------------------------------------------------------------------------------------
# tabulation
# ----------------------------------------------------------------------------------------------------------------------

def tally(items) -> dict:
    return dict(sorted(Counter(items).items()))


def flow(p: Policy, window: str) -> dict:
    """Reconciled flow of the A impulses (first attempts) born in ``window`` and of their successors."""
    imps = [s for s in p.births() if p.facts(s) and p.facts(s)["family"] == "A" and window_of(p.birth_time(s)) == window]
    sm = {s: p.summary(s) for s in imps}
    conf = [s for s in imps if sm[s]["stage"] == "CONFIRMED"]
    fails = [s for s in conf if sm[s]["v_failure_after_confirmation"]]
    rv = {s: p.review_of(s) for s in fails}
    opened = [s for s in fails if rv[s]["opened"]]
    succ = {s: rv[s]["successor"]["sid"] for s in opened if rv[s]["successor"]}
    ssum = {x: p.summary(x) for x in succ.values()}
    sconf = [x for x in succ.values() if ssum[x]["stage"] == "CONFIRMED"]
    out = {
        "impulses": len(imps),
        "no_arm": tally(sm[s]["terminal"] for s in imps if sm[s]["stage"] == "NO_ARM"),
        "armed_not_confirmed": tally(sm[s]["terminal"] for s in imps if sm[s]["stage"] == "ARMED_NOT_CONFIRMED"),
        "confirmed": len(conf),
        "confirmed_terminal": tally(sm[s]["terminal"] for s in conf),
        "v_failures_after_confirmation": len(fails),
        "review_opened_admissible": len(opened),
        "review_not_opened": tally(rv[s]["not_opened"]["reason"] for s in fails if rv[s]["not_opened"]),
        "failures_without_review_record": len([s for s in fails if not rv[s]["opened"] and not rv[s]["not_opened"]]),
        "review_closed_without_successor": tally(f"{rv[s]['closed']['state']}:{rv[s]['closed']['reason']}"
                                                 for s in opened if rv[s]["closed"]),
        "review_open_at_end": len([s for s in opened if not rv[s]["closed"] and not rv[s]["successor"]]),
        "successors_armed": len(succ),
        "successor_not_confirmed": tally(ssum[x]["terminal"] for x in succ.values() if ssum[x]["stage"] != "CONFIRMED"),
        "successor_recovery_excluded": sum(len(rv[s]["excluded"]) for s in opened),
        "successor_confirmed": len(sconf),
        "successor_confirmed_terminal": tally(ssum[x]["terminal"] for x in sconf),
        "first_attempt_child": tally(sm[s]["child"] for s in conf),
        "successor_child": tally(ssum[x]["child"] for x in sconf),
        "calls_first_attempt": sum(sm[s]["calls"] for s in imps),
        "calls_successor": sum(ssum[x]["calls"] for x in succ.values()),
    }
    rec = {
        "impulses = no_arm + armed_not_confirmed + confirmed":
            out["impulses"] == sum(out["no_arm"].values()) + sum(out["armed_not_confirmed"].values()) + out["confirmed"],
        "confirmed = sum(confirmed_terminal)": out["confirmed"] == sum(out["confirmed_terminal"].values()),
        "v_failures = opened + not_opened + without_record":
            out["v_failures_after_confirmation"] == out["review_opened_admissible"] + sum(
                out["review_not_opened"].values()) + out["failures_without_review_record"],
        "opened = closed + successors + open_at_end":
            out["review_opened_admissible"] == sum(out["review_closed_without_successor"].values())
            + out["successors_armed"] + out["review_open_at_end"],
        "successors = not_confirmed + confirmed":
            out["successors_armed"] == sum(out["successor_not_confirmed"].values()) + out["successor_confirmed"],
        "confirmed = sum(first_attempt_child)": out["confirmed"] == sum(out["first_attempt_child"].values()),
        "successor_confirmed = sum(successor_child)": out["successor_confirmed"] == sum(out["successor_child"].values()),
        "calls_first_attempt = ISSUED": out["calls_first_attempt"] == out["first_attempt_child"].get("ISSUED", 0),
        "calls_successor = ISSUED": out["calls_successor"] == out["successor_child"].get("ISSUED", 0),
    }
    out["reconciliation"] = rec
    return out


def bc_flow(p: Policy, window: str) -> dict:
    out = {}
    for fam in ("B", "C"):
        ss = [s for s in p.births() if p.facts(s) and p.facts(s)["family"] == fam and window_of(p.birth_time(s)) == window]
        sm = {s: p.summary(s) for s in ss}
        conf = [s for s in ss if sm[s]["stage"] == "CONFIRMED"]
        out[fam] = {"births": len(ss), "stage": tally(sm[s]["stage"] for s in ss), "confirmed": len(conf),
                    "terminal": tally(sm[s]["terminal"] for s in ss), "child": tally(sm[s]["child"] for s in conf),
                    "calls": sum(sm[s]["calls"] for s in ss)}
    return out


def match(p6: Policy, px: Policy) -> dict:
    def index(p):
        idx: dict[str, list[str]] = defaultdict(list)
        for s in p.births():
            k = p.key(s)
            if k is not None:
                idx[khash(k)].append(s)
        return idx

    i6, ix = index(p6), index(px)
    pairs, non_unique = {}, {"v0.6": [], "v0.6-a2x": []}
    for h in sorted(set(i6) | set(ix)):
        a, b = i6.get(h, []), ix.get(h, [])
        if len(a) > 1:
            non_unique["v0.6"] += a
        if len(b) > 1:
            non_unique["v0.6-a2x"] += b
        if len(a) == 1 and len(b) == 1:
            pairs[a[0]] = b[0]
    no_key = {"v0.6": [s for s in p6.births() if p6.key(s) is None],
              "v0.6-a2x": [s for s in px.births() if px.key(s) is None]}
    m6 = set(pairs)
    mx = set(pairs.values())
    return {"pairs": pairs, "non_unique": non_unique, "no_key": no_key,
            "unmatched_v06": sorted((s for s in p6.births() if s not in m6), key=p6.birth_time),
            "unmatched_a2x": sorted((s for s in px.births() if s not in mx), key=px.birth_time)}


def birth_state(other: Policy, t: str, d: int) -> dict:
    """The other policy's traced birth-step state at the same dispatch and direction."""
    q = other.qa.get((t, d))
    if q is None:
        return {"cause": "NO_QA_TRACE"}
    base = {"qa": q["qa"], "latch": q["latch"], "owner": q["owner"], "reserved_for": q["reserved_for"]}
    if q["qa"] is not True:
        return {"cause": "QA_DIFFERS", **base}
    if q["owner"] is not None:
        if q["reserved_for"] or other.is_successor(q["owner"]):
            imp = q["reserved_for"] or other.facts(q["owner"])["impulse"]
            return {"cause": "SLOT_RESERVED_BY_SECOND_ATTEMPT", "impulse": imp, **base}
        return {"cause": "SLOT_OCCUPIED_BY_ORDINARY_SCENARIO", "occupant": q["owner"], **base}
    if q["latch"] == "NEED_FALSE":
        prev = [x for x in other.qa_seq[d] if x["t"] < t and x["owner"] is not None]
        held = prev[-1] if prev else None
        return {"cause": "LATCH_NOT_READY", "last_traced_owner": held and held["owner"],
                "last_traced_owner_at": held and held["t"], **base}
    return {"cause": "UNEXPLAINED", **base}


def deferral_link(px: Policy, t: str, d: int, src: str) -> str:
    for e in px.obs:
        r = e["record"]
        if (r["category"] == "ORDINARY_BIRTH_DEFERRED" and zt(r["env"]["clock_time"]) == t
                and r["values"]["direction"] == DNAME[d] and r["values"]["ordinary_source_close"] == src):
            return "RECORD"
    if any(x["t"] == t and x["d"] == d and x["src_close"] == src for x in px.deferrals):
        return "TRACE"
    return "NONE"


def compare(p6: Policy, px: Policy) -> dict:
    m = match(p6, px)
    pairs = m["pairs"]
    inv = {v: k for k, v in pairs.items()}
    div: list[dict] = []

    def short(p: Policy, sid: str) -> dict:
        f = p.facts(sid) or {}
        return {"sid": sid, "family": f.get("family"), "direction": DNAME.get(f.get("d")),
                "birth": p.birth_time(sid) if p.scen.get(sid) else None, "key": khash(p.key(sid)),
                "window": window_of(p.birth_time(sid)) if p.scen.get(sid) else None}

    # 1. matched scenarios: identical or different chains
    common = Counter()
    for a, b in sorted(pairs.items(), key=lambda kv: p6.birth_time(kv[0])):
        ca, cb = p6.chain(a), px.chain(b)
        fam = p6.facts(a)["family"]
        w = window_of(p6.birth_time(a))
        if ca == cb:
            common[(fam, w, "IDENTICAL")] += 1
            continue
        common[(fam, w, "DIFFERENT")] += 1
        i = next((j for j in range(min(len(ca), len(cb))) if ca[j] != cb[j]), min(len(ca), len(cb)))
        div.append({"type": "MATCHED_CHAIN_DIFFERS", "family": fam, "t": (ca[i] if i < len(ca) else cb[i])[1],
                    "v0.6": short(p6, a), "a2x": short(px, b), "first_difference_index": i,
                    "v0.6_record": ca[i][:2] + (json.loads(ca[i][2]).get("transition") or json.loads(ca[i][2]).get("state"),
                                                json.loads(ca[i][2]).get("reason")) if i < len(ca) else None,
                    "a2x_record": cb[i][:2] + (json.loads(cb[i][2]).get("transition") or json.loads(cb[i][2]).get("state"),
                                               json.loads(cb[i][2]).get("reason")) if i < len(cb) else None,
                    "v0.6_summary": p6.summary(a), "a2x_summary": px.summary(b)})

    # 2. the variant's reviews and added successors (lineage), per impulse
    for imp in sorted({e["record"]["values"]["impulse_id"] for e in px.obs if e["record"]["values"].get("impulse_id")},
                      key=lambda s: px.birth_time(s) if px.scen.get(s) else "~"):
        rv = px.review_of(imp)
        base = {"a2x_impulse": short(px, imp), "v0.6_counterpart": short(p6, inv[imp]) if imp in inv else None}
        if rv["not_opened"]:
            div.append({"type": "REVIEW_NOT_OPENED", "t": rv["not_opened"]["t"], "reason": rv["not_opened"]["reason"],
                        "family": "A", **base})
        if rv["opened"] and rv["successor"]:
            s2 = rv["successor"]["sid"]
            div.append({"type": "SUCCESSOR_ADDED", "t": rv["successor"]["t"], "family": "A", "review_opened": rv["opened"],
                        "successor": s2, "successor_summary": px.summary(s2),
                        "recovery_excluded_at": rv["excluded"], **base})
        elif rv["opened"]:
            div.append({"type": "REVIEW_CLOSED_WITHOUT_SUCCESSOR", "t": rv["closed"]["t"] if rv["closed"] else None,
                        "review_opened": rv["opened"], "closed": rv["closed"], "family": "A", **base})

    # 3. unmatched births, with the other policy's state at that dispatch
    for side, p, other in (("v0.6", p6, px), ("v0.6-a2x", px, p6)):
        unm = m["unmatched_v06"] if side == "v0.6" else m["unmatched_a2x"]
        for s in unm:
            f = p.facts(s)
            t = p.birth_time(s)
            d = {"type": f"BIRTH_ONLY_IN_{'V06' if side == 'v0.6' else 'A2X'}", "t": t,
                 "family": f["family"] if f else None, "birth": short(p, s), "summary": p.summary(s)}
            if f and f["family"] == "A":
                st = birth_state(other, t, f["d"])
                if st.get("occupant"):
                    occ = st["occupant"]
                    st["occupant_matched"] = occ in (inv if side == "v0.6" else pairs)
                    st["occupant_is_successor"] = other.is_successor(occ)
                    st["occupant_birth"] = other.birth_time(occ) if other.scen.get(occ) else None
                if st.get("impulse"):
                    st["impulse_matched"] = st["impulse"] in (inv if side == "v0.6" else pairs)
                d["other_policy_state"] = st
                if side == "v0.6" and st["cause"] == "SLOT_RESERVED_BY_SECOND_ATTEMPT":
                    link = deferral_link(px, t, f["d"], f["sources"][-1])
                    d["deferral_link"] = link
                    d["type"] = "BIRTH_DEFERRED" if link != "NONE" else "BIRTH_ONLY_IN_V06"
                    nxt = [x for x in px.births() if px.facts(x) and px.facts(x)["family"] == "A"
                           and px.facts(x)["d"] == f["d"] and px.birth_time(x) > t]
                    if nxt:
                        n0 = min(nxt, key=px.birth_time)
                        d["next_same_direction_a2x_birth"] = {**short(px, n0), "matched_to_a_v06_birth": n0 in inv}
            div.append(d)

    # 4. calls only in one policy (call key = scenario key or successor-of-impulse key, plus issue time)
    def call_keys(p: Policy, partner: dict) -> dict:
        out = {}
        for cid, e in p.calls.items():
            r = e["record"]
            sid = r["scenario_id"]
            if p.is_successor(sid):
                k = ["SUCCESSOR_OF", khash(p.key(p.facts(sid)["impulse"]))]
            else:
                k = [khash(p.key(sid))]
            out[json.dumps(k + [zt(r["issued_at"])])] = (cid, sid)
        return out

    k6, kx = call_keys(p6, pairs), call_keys(px, inv)
    for side, ka, kb, p in (("v0.6", k6, kx, p6), ("v0.6-a2x", kx, k6, px)):
        for k in sorted(set(ka) - set(kb)):
            cid, sid = ka[k]
            r = p.calls[cid]["record"]
            div.append({"type": f"CALL_ONLY_IN_{'V06' if side == 'v0.6' else 'A2X'}", "t": zt(r["issued_at"]),
                        "family": r["family"], "call": cid, "scenario": short(p, sid),
                        "attempt": 2 if p.is_successor(sid) else 1, "direction": r["direction"]})

    div.sort(key=lambda x: (x["t"] or "~", x["type"]))
    calls_common = len(set(k6) & set(kx))
    return {"matching": {"pairs": len(pairs), "by_family_window_chain": {f"{a}|{b}|{c}": n for (a, b, c), n in sorted(common.items())},
                         "non_unique": {k: [norm_ids(x) for x in v] for k, v in m["non_unique"].items()},
                         "no_key": {k: [norm_ids(x) for x in v] for k, v in m["no_key"].items()},
                         "unmatched_v06": len(m["unmatched_v06"]), "unmatched_a2x": len(m["unmatched_a2x"])},
            "calls": {"v0.6": len(p6.calls), "v0.6-a2x": len(px.calls), "common": calls_common},
            "divergences": div, "_m": m}


def other_kinds(p6: Policy, px: Policy) -> dict:
    """Observed effects on the other published records (views, landmarks, material changes, ordinary observations)."""
    out = {}
    for kind in ("market_view", "landmark", "material_change", "observation"):
        def recs(p):
            return Counter(norm_record(e) for e in p.journal if e["kind"] == kind
                           and not (kind == "observation" and e["record"]["name"] == A2X_OBS)
                           and WINDOW[0] <= zt(e["record"]["env"]["clock_time"]) < WINDOW[1])
        a, b = recs(p6), recs(px)
        only_a, only_b = a - b, b - a
        times = sorted({x[1] for x in only_a} | {x[1] for x in only_b})
        out[kind] = {"v0.6": sum(a.values()), "v0.6-a2x": sum(b.values()), "only_v0.6": sum(only_a.values()),
                     "only_a2x": sum(only_b.values()), "first_difference_at": times[0] if times else None,
                     "dispatches_with_difference": len(times)}
    return out


def checks(p6: Policy, px: Policy, res: dict) -> dict:
    c: dict[str, object] = {}
    for p in (p6, px):
        bad = []
        for sid, recs in p.scen.items():
            f = p.facts(sid)
            r0 = recs[0]["record"]
            if f is None:
                bad.append((sid, "NO_FACTS"))
                continue
            if r0["setup"]["sources"] != ",".join(f["sources"][-3:]):
                bad.append((sid, "SOURCES"))
            if f["family"] == "A" and (Decimal(r0["setup"]["impulse_A"]) != Decimal(f["impulse_A"])
                                       or Decimal(r0["setup"]["impulse_B"]) != Decimal(f["impulse_B"])):
                bad.append((sid, "GEOMETRY"))
            if r0["setup"]["s15"] != f["s15"] or r0["setup"]["zone_halfwidth"] != f["z"]:
                bad.append((sid, "SCALE_ZONE"))
            if r0["transition"] != ("ARM" if f["attempt"] == 2 else "BIRTH"):
                bad.append((sid, "FIRST_TRANSITION"))
        c[f"{p.name}: every scenario has trace facts consistent with its first record"] = not bad
        c[f"{p.name}: trace scenario ids = journal scenario ids"] = set(p.first) == set(p.scen)
        evq = [x for x in p.qa_seq[1] if WINDOW[0] <= x["t"] < WINDOW[1]]
        c[f"{p.name}: one traced birth step per 15m close of the evaluation window and direction"] = all(
            len({x["t"] for x in p.qa_seq[d] if WINDOW[0] <= x["t"] < WINDOW[1]}) == len(_quarters()) for d in (1, -1)) \
            and bool(evq)
        c[f"{p.name}: no BIRTH in the tail"] = not [s for s in p.births() if window_of(p.birth_time(s)) == "tail"]
    c["v0.6: no variant observation or attempt key"] = not p6.obs and not p6.successors()
    succ = px.successors()
    lin = []
    for s in succ:
        r0 = px.scen[s][0]["record"]
        f = px.facts(s)
        imp = r0["setup"]["impulse_id"]
        ok = (imp == r0["setup"]["parent_scenario_id"] == f["impulse"] == r0["env"]["lineage"][1]
              and imp in px.scen and px.facts(imp)["attempt"] == 1 and px.summary(imp)["v_failure_after_confirmation"]
              and (px.review_of(imp)["successor"] or {}).get("sid") == s)
        lin.append(ok)
    c["a2x: every successor linked by lineage to a confirmed first attempt failed at V, with its review records"] = all(lin)
    c["a2x: at most one successor per impulse"] = len({px.facts(s)["impulse"] for s in succ}) == len(succ)
    c["a2x: every review observation names an existing first attempt"] = all(
        e["record"]["values"].get("impulse_id") in px.scen and px.facts(e["record"]["values"]["impulse_id"])["attempt"] == 1
        for e in px.obs if e["record"]["category"] in REVIEW_CATS)
    held = [e["record"]["values"] for e in px.obs if e["record"]["category"] == "ORDINARY_BIRTH_DEFERRED"]
    c["a2x: every published deferral names the reserving first attempt or successor"] = all(
        v["impulse_id"] in px.scen and (v["reserved_by"] == f"{v['impulse_id']}#review" or v["reserved_by"] == v["impulse_id"])
        for v in held)
    for w in ("evaluation", "warmup"):
        c[f"a2x: every V failure after confirmation has a review record ({w})"] =             flow(px, w)["failures_without_review_record"] == 0
    m = res["_m"]
    c["matching: every pair is one-to-one"] = len(set(m["pairs"].values())) == len(m["pairs"])
    c["matching: matched + unmatched + non-unique + no-key = births (v0.6)"] = (
        len(m["pairs"]) + len(m["unmatched_v06"]) == len(p6.births()))
    c["matching: matched + unmatched + non-unique + no-key = births (a2x)"] = (
        len(m["pairs"]) + len(m["unmatched_a2x"]) == len(px.births()))
    c["matching: no non-unique key, no scenario without key"] = not any(m["non_unique"].values()) and not any(
        m["no_key"].values())
    return c


def _quarters() -> list[str]:
    from datetime import datetime, timedelta
    t = datetime.fromisoformat(WINDOW[0].replace("Z", "+00:00"))
    end = datetime.fromisoformat(WINDOW[1].replace("Z", "+00:00"))
    out = []
    while t < end:
        out.append(t)
        t += timedelta(minutes=15)
    return out


EXAMPLE_TYPES = ("SUCCESSOR_ADDED", "REVIEW_CLOSED_WITHOUT_SUCCESSOR", "REVIEW_NOT_OPENED", "BIRTH_DEFERRED",
                 "BIRTH_ONLY_IN_V06", "BIRTH_ONLY_IN_A2X", "MATCHED_CHAIN_DIFFERS", "CALL_ONLY_IN_V06", "CALL_ONLY_IN_A2X")


def examples(p6: Policy, px: Policy, res: dict) -> dict:
    """First chronological occurrence of each divergence type (registered criterion); records of the scenarios
    involved in both policies, from the impulse's birth to the involved scenarios' own last records."""
    m = res["_m"]
    pairs = m["pairs"]
    inv = {v: k for k, v in pairs.items()}
    out = {}

    def lines(p: Policy, sids: set[str]) -> list[str]:
        ls = []
        for e in p.journal:
            r, k = e["record"], e["kind"]
            sid = r.get("scenario_id")
            if k == "call_revision":
                sid = next((c["record"]["scenario_id"] for c in [p.calls.get(r["call_id"])] if c), None)
            if k == "observation" and r["name"] == A2X_OBS:
                v = r["values"]
                if v.get("impulse_id") in sids or v.get("successor_id") in sids:
                    ls.append(f"{zt(r['env']['clock_time'])} obs {r['category']} {code(v.get('reason')) or ''}"
                              f"{' ' + v['state'] if v.get('state') else ''}".rstrip())
                continue
            if sid not in sids or k not in ("scenario", "entry_attempt", "call", "call_revision"):
                continue
            if k == "scenario":
                ls.append(f"{zt(r['env']['clock_time'])} scenario {norm_ids(sid)} {r['transition']} "
                          f"{code(r['reason']) or ''} {r['terminal_state'] or ''} K={r['trigger_level']} "
                          f"V={r['invalidation_level']} R={r['reaction_level']} B={r['destination']}".replace("  ", " "))
            elif k == "entry_attempt":
                ls.append(f"{zt(r['env']['clock_time'])} entry {r['transition']} {r['state']} {code(r['reason']) or ''}")
            elif k == "call":
                ls.append(f"{zt(r['env']['clock_time'])} call {norm_ids(r['call_id'])} {r['direction']} "
                          f"V={r['invalidation']} T={r['target']} hard={zt(r['hard_deadline'])} ({r['hard_deadline_origin']})")
            else:
                ls.append(f"{zt(r['env']['clock_time'])} call_revision {r['entry_status']} {r['thesis_status']} "
                          f"{r['terminal_reason'] or ''}".rstrip())
        return ls

    for typ in EXAMPLE_TYPES:
        first = next((d for d in res["divergences"] if d["type"] == typ), None)
        if first is None:
            continue
        s6, sx = set(), set()
        for k in ("v0.6", "v0.6_counterpart"):
            if first.get(k):
                s6.add(first[k]["sid"])
        for k in ("a2x", "a2x_impulse"):
            if first.get(k):
                sx.add(first[k]["sid"])
        if first.get("successor"):
            sx.add(first["successor"])
        if typ.startswith("BIRTH"):
            mine, theirs = (s6, sx) if typ != "BIRTH_ONLY_IN_A2X" else (sx, s6)
            mine.add(first["birth"]["sid"])
            st = first.get("other_policy_state", {})
            for k in ("occupant", "impulse"):
                if st.get(k):
                    theirs.add(st[k])
        if typ.startswith("CALL"):
            (s6 if typ == "CALL_ONLY_IN_V06" else sx).add(first["scenario"]["sid"])
        # counterparts of the involved scenarios in the other policy (by the registered key only)
        s6 |= {inv[x] for x in sx if x in inv}
        sx |= {pairs[x] for x in s6 if x in pairs}
        for x in list(sx):
            if px.is_successor(x):
                sx.add(px.facts(x)["impulse"])
        out[typ] = {"divergence": {k: v for k, v in first.items() if k not in ("v0.6_summary", "a2x_summary")},
                    "v0.6": lines(p6, s6), "v0.6-a2x": lines(px, sx)}
    return out


def tabulate(p6: Policy, px: Policy) -> dict:
    res = compare(p6, px)
    out = {
        "window": WINDOW,
        "flow": {p.name: {w: flow(p, w) for w in ("evaluation", "warmup")} for p in (p6, px)},
        "bc": {p.name: {w: bc_flow(p, w) for w in ("evaluation", "warmup")} for p in (p6, px)},
        "matching": res["matching"], "calls": res["calls"],
        "divergence_counts": tally(d["type"] for d in res["divergences"]),
        "unmatched_birth_causes": tally(f"{d['type']}:{d.get('other_policy_state', {}).get('cause', 'NOT_A')}"
                                        f"{':' + d['deferral_link'] if d.get('deferral_link') else ''}"
                                        for d in res["divergences"] if d["type"].startswith("BIRTH")),
        "divergences": res["divergences"],
        "other_records": other_kinds(p6, px),
        "checks": checks(p6, px, res),
        "examples": examples(p6, px, res),
    }
    out["all_checks_pass"] = all(v is True for v in out["checks"].values()) and all(
        all(f["reconciliation"].values()) for pol in out["flow"].values() for f in pol.values())
    return out


def impulses_csv(p6: Policy, px: Policy, res: dict) -> str:
    m = match(p6, px)
    inv = {v: k for k, v in m["pairs"].items()}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["policy", "family", "window", "scenario", "attempt", "impulse", "key", "birth_or_arm", "direction",
                "stage", "terminal", "v_failure", "review", "child", "calls", "match"])
    for p, partner in ((p6, m["pairs"]), (px, inv)):
        for sid in sorted(p.scen, key=lambda s: (p.scen[s][0]["seq"])):
            f = p.facts(sid) or {}
            sm = p.summary(sid)
            imp = f.get("impulse")
            rv = p.review_of(sid) if sm["v_failure_after_confirmation"] and p.name == "v0.6-a2x" else None
            review = ("" if rv is None else "OPEN" if rv["opened"] else f"NOT_OPENED:{rv['not_opened']['reason']}"
                      if rv["not_opened"] else "NONE")
            if rv and rv["opened"]:
                review += f">{'SUCCESSOR' if rv['successor'] else (rv['closed'] or {}).get('state', 'OPEN_AT_END')}"
            w.writerow([p.name, f.get("family"), window_of(p.birth_time(sid)), sid, f.get("attempt"), imp or "", khash(p.key(sid)) or "", p.birth_time(sid),
                        DNAME.get(f.get("d")), sm["stage"], sm["terminal"], sm["v_failure_after_confirmation"], review,
                        sm["child"] or "", sm["calls"],
                        "SUCCESSOR_OF_" + ("MATCHED" if imp in partner else "UNMATCHED") if f.get("attempt") == 2
                        else "MATCHED" if sid in partner else "UNMATCHED"])
    return buf.getvalue()


def divergences_csv(res: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["t", "type", "family", "subject", "detail"])
    for d in res["divergences"]:
        subj = (d.get("birth") or d.get("a2x_impulse") or d.get("v0.6") or d.get("scenario") or {}).get("sid", "")
        detail = {k: v for k, v in d.items() if k not in ("t", "type", "family", "summary", "v0.6_summary", "a2x_summary")}
        w.writerow([d["t"], d["type"], d.get("family"), subj, json.dumps(detail, sort_keys=True, default=str)])
    return buf.getvalue()


def load(run: Path) -> tuple[list[dict], list[dict]]:
    with gzip.open(run / "journal.jsonl.gz", "rt", encoding="utf-8") as f:
        j = [json.loads(x) for x in f]
    with gzip.open(run / "trace.jsonl.gz", "rt", encoding="utf-8") as f:
        t = [json.loads(x) for x in f]
    return j, t


def write_outputs(p6: Policy, px: Policy, out: Path, extra_checks: dict | None = None) -> dict:
    res = tabulate(p6, px)
    if extra_checks:
        res["checks"].update(extra_checks)
        res["all_checks_pass"] = res["all_checks_pass"] and all(v is True for v in extra_checks.values())
    out.mkdir(parents=True, exist_ok=True)
    files = {"results.json": json.dumps(res, indent=1, sort_keys=True, default=str) + "\n",
             "impulses.csv": impulses_csv(p6, px, res), "divergences.csv": divergences_csv(compare(p6, px))}
    digests = {}
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
        digests[name] = hashlib.sha256(text.encode()).hexdigest()
    return {"res": res, "digests": digests}


# ----------------------------------------------------------------------------------------------------------------------
# self-test on synthetic tapes (test harness; hand-known structure from tests/adviser_a2x_fixtures.py)
# ----------------------------------------------------------------------------------------------------------------------

def _synthetic(ms, method: str):
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(HERE))
    from datetime import timedelta

    from adviser3_fixtures import DAY1, DAY2
    from instrument import install

    from algotrader.adviser.harness import build_events, make_runtime, temporal_for
    evs, cov = build_events(DAY1, ms)
    end = DAY1 + len(ms) * timedelta(minutes=1)
    rt = make_runtime(eval_start=DAY2, eval_end=end, method=method)
    temporal = temporal_for(cov)
    rt.attach(temporal)
    trace: list[dict] = []
    install(rt.core, lambda ev: trace.append(json.loads(json.dumps(ev, default=str))))
    for i, e in enumerate(evs):
        temporal.on_event(e, i)
        rt.before_admit(e)
        rt.admit(e, i)
    temporal.finish(end)
    rt.finish(end)
    j, _ = rt.take()
    return json.loads(json.dumps(j, default=str)), trace


def selftest() -> None:
    global WINDOW
    sys.path.insert(0, str(ROOT / "tests"))
    import adviser_a2x_fixtures as fx
    from adviser3_fixtures import DAY2, bar15

    from algotrader.adviser.harness import run_pure
    ok = []

    def check(name, cond):
        ok.append(bool(cond))
        print(("ok   " if cond else "FAIL ") + name)

    def pols(ms):
        global WINDOW
        from datetime import timedelta
        WINDOW = (DAY2.isoformat().replace("+00:00", "Z"),
                  (fx.DAY1 + len(ms) * timedelta(minutes=1)).isoformat().replace("+00:00", "Z"))
        j6, t6 = _synthetic(ms, "v0.6")
        jx, tx = _synthetic(ms, "v0.6-a2x")
        return Policy("v0.6", j6, t6), Policy("v0.6-a2x", jx, tx)

    # instrumentation is passive: the instrumented journals equal the harness journals
    ms = fx.two_calls()
    p6, px = pols(ms)
    ref6 = run_pure(fx.DAY1, ms, method="v0.6", eval_start=fx.DAY2).journal
    refx = run_pure(fx.DAY1, ms, method="v0.6-a2x", eval_start=fx.DAY2).journal
    check("instrumented journals digest-identical to the uninstrumented harness runs",
          [e["digest"] for e in p6.journal] == [e["digest"] for e in ref6]
          and [e["digest"] for e in px.journal] == [e["digest"] for e in refx])
    res = tabulate(p6, px)
    check("two_calls: all checks and reconciliations pass", res["all_checks_pass"])
    f6, fx_ = res["flow"]["v0.6"]["evaluation"], res["flow"]["v0.6-a2x"]["evaluation"]
    check("two_calls: one V failure after confirmation in both; v0.6 has no review", f6["v_failures_after_confirmation"] == 1
          == fx_["v_failures_after_confirmation"] and f6["review_opened_admissible"] == 0)
    check("two_calls: a2x review opened -> one successor -> confirmed -> issued",
          (fx_["review_opened_admissible"], fx_["successors_armed"], fx_["successor_confirmed"], fx_["calls_successor"])
          == (1, 1, 1, 1))
    check("two_calls: first-attempt flows identical", {k: v for k, v in f6.items() if not k.startswith(("review", "successor", "calls_successor", "failures_without"))}
          == {k: v for k, v in fx_.items() if not k.startswith(("review", "successor", "calls_successor", "failures_without"))})
    dc = res["divergence_counts"]
    check("two_calls: one SUCCESSOR_ADDED linked to a matched impulse, one CALL_ONLY_IN_A2X, nothing else",
          dc == {"CALL_ONLY_IN_A2X": 1, "SUCCESSOR_ADDED": 1}
          and next(d for d in res["divergences"] if d["type"] == "SUCCESSOR_ADDED")["v0.6_counterpart"] is not None)
    check("two_calls: every matched chain identical", all(k.endswith("IDENTICAL") for k in res["matching"]["by_family_window_chain"]))

    # deferred birth (published record) and the ordinary latch after release (test_reservation_defers_an_ordinary_birth)
    for side in ("L", "S"):
        p, after = Decimal(102400), []
        for c in (102500, 101800, 101300, 101200, 102000, 102800, 103300):
            after += bar15(p, Decimal(c) + 20, min(p, Decimal(c)) - 10, Decimal(c), order="LH")
            p = Decimal(c)
        ms = fx.reservation_defers_birth(after=after)
        p6, px = pols(ms if side == "L" else fx.short(ms))
        res = tabulate(p6, px)
        b6 = sorted(p6.birth_time(s)[11:16] for s in p6.births() if p6.facts(s)["family"] == "A")
        bx = sorted(px.birth_time(s)[11:16] for s in px.births() if px.facts(s)["family"] == "A")
        check(f"reservation {side}: births v0.6 03:30/05:15/07:30, a2x 03:30/07:30 (hand-known)",
              b6 == ["03:30", "05:15", "07:30"] and bx == ["03:30", "07:30"])
        dd = [d for d in res["divergences"] if d["type"].startswith("BIRTH")]
        check(f"reservation {side}: the 05:15 v0.6 birth is BIRTH_DEFERRED by RECORD, reserved for the matched impulse",
              len(dd) == 1 and dd[0]["type"] == "BIRTH_DEFERRED" and dd[0]["deferral_link"] == "RECORD"
              and dd[0]["t"].endswith("05:15:00Z") and dd[0]["other_policy_state"]["impulse_matched"] is True)
        check(f"reservation {side}: next same-direction a2x birth 07:30 is itself matched (not the same impulse)",
              dd[0]["next_same_direction_a2x_birth"]["birth"].endswith("07:30:00Z")
              and dd[0]["next_same_direction_a2x_birth"]["matched_to_a_v06_birth"] is True)
        check(f"reservation {side}: review closed without successor; checks pass",
              res["divergence_counts"].get("REVIEW_CLOSED_WITHOUT_SUCCESSOR") == 1 and res["all_checks_pass"])
        check(f"reservation {side}: examples are first occurrences with records of both policies",
              "BIRTH_DEFERRED" in res["examples"] and res["examples"]["BIRTH_DEFERRED"]["v0.6"]
              and res["examples"]["BIRTH_DEFERRED"]["v0.6-a2x"])

    # premise in the failure dispatch: review not opened, otherwise identical
    p6, px = pols(fx.premise_in_failure_dispatch())
    res = tabulate(p6, px)
    check("premise_in_failure_dispatch: REVIEW_NOT_OPENED only; chains identical",
          res["divergence_counts"] == {"REVIEW_NOT_OPENED": 1} and res["all_checks_pass"]
          and res["flow"]["v0.6-a2x"]["evaluation"]["review_not_opened"] == {"PREMISE_CLOSE_AT_OR_BEYOND_A_PLUS_Z_KNOWN": 1})

    # pure functions
    check("ids: only the 12-hex rules suffix is normalized",
          norm_ids("AL-2025-09-01T03:15:00+00:00-cdf01ef313c9#entry call-AL-2025-09-01T04:03:00+00:00-6f897d272af9")
          == "AL-2025-09-01T03:15:00+00:00-*#entry call-AL-2025-09-01T04:03:00+00:00-*")
    check("reason codes", (code("V_CONTACT:okx/x@1"), code("CONTEXT_OR_ADVERSE_EXPANSION:UP/EXPANSION:DOWN"),
                           code("SCENARIO_TERMINAL:INVALIDATED:V_CONTACT"), code("okx/BTC#obs@2025")) ==
          ("V_CONTACT", "CONTEXT_OR_ADVERSE_EXPANSION", "SCENARIO_TERMINAL:INVALIDATED:V_CONTACT", "<id>"))
    p6, px = pols(fx.two_calls())
    s1 = next(s for s in p6.births() if p6.facts(s)["family"] == "A")
    dup = Policy("v0.6", p6.journal, [ev for ev in _trace_of(p6)])
    fake = "AL-2025-09-01T09:00:00+00:00-000000000000"
    dup.first[fake] = {**dup.first[s1], "sid": fake}
    dup.scen[fake] = [{**dup.scen[s1][0], "seq": 10 ** 9}]
    m = match(dup, px)
    check("matching: a key held twice in one policy matches nothing (NON_UNIQUE)",
          s1 in m["non_unique"]["v0.6"] and fake in m["non_unique"]["v0.6"] and s1 not in m["pairs"])
    print(f"{sum(ok)}/{len(ok)} self-test checks pass")
    if not all(ok):
        raise SystemExit(1)


def _trace_of(p: Policy) -> list[dict]:
    return list(p.first.values()) + [v for vs in p.qa_seq.values() for v in vs] + list(p.deferrals)


def main(argv: list[str]) -> None:
    if argv[1:] == ["--selftest"]:
        selftest()
        return
    r6, rx, out = Path(argv[1]), Path(argv[2]), Path(argv[3])
    p6, px = Policy("v0.6", *load(r6)), Policy("v0.6-a2x", *load(rx))
    m6, mx = (json.loads((r / "run_manifest.json").read_text(encoding="utf-8")) for r in (r6, rx))
    flow_checks = {
        "runs: both applied every event of the cache": m6["events_applied"] == mx["events_applied"] == 679335,
        "runs: same clock end 2026-01-01T06:05Z": m6["clock_end"] == mx["clock_end"] == "2026-01-01T06:05:00Z",
        "runs: same final input commitment": m6["final_input_commitment"] == mx["final_input_commitment"],
        "runs: same temporal commitment (same market flow)": m6["temporal_commitment"] == mx["temporal_commitment"],
        "runs: same build, pack, cache and feed": all(m6[k] == mx[k] for k in (
            "build", "pack_id", "pack_manifest_sha256", "cache_id", "cache_manifest_sha256", "feed_content_identity")),
        "runs: methods v0.6 / v0.6-a2x, no evaluator": (m6["method"], mx["method"], m6["evaluator"], mx["evaluator"])
        == ("v0.6", "v0.6-a2x", None, None),
        "runs: journal and trace files equal their manifest hashes": all(
            hashlib.sha256((r / n).read_bytes()).hexdigest() == m["outputs_outside_git"][n]
            for r, m in ((r6, m6), (rx, mx)) for n in ("journal.jsonl.gz", "trace.jsonl.gz")),
    }
    got = write_outputs(p6, px, out, extra_checks=flow_checks)
    for k, v in got["digests"].items():
        print(f"{k} {v}")
    print("ALL CHECKS PASS" if got["res"]["all_checks_pass"] else "CHECK FAILURE")


if __name__ == "__main__":
    main(sys.argv)
