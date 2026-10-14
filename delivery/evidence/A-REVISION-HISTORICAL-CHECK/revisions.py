"""A revisions — descriptive historical check of the published A formulations (v0.6, Sep–Dec 2025).

Registered in REGISTRATION.md before any tabulation. Reads the reused local v0.6 journal and admitted trade 1m bars only:
no engine, no replay, no extraction, no acquisition. Stdlib only.

For every A scenario the journal's own scenario records (ordered by journal sequence) are rebuilt into a chain of
immutable formulations (ARM / REVISE / REARM, each with its own levels, observed source bar, publication time and
admitted cursor), observation-only gaps (ANCHOR_LOST -> WATCH) and, at most once, a confirmed formulation followed to the
scenario's actual terminal. The 1m/15m bars only corroborate what the journal states (source levels, contact and
confirmation minutes, absence of an earlier unrecorded contact/confirmation); they never reclassify an engine event.
Trigger/destination compatibility is DERIVED with the later formalized criterion (Tq = Kq + tick x trigger_ticks;
incompatible iff Tq >= Bq), never read as a v0.6 verdict.

  python revisions.py selftest
  python revisions.py run <run_dir> <out_dir>
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
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

WINDOW = ("2025-09-01T00:00:00Z", "2026-01-01T00:00:00Z")
TICK = Decimal("0.1")  # pinned instrument tick (manifest pins.tick)
TRIGGER_TICKS = 1  # v0.6 register trigger_offset_ticks (checked against every antecedent text)
MIN = timedelta(minutes=1)
Q15 = timedelta(minutes=15)
CODE_SEG = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
MINUTE_RID = re.compile(r"#obs@(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)$")
SOURCE_RID = re.compile(r"/15m/(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00)$")
ANTE = re.compile(r"close ([<>]=) (-?\d+(?:\.\d+)?) with (low >|high <) (-?\d+(?:\.\d+)?)")
PUBLISH = ("ARM", "REVISE", "REARM")


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def zs(t: datetime | None) -> str | None:
    return None if t is None else t.isoformat().replace("+00:00", "Z")


def code(reason: str | None) -> str:
    if not reason:
        return ""
    out = []
    for seg in reason.split(":"):
        if not CODE_SEG.match(seg):
            break
        out.append(seg)
    return ":".join(out) if out else "<id>"


def window_of(t: str) -> str:
    return "warmup" if t < WINDOW[0] else "evaluation" if t < WINDOW[1] else "tail"


@dataclass(frozen=True)
class Bar:
    start: datetime
    end: datetime
    o: Decimal
    h: Decimal
    lo: Decimal
    c: Decimal

    def q(self, d: int) -> tuple[Decimal, Decimal, Decimal]:
        """(high_q, low_q, close_q) in the direction-transformed domain q = d x price."""
        return (self.h, self.lo, self.c) if d > 0 else (-self.lo, -self.h, -self.c)


class Market:
    """Admitted trade 1m bars keyed by start (a missing minute is None) and complete UTC 15m bars keyed by start."""

    def __init__(self, bars: dict[datetime, Bar | None]) -> None:
        self.m1 = bars
        self.m15: dict[datetime, Bar] = {}
        if not bars:
            return
        q, last_end = min(bars), max(bars) + MIN
        q = q.replace(minute=q.minute - q.minute % 15)
        while q + Q15 <= last_end:
            ms = [bars.get(q + i * MIN) for i in range(15)]
            if all(m is not None for m in ms):
                self.m15[q] = Bar(q, q + Q15, ms[0].o, max(m.h for m in ms), min(m.lo for m in ms), ms[-1].c)
            q += Q15

    def minutes(self, start: datetime, end: datetime) -> list[Bar | None]:
        """Minutes whose start is in [start, end) - None where the minute is missing."""
        out, m = [], start.replace(second=0, microsecond=0)
        if m < start:
            m += MIN
        while m < end:
            out.append(self.m1.get(m))
            m += MIN
        return out


def q(x: str | Decimal | None, d: int) -> Decimal | None:
    return None if x is None else Decimal(x) * d


# ----------------------------------------------------------------------------------------------------------------------
# terminal and segment-end vocabularies (registered)
# ----------------------------------------------------------------------------------------------------------------------

def terminal_class(state: str, reason: str) -> str:
    c = code(reason)
    if state == "DESTINATION_REACHED":
        return "DESTINATION"
    if state == "INVALIDATED":
        return "V_CONTACT"
    if state == "TIME_EXPIRED":
        return "HARD_DEADLINE"
    if state == "STALLED":
        return "STALLED"
    if state == "EXPIRED" and c == "ORIGINAL_SETUP_DEADLINE":
        return "ORIGINAL_SETUP_EXPIRY"
    if state == "EXPIRED":
        return f"EXPIRED:{c}"
    if state == "WITHDRAWN" and c.startswith("CONTEXT"):
        return "CONTEXT_WITHDRAWAL"
    if state == "WITHDRAWN":
        return f"STRUCTURAL_WITHDRAWAL:{c}"
    if state == "UNASSESSABLE":
        if "AMBIGUOUS" in reason:
            return "AMBIGUOUS"
        if any(k in reason for k in ("GAP", "STALE", "COVERAGE", "UNAVAILABLE")):
            return "DATA_LOSS"
        return f"UNASSESSABLE:{c}"
    return f"OTHER:{state}:{c}"


def armed_end(tc: str) -> str:
    """End category of an ACTIVE formulation ended by a scenario terminal."""
    if tc == "DESTINATION":
        return "DESTINATION_BEFORE_CONFIRMATION"
    if tc == "ORIGINAL_SETUP_EXPIRY":
        return "ORIGINAL_SETUP_EXPIRY"
    if tc in ("AMBIGUOUS", "DATA_LOSS"):
        return tc
    if tc in ("V_CONTACT", "HARD_DEADLINE", "STALLED"):
        return ""  # impossible before confirmation in v0.6 A: linkage failure
    return "STRUCTURAL_OR_CONTEXT_TERMINAL"


def gap_end(tc: str) -> str:
    if tc == "DESTINATION":
        return "DESTINATION_IN_OBSERVATION_GAP"
    return armed_end(tc)


# ----------------------------------------------------------------------------------------------------------------------
# one scenario
# ----------------------------------------------------------------------------------------------------------------------

class Linkage(Exception):
    pass


def formulation(e: dict, mk: Market, d: int, idx: int) -> dict:
    r = e["record"]
    t = dt(e["clock_time"])
    K, V, R, B = q(r["trigger_level"], d), q(r["invalidation_level"], d), q(r["reaction_level"], d), q(r["destination"], d)
    T = K + TICK * TRIGGER_TICKS
    src = r.get("anchor_source") or ""
    m = SOURCE_RID.search(src)
    if None in (K, V, R, B) or m is None:
        raise Linkage(f"{r['transition']} seq {e['seq']}: levels or source missing")
    s_start = dt(m.group(1))
    sb = mk.m15.get(s_start)
    checks = {}
    if sb is None:
        raise Linkage(f"{r['transition']} seq {e['seq']}: source 15m bar {zs(s_start)} unavailable")
    h_q, l_q, _ = sb.q(d)
    z = Decimal(r["setup"]["zone_halfwidth"])
    ante = ANTE.search(r.get("antecedent") or "")
    checks["published at/after the end of its source bar"] = t >= sb.end
    checks["K = source high (q), R = source low (q), V = R - z"] = K == h_q and R == l_q and V == R - z
    checks["antecedent threshold = K + tick x trigger_ticks and V"] = (
        ante is not None and Decimal(ante.group(2)) * d == T and Decimal(ante.group(4)) * d == V
        and ante.group(1) == (">=" if d > 0 else "<="))
    checks["publication fields = envelope time/cursor"] = (
        r.get("anchor_published_at") == e["clock_time"] and r.get("anchor_published_cursor") == e["factual_cursor"])
    checks["epoch = index"] = r.get("anchor_epoch") == idx
    bad = [k for k, ok in checks.items() if not ok]
    if bad:
        raise Linkage(f"{r['transition']} seq {e['seq']}: " + "; ".join(bad))
    return {"kind": "FORMULATION", "transition": r["transition"], "epoch": idx, "seq": e["seq"],
            "observed_from": zs(sb.start), "observed_to": zs(sb.end), "published_at": e["clock_time"],
            "published_cursor": e["factual_cursor"], "K": r["trigger_level"], "R": r["reaction_level"],
            "V": r["invalidation_level"], "B": r["destination"], "T": str(T * d), "premise": r.get("premise"),
            "original_expiry": r.get("original_expiry"),
            "derived_trigger_destination": "INCOMPATIBLE" if T >= B else "COMPATIBLE",
            "_t": t, "_K": K, "_V": V, "_B": B, "_T": T,
            "end_category": None, "end_detail": None, "ended_at": None, "ended_seq": None, "ended_cursor": None,
            "audit": []}


def close(seg: dict, e: dict | None, cat: str, detail: str = "") -> None:
    seg["end_category"], seg["end_detail"] = cat, detail
    if e is not None:
        seg["ended_at"], seg["ended_seq"], seg["ended_cursor"] = e["clock_time"], e["seq"], e["factual_cursor"]


def minute_of(reason: str | None) -> datetime | None:
    m = MINUTE_RID.search(reason or "")
    return dt(m.group(1)) if m else None


def audit_domain(seg: dict, mk: Market, d: int, end_t: datetime | None, data_end: datetime, b_from: datetime,
                 gap: bool = False) -> list[str]:
    """Bars inside a formulation's (or gap's) own domain BEFORE its ending dispatch must show no unrecorded V contact,
    destination contact or qualifying confirmation minute. A qualifying minute admitted IN the ending dispatch is
    reported separately (same-dispatch boundary), not as an anomaly."""
    start = seg["_t"]
    stop = end_t or data_end
    notes = []
    for b in mk.minutes(start, stop):
        if b is None:
            notes.append("MISSING_MINUTE")
            continue
        h, lo, c = b.q(d)
        last = b.end >= stop  # admitted in the ending dispatch (or beyond)
        if b.end > stop:
            continue
        hit_b = b.start >= b_from and h >= seg["_B"]
        if gap:
            if hit_b and not last:
                notes.append(f"UNRECORDED_DESTINATION_CONTACT:{zs(b.start)}")
            continue
        hit_v = lo <= seg["_V"]
        if (hit_v or hit_b) and not last:
            notes.append(f"UNRECORDED_{'V' if hit_v else 'DESTINATION'}_CONTACT:{zs(b.start)}")
        elif c >= seg["_T"] and not hit_v and not hit_b:
            notes.append(("QUALIFYING_MINUTE_IN_ENDING_DISPATCH:" if last else "UNRECORDED_QUALIFYING_MINUTE:")
                         + zs(b.start))
    return notes


def chain(entries: list[dict], mk: Market, data_end: datetime) -> dict:
    entries = sorted(entries, key=lambda e: e["seq"])
    r0 = entries[0]["record"]
    d = 1 if r0["direction"] == "LONG" else -1
    out = {"scenario_id": r0["scenario_id"], "direction": r0["direction"], "born_at": entries[0]["clock_time"],
           "born_seq": entries[0]["seq"], "born_cursor": entries[0]["factual_cursor"],
           "window": window_of(entries[0]["clock_time"]),
           "events": [{"seq": e["seq"], "transition": e["record"]["transition"], "clock_time": e["clock_time"],
                       "cursor": e["factual_cursor"], "status": e["record"].get("status"),
                       "anchor_epoch": e["record"].get("anchor_epoch"), "anchor_status": e["record"].get("anchor_status"),
                       "reason": e["record"].get("reason"), "K": e["record"].get("trigger_level"),
                       "V": e["record"].get("invalidation_level"), "B": e["record"].get("destination")}
                      for e in entries],
           "segments": [], "confirmed": None, "terminal": None, "linkage": None}
    try:
        _chain(entries, mk, d, data_end, out)
    except Linkage as x:
        out["linkage"] = str(x)
    out["category"], out["detail"] = scenario_category(out)
    return out


def _chain(entries: list[dict], mk: Market, d: int, data_end: datetime, out: dict) -> None:
    if entries[0]["record"]["transition"] != "BIRTH":
        raise Linkage("first record is not BIRTH")
    if len({e["seq"] for e in entries}) != len(entries):
        raise Linkage("duplicate journal sequence")
    state, cur, gap, conf, first_arm = "UNARMED", None, None, None, None
    segs = out["segments"]
    for e in entries[1:]:
        r, tr = e["record"], e["record"]["transition"]
        t = dt(e["clock_time"])
        if out["terminal"] is not None:
            raise Linkage(f"{tr} seq {e['seq']} after TERMINAL")
        if tr == "BIRTH":
            raise Linkage(f"second BIRTH seq {e['seq']}")
        if tr in PUBLISH:
            want = {"UNARMED": "ARM", "ARMED": "REVISE", "GAP": "REARM"}.get(state)
            if tr != want:
                raise Linkage(f"{tr} seq {e['seq']} in state {state}")
            prev = r.get("previous_anchor") or {}
            if tr == "REVISE":
                if prev.get("epoch") != str(cur["epoch"]) or prev.get("status") != "SUPERSEDED":
                    raise Linkage(f"REVISE seq {e['seq']}: previous anchor does not link to epoch {cur['epoch']}")
                close(cur, e, "SUPERSEDED_BY_REVISION", code(prev.get("reason")))
            if tr == "REARM":
                lost = segs[-2] if gap is segs[-1] else None
                if lost is None or prev.get("epoch") != str(lost["epoch"]) or prev.get("status") not in (
                        "INVALIDATED", "UNASSESSABLE"):
                    raise Linkage(f"REARM seq {e['seq']}: previous anchor does not link to the lost epoch")
                close(gap, e, "REARM", code(r.get("reason")))
            idx = 1 if tr == "ARM" else (cur or segs[-2])["epoch"] + 1
            f = formulation(e, mk, d, idx)
            if tr == "ARM":
                first_arm = f["_t"]
            if segs and segs[-1]["ended_seq"] is not None and segs[-1]["ended_seq"] > e["seq"]:
                raise Linkage("overlapping domains")
            segs.append(f)
            cur, gap, state = f, None, "ARMED"
        elif tr == "ANCHOR_LOST":
            if state != "ARMED":
                raise Linkage(f"ANCHOR_LOST seq {e['seq']} in state {state}")
            prev = r.get("previous_anchor") or {}
            if prev.get("epoch") != str(cur["epoch"]):
                raise Linkage(f"ANCHOR_LOST seq {e['seq']}: previous anchor does not link to epoch {cur['epoch']}")
            status = r.get("anchor_status")
            m = minute_of(prev.get("interval"))
            if status == "INVALIDATED":
                b = mk.m1.get(m) if m else None
                if b is None or b.start < cur["_t"] or b.end > t or b.q(d)[1] > cur["_V"]:
                    raise Linkage(f"ANCHOR_LOST seq {e['seq']}: certified V contact not corroborated by its minute")
                close(cur, e, "ANCHOR_LOST_CERTIFIED", code(r.get("reason")))
            elif status == "UNASSESSABLE":
                close(cur, e, "ANCHOR_LOST_AMBIGUOUS", code(r.get("reason")))
            else:
                raise Linkage(f"ANCHOR_LOST seq {e['seq']}: anchor status {status}")
            gap = {"kind": "OBSERVATION_GAP", "transition": "WATCH", "epoch": None, "seq": e["seq"],
                   "published_at": e["clock_time"], "published_cursor": e["factual_cursor"], "_t": t,
                   "_B": cur["_B"], "B": cur["B"], "after_epoch": cur["epoch"], "end_category": None,
                   "end_detail": None, "ended_at": None, "ended_seq": None, "ended_cursor": None, "audit": []}
            segs.append(gap)
            cur, state = None, "GAP"
        elif tr == "CONFIRM":
            if state != "ARMED" or r.get("anchor_epoch") != cur["epoch"]:
                raise Linkage(f"CONFIRM seq {e['seq']} does not link to the active formulation")
            m = minute_of(r.get("reason"))
            b = mk.m1.get(m) if m else None
            if b is None:
                raise Linkage(f"CONFIRM seq {e['seq']}: confirming minute unavailable")
            h, lo, c = b.q(d)
            ok = {"minute starts at/after the formulation's publication (no source-bar reuse)": b.start >= cur["_t"],
                  "minute admitted at/before the confirmation dispatch": b.end <= t,
                  "close reaches T": c >= cur["_T"], "low/high keeps V": lo > cur["_V"],
                  "confirmation close = minute close": Decimal(r["confirmation_close"]) == b.c,
                  "levels unchanged at confirmation": (q(r["trigger_level"], d) == cur["_K"]
                                                      and q(r["invalidation_level"], d) == cur["_V"]
                                                      and q(r["destination"], d) == cur["_B"])}
            bad = [k for k, v in ok.items() if not v]
            if bad:
                raise Linkage(f"CONFIRM seq {e['seq']}: " + "; ".join(bad))
            close(cur, e, "CONFIRMED_ON_THIS_FORMULATION", zs(b.start))
            conf = {"epoch": cur["epoch"], "transition": cur["transition"], "minute": zs(b.start),
                    "confirmed_at": e["clock_time"], "confirmed_cursor": e["factual_cursor"], "seq": e["seq"],
                    "confirmed_deadline": r.get("confirmed_deadline"), "_t": t, "_V": cur["_V"], "_B": cur["_B"],
                    "compat": cur["derived_trigger_destination"]}
            out["confirmed"] = conf
            cur, state = None, "CONFIRMED"
        elif tr == "OWNER_RELEASE":
            continue
        elif tr == "TERMINAL":
            tc = terminal_class(r.get("terminal_state") or "", r.get("reason") or "")
            m = minute_of(r.get("reason"))
            if tc in ("DESTINATION", "V_CONTACT"):
                b = mk.m1.get(m) if m else None
                lim = conf["_t"] if state == "CONFIRMED" else first_arm
                lvl = (conf or cur or gap or {}).get("_V" if tc == "V_CONTACT" else "_B")
                good = b is not None and lim is not None and b.start >= lim and b.end <= t and lvl is not None and (
                    b.q(d)[0] >= lvl if tc == "DESTINATION" else b.q(d)[1] <= lvl)
                if not good:
                    raise Linkage(f"TERMINAL seq {e['seq']}: {tc} not corroborated by its minute")
            if state == "ARMED":
                cat = armed_end(tc)
                if not cat:
                    raise Linkage(f"TERMINAL {tc} seq {e['seq']} while armed")
                close(cur, e, cat, tc)
            elif state == "GAP":
                cat = gap_end(tc)
                if not cat:
                    raise Linkage(f"TERMINAL {tc} seq {e['seq']} in an observation gap")
                close(gap, e, cat, tc)
            out["terminal"] = {"class": tc, "state": r.get("terminal_state"), "reason": code(r.get("reason")),
                               "at": e["clock_time"], "seq": e["seq"], "cursor": e["factual_cursor"],
                               "phase": {"UNARMED": "NEVER_ARMED", "ARMED": "ARMED", "GAP": "OBSERVATION_GAP",
                                         "CONFIRMED": "CONFIRMED"}[state]}
        else:
            raise Linkage(f"unknown transition {tr}")
    if out["terminal"] is None:
        for s in (cur, gap):
            if s is not None:
                close(s, None, "OPEN_AT_DATA_END")
    # domain audits (bars inside each formulation / gap before its ending dispatch)
    for s in segs:
        end = dt(s["ended_at"]) if s["ended_at"] else None
        s["audit"] = audit_domain(s, mk, d, end, data_end, first_arm, gap=s["kind"] == "OBSERVATION_GAP")
        if s["end_category"] == "CONFIRMED_ON_THIS_FORMULATION":
            # amendment 1: the recorded confirming minute is not an audit note; it must be the first qualifying minute
            own = f"QUALIFYING_MINUTE_IN_ENDING_DISPATCH:{s['end_detail']}"
            s["confirming_minute_first_qualifying"] = own in s["audit"] and not any(
                a.startswith("UNRECORDED_QUALIFYING_MINUTE") for a in s["audit"])
            s["audit"] = [a for a in s["audit"] if a != own]
    if conf is not None:
        end = dt(out["terminal"]["at"]) if out["terminal"] else data_end
        post = []
        for b in mk.minutes(conf["_t"], end):
            if b is None:
                post.append("MISSING_MINUTE")
            elif b.end < end and (b.q(d)[1] <= conf["_V"] or b.q(d)[0] >= conf["_B"]):
                post.append(f"UNRECORDED_POST_CONFIRMATION_CONTACT:{zs(b.start)}")
        conf["audit"] = post


def scenario_category(o: dict) -> tuple[str, str]:
    if o["linkage"]:
        return "NOT_RECONSTRUCTABLE", o["linkage"]
    segs = [s for s in o["segments"] if s["kind"] == "FORMULATION"]
    term = o["terminal"]
    tc = term["class"] if term else "OPEN_AT_DATA_END"
    if not segs:
        return "NEVER_ARMED", tc
    if o["confirmed"] is not None:
        c = o["confirmed"]
        if c["epoch"] == 1:
            return "CONFIRMED_ON_ORIGINAL_FORMULATION", tc
        return {"REVISE": "CONFIRMED_ON_REVISED_FORMULATION", "REARM": "CONFIRMED_ON_REARMED_FORMULATION"}[
            c["transition"]], tc
    last = o["segments"][-1]
    return "ARMED_NEVER_CONFIRMED", last["end_category"]


# ----------------------------------------------------------------------------------------------------------------------
# population, tables, checks
# ----------------------------------------------------------------------------------------------------------------------

def children_and_calls(journal: list[dict]) -> tuple[dict, dict]:
    child: dict[str, list[dict]] = defaultdict(list)
    calls: dict[str, list[str]] = defaultdict(list)
    for e in journal:
        r = e["record"]
        if e["kind"] == "entry_attempt" and r.get("family") == "A":
            child[r["scenario_id"]].append({"seq": e["seq"], "transition": r.get("transition"),
                                            "state": r.get("state"), "reason": code(r.get("reason")),
                                            "call_id": r.get("call_id")})
        elif e["kind"] == "call" and r.get("family") == "A" and r.get("call_id") not in calls[r["scenario_id"]]:
            calls[r["scenario_id"]].append(r.get("call_id"))
    return child, calls


def build(journal: list[dict], mk: Market, data_end: datetime) -> list[dict]:
    per: dict[str, list[dict]] = defaultdict(list)
    for e in journal:
        if e["kind"] == "scenario" and e["record"].get("family") == "A":
            per[e["record"]["scenario_id"]].append(e)
    child, calls = children_and_calls(journal)
    obs = []
    for sid in sorted(per):
        o = chain(per[sid], mk, data_end)
        ch = child.get(sid, [])
        o["child"] = {"records": len(ch), "transitions": dict(Counter(x["transition"] for x in ch)),
                      "final": f"{ch[-1]['state']}:{ch[-1]['reason']}" if ch else None}
        o["calls"] = calls.get(sid, [])
        obs.append(o)
    return sorted(obs, key=lambda o: (o["born_at"], o["scenario_id"]))


def tables(obs: list[dict], window: str) -> dict:
    xs = [o for o in obs if o["window"] == window]
    cat = Counter(o["category"] for o in xs)
    detail = defaultdict(Counter)
    for o in xs:
        detail[o["category"]][o["detail"]] += 1
    confirmed = [o for o in xs if o["confirmed"] is not None]
    conf_x = defaultdict(Counter)
    for o in confirmed:
        g = "original" if o["confirmed"]["epoch"] == 1 else "revised_or_rearmed"
        conf_x[g][o["terminal"]["class"] if o["terminal"] else "OPEN_AT_DATA_END"] += 1
    path = defaultdict(Counter)
    for o in confirmed:
        if o["confirmed"]["epoch"] > 1:
            kinds = [s["transition"] for s in o["segments"]]
            path[o["confirmed"]["transition"]]["with an anchor loss" if "WATCH" in kinds else "without anchor loss"] += 1
    seg_end = defaultdict(Counter)
    gap_end_ = Counter()
    compat = defaultdict(Counter)
    for o in xs:
        for s in o["segments"]:
            if s["kind"] == "FORMULATION":
                seg_end[s["transition"]][s["end_category"]] += 1
                compat[f"{s['transition']}:{s['derived_trigger_destination']}"][s["end_category"]] += 1
            else:
                gap_end_[s["end_category"]] += 1
    first_formulation = Counter()
    for o in xs:
        f = next((s for s in o["segments"] if s["kind"] == "FORMULATION"), None)
        if f is None or o["linkage"]:
            continue
        later = o["confirmed"] is not None and o["confirmed"]["epoch"] > 1
        first_formulation[f"first formulation {f['end_category']}" + (
            " -> later confirmation on another formulation" if later else "")] += 1
    child = Counter(o["child"]["final"] or "NO_CHILD_RECORD" for o in xs)
    return {
        "scenarios": len(xs), "categories": dict(sorted(cat.items())),
        "category_detail": {k: dict(sorted(v.items())) for k, v in sorted(detail.items())},
        "confirmed_terminal_crosstab": {k: dict(sorted(v.items())) for k, v in sorted(conf_x.items())},
        "non_original_confirmation_paths": {k: dict(sorted(v.items())) for k, v in sorted(path.items())},
        "formulation_ends__publications_not_independent_scenarios": {
            k: dict(sorted(v.items())) for k, v in sorted(seg_end.items())},
        "observation_gap_ends__publications_not_independent_scenarios": dict(sorted(gap_end_.items())),
        "derived_trigger_destination_by_formulation_end": {k: dict(sorted(v.items())) for k, v in sorted(compat.items())},
        "first_formulation_fate": dict(sorted(first_formulation.items())),
        "children_final_state__separate_from_scenarios": dict(sorted(child.items())),
        "calls": sorted(c for o in xs for c in o["calls"]),
        "formulations": sum(1 for o in xs for s in o["segments"] if s["kind"] == "FORMULATION"),
        "observation_gaps": sum(1 for o in xs for s in o["segments"] if s["kind"] == "OBSERVATION_GAP"),
    }


def checks(obs: list[dict], journal: list[dict]) -> dict:
    a_ids = {e["record"]["scenario_id"] for e in journal if e["kind"] == "scenario" and e["record"].get("family") == "A"}
    births = [e for e in journal if e["kind"] == "scenario" and e["record"].get("family") == "A"
              and e["record"]["transition"] == "BIRTH"]
    seqs = [e["seq"] for e in journal]
    c = {}
    c["every A scenario appears once"] = sorted(o["scenario_id"] for o in obs) == sorted(a_ids) and len(obs) == len(a_ids)
    c["one BIRTH per A scenario"] = len(births) == len(a_ids)
    c["journal sequence strictly increasing and record ids unique"] = (
        all(a < b for a, b in zip(seqs, seqs[1:])) and len({e["record_id"] for e in journal}) == len(journal))
    ok_order = ok_dom = ok_conf = ok_epoch = True
    for o in obs:
        if o["linkage"]:
            continue
        ss = o["segments"]
        prev_end = o["born_seq"]
        for s in ss:
            ok_order &= s["seq"] >= prev_end
            ok_dom &= s["ended_seq"] is None or s["ended_seq"] >= s["seq"]
            ok_dom &= s["ended_at"] is None or s["ended_at"] >= s["published_at"]
            prev_end = s["ended_seq"] if s["ended_seq"] is not None else prev_end
        fs = [s for s in ss if s["kind"] == "FORMULATION"]
        ok_epoch &= [s["epoch"] for s in fs] == list(range(1, len(fs) + 1))
        if o["confirmed"] is not None:
            cs = [s for s in fs if s["end_category"] == "CONFIRMED_ON_THIS_FORMULATION"]
            ok_conf &= len(cs) == 1 and cs[0]["epoch"] == o["confirmed"]["epoch"] and cs[0] is fs[-1]
            ok_conf &= o["confirmed"]["compat"] == "COMPATIBLE"  # an incompatible T cannot close before B
        else:
            ok_conf &= not any(s["end_category"] == "CONFIRMED_ON_THIS_FORMULATION" for s in fs)
    c["segments ordered by journal sequence; domains non-overlapping"] = ok_order and ok_dom
    c["epochs 1..n in publication order"] = ok_epoch
    c["at most one confirmation per scenario, on its last formulation, linked to its own epoch"] = ok_conf
    c["no tail-window birth"] = not any(o["window"] == "tail" for o in obs)
    c["each confirming minute is the first qualifying minute of its formulation's domain (amendment 1)"] = all(
        s.get("confirming_minute_first_qualifying") for o in obs if not o["linkage"] for s in o["segments"]
        if s["end_category"] == "CONFIRMED_ON_THIS_FORMULATION")
    return c


def reconcile(t: dict) -> dict:
    cat = t["categories"]
    armed = t["scenarios"] - cat.get("NEVER_ARMED", 0)
    conf = sum(v for k, v in cat.items() if k.startswith("CONFIRMED_ON_"))
    xt = sum(sum(v.values()) for v in t["confirmed_terminal_crosstab"].values())
    ends = sum(sum(v.values()) for v in t["formulation_ends__publications_not_independent_scenarios"].values())
    first = sum(t["first_formulation_fate"].values())
    return {
        "born = never armed + armed": t["scenarios"] == cat.get("NEVER_ARMED", 0) + armed,
        "armed = never confirmed + confirmed (original + revised + rearmed) + not reconstructable":
            armed == cat.get("ARMED_NEVER_CONFIRMED", 0) + conf + cat.get("NOT_RECONSTRUCTABLE", 0),
        "confirmed terminal cross-tab = confirmed": xt == conf,
        "formulation ends = formulations": ends == t["formulations"],
        "first-formulation fates = reconstructable armed scenarios": first == armed - cat.get("NOT_RECONSTRUCTABLE", 0),
        "category details sum to categories": all(sum(v.values()) == cat[k] for k, v in t["category_detail"].items()),
    }


def run(journal: list[dict], mk: Market, data_end: datetime) -> dict:
    obs = build(journal, mk, data_end)
    tabs = {w: tables(obs, w) for w in ("evaluation", "warmup")}
    rec = {w: reconcile(tabs[w]) for w in tabs}
    chk = checks(obs, journal)
    audits = Counter()
    for o in obs:
        for s in o["segments"]:
            for a in s["audit"]:
                audits[f"{o['window']}:{s['kind']}:{s['end_category']}:{a.split(':')[0]}"] += 1
        for a in (o["confirmed"] or {}).get("audit", []):
            audits[f"{o['window']}:CONFIRMED:{a.split(':')[0]}"] += 1
    res = {"tables": tabs, "reconciliation": rec, "checks": chk, "bar_audits": dict(sorted(audits.items())),
           "illustrations": illustrations(obs),
           "all_checks_pass": all(chk.values()) and all(all(v.values()) for v in rec.values())}
    return {"obs": obs, "res": res}


def illustrations(obs: list[dict]) -> dict:
    """First chronological occurrence (by birth, evaluation window) of each registered TYPE; never chosen by outcome."""
    xs = [o for o in obs if o["window"] == "evaluation" and not o["linkage"]]

    def first(pred):
        o = next((o for o in xs if pred(o)), None)
        return o["scenario_id"] if o else None

    kinds = lambda o: [s["transition"] for s in o["segments"]]  # noqa: E731
    return {
        "revision while armed (REVISE)": first(lambda o: "REVISE" in kinds(o)),
        "anchor loss -> WATCH gap -> REARM": first(lambda o: "REARM" in kinds(o)),
        "revised or rearmed formulation never confirmed": first(
            lambda o: o["confirmed"] is None and any(k in ("REVISE", "REARM") for k in kinds(o))),
        "destination before confirmation": first(lambda o: any(
            s["end_category"] in ("DESTINATION_BEFORE_CONFIRMATION", "DESTINATION_IN_OBSERVATION_GAP")
            for s in o["segments"])),
        "derived-incompatible formulation": first(lambda o: any(
            s.get("derived_trigger_destination") == "INCOMPATIBLE" for s in o["segments"])),
    }


# ----------------------------------------------------------------------------------------------------------------------
# outputs
# ----------------------------------------------------------------------------------------------------------------------

def public(s: dict) -> dict:
    return {k: v for k, v in s.items() if not k.startswith("_")}


def scenarios_csv(obs: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["window", "scenario_id", "direction", "born_at", "born_cursor", "category", "detail", "path",
                "formulations", "revise", "rearm", "anchor_losses", "first_published_at", "first_K", "first_V", "B",
                "first_T", "first_derived_trigger_destination", "first_end", "confirmed_epoch", "confirmed_transition",
                "confirmed_formulation_published_at", "confirmed_formulation_cursor", "confirmed_K", "confirmed_V",
                "confirmed_T", "confirming_minute", "confirmed_at", "confirmed_cursor", "confirmed_deadline",
                "terminal_phase", "terminal_class", "terminal_reason", "terminal_at", "child_final", "calls",
                "bar_audit_notes", "linkage"])
    for o in obs:
        fs = [s for s in o["segments"] if s["kind"] == "FORMULATION"]
        f0 = fs[0] if fs else {}
        c = o["confirmed"] or {}
        cf = next((s for s in fs if s["epoch"] == c.get("epoch")), {}) if c else {}
        path = ">".join((f"{s['transition']}{s['epoch']}" if s["kind"] == "FORMULATION" else "WATCH")
                        + f"[{s['end_category']}]" for s in o["segments"])
        term = o["terminal"] or {}
        notes = sum(len(s["audit"]) for s in o["segments"]) + len(c.get("audit", []))
        w.writerow([o["window"], o["scenario_id"], o["direction"], o["born_at"], o["born_cursor"], o["category"],
                    o["detail"], path, len(fs), sum(s["transition"] == "REVISE" for s in fs),
                    sum(s["transition"] == "REARM" for s in fs),
                    sum(s["kind"] == "OBSERVATION_GAP" for s in o["segments"]), f0.get("published_at"), f0.get("K"),
                    f0.get("V"), f0.get("B"), f0.get("T"), f0.get("derived_trigger_destination"), f0.get("end_category"),
                    c.get("epoch"), c.get("transition"), cf.get("published_at"), cf.get("published_cursor"),
                    cf.get("K"), cf.get("V"), cf.get("T"), c.get("minute"), c.get("confirmed_at"),
                    c.get("confirmed_cursor"), c.get("confirmed_deadline"), term.get("phase", "OPEN"),
                    term.get("class", "OPEN_AT_DATA_END"), term.get("reason"), term.get("at"),
                    o["child"]["final"], " ".join(o["calls"]), notes, o["linkage"]])
    return buf.getvalue()


def formulations_csv(obs: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = ["window", "scenario_id", "direction", "order", "kind", "transition", "epoch", "observed_from", "observed_to",
            "published_at", "published_cursor", "published_seq", "K", "R", "V", "B", "T",
            "derived_trigger_destination", "premise", "original_expiry", "end_category", "end_detail", "ended_at",
            "ended_cursor", "ended_seq", "bar_audit"]
    w.writerow(cols)
    for o in obs:
        for i, s in enumerate(o["segments"], 1):
            p = public(s)
            w.writerow([o["window"], o["scenario_id"], o["direction"], i, p.get("kind"), p.get("transition"),
                        p.get("epoch"), p.get("observed_from"), p.get("observed_to"), p.get("published_at"),
                        p.get("published_cursor"), p.get("seq"), p.get("K"), p.get("R"), p.get("V"), p.get("B"),
                        p.get("T"), p.get("derived_trigger_destination"), p.get("premise"), p.get("original_expiry"),
                        p.get("end_category"), p.get("end_detail"), p.get("ended_at"), p.get("ended_cursor"),
                        p.get("ended_seq"), " ".join(p.get("audit") or [])])
    return buf.getvalue()


def sequences_json(obs: list[dict]) -> str:
    out = []
    for o in obs:
        x = {k: v for k, v in o.items() if k not in ("segments", "confirmed")}
        x["segments"] = [public(s) for s in o["segments"]]
        x["confirmed"] = public(o["confirmed"]) if o["confirmed"] else None
        out.append(x)
    return json.dumps(out, indent=1, sort_keys=True) + "\n"


def load_market(path: Path) -> Market:
    bars: dict[datetime, Bar | None] = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s = dt(row["start"])
            bars[s] = None if row["kind"] != "bar" else Bar(s, dt(row["end"]), Decimal(row["open"]),
                                                          Decimal(row["high"]), Decimal(row["low"]),
                                                          Decimal(row["close"]))
    return Market(bars)


def main_run(run_dir: Path, out: Path) -> None:
    with gzip.open(run_dir / "journal.jsonl.gz", "rt", encoding="utf-8") as f:
        journal = [json.loads(x) for x in f]
    mk = load_market(run_dir / "trade_bars.csv.gz")
    data_end = max(b for b in mk.m1) + MIN
    got = run(journal, mk, data_end)
    out.mkdir(parents=True, exist_ok=True)
    files = {"results.json": json.dumps(got["res"], indent=1, sort_keys=True) + "\n",
             "scenarios.csv": scenarios_csv(got["obs"]),
             "formulations.csv": formulations_csv(got["obs"]),
             "sequences.json": sequences_json(got["obs"])}
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
        print(name, hashlib.sha256(text.encode()).hexdigest())
    print("ALL CHECKS PASS" if got["res"]["all_checks_pass"] else "CHECK FAILURE")


# ----------------------------------------------------------------------------------------------------------------------
# synthetic discriminating cases (hand-built journal fragments and bars; no engine)
# ----------------------------------------------------------------------------------------------------------------------

def selftest() -> dict:
    results: dict[str, bool] = {}

    def check(name: str, cond: bool) -> None:
        results[name] = bool(cond)

    T0 = dt("2025-09-02T10:00:00Z")

    def market(d: int, spec: dict[int, tuple] | None = None, base: str = "1000") -> Market:
        """Flat 1m bars around ``base`` from T0-60m to T0+300m; ``spec`` overrides minute offsets (o,h,l,c) given
        in q-domain distances from base (direction-mirrored for SHORT)."""
        b0, bars = Decimal(base), {}
        for i in range(-60, 300):
            s = T0 + i * MIN
            o, h, lo, c = (spec or {}).get(i, (0, 1, -1, 0))
            vals = [b0 + Decimal(str(x)) * d for x in (o, h, lo, c)]
            hi, low = max(vals[1], vals[2]), min(vals[1], vals[2])
            bars[s] = Bar(s, s + MIN, vals[0], hi, low, vals[3])
        return Market(bars)

    seq = [100]

    def ent(t: datetime, tr: str, d: int, **r) -> dict:
        seq[0] += 1
        rec = {"scenario_id": "S", "family": "A", "direction": "LONG" if d > 0 else "SHORT", "transition": tr,
               "status": r.pop("status", "ARMED"), "setup": {"zone_halfwidth": "1"}}
        rec.update(r)
        return {"seq": seq[0], "clock_time": zs(t), "factual_cursor": seq[0] * 10, "kind": "scenario",
                "record_id": f"r{seq[0]}", "record": rec}

    def born(t: datetime, d: int) -> dict:
        e = ent(t, "BIRTH", d, status="WATCH")
        e["seq"] = 0  # the birth precedes every other record of the synthetic scenario
        return e

    def pub(t: datetime, tr: str, d: int, mk: Market, epoch: int, B: str, prev: dict | None = None,
            src_off: int = -15) -> dict:
        """A publication whose levels are read from its source 15m bar (as v0.6 does)."""
        s = T0 + src_off * MIN
        sb = mk.m15[s]
        K, R = (sb.h, sb.lo) if d > 0 else (sb.lo, sb.h)
        V = R - Decimal(1) * d
        T = K + TICK * d
        op, vop = (">=", "low >") if d > 0 else ("<=", "high <")
        e = ent(t, tr, d, trigger_level=str(K), reaction_level=str(R), invalidation_level=str(V), destination=B,
                anchor_source=f"x/15m/{s.isoformat()}", anchor_epoch=epoch, anchor_status="ACTIVE",
                antecedent=f"a later eligible complete 1m close {op} {T} with {vop} {V} confirms",
                previous_anchor=prev)
        e["record"]["anchor_published_at"], e["record"]["anchor_published_cursor"] = e["clock_time"], e["factual_cursor"]
        return e

    def conf(t: datetime, d: int, minute: datetime, mk: Market, f: dict, epoch: int) -> dict:
        r = f["record"]
        return ent(t, "CONFIRM", d, status="CONFIRMED", anchor_epoch=epoch, reason=f"x#obs@{zs(minute)}",
                   confirmation_close=str(mk.m1[minute].c), trigger_level=r["trigger_level"],
                   invalidation_level=r["invalidation_level"], destination=r["destination"],
                   confirmed_deadline=zs(t + timedelta(hours=4)))

    def term(t: datetime, d: int, state: str, reason: str) -> dict:
        return ent(t, "TERMINAL", d, status="TERMINAL", terminal_state=state, reason=reason)

    def lost(t: datetime, d: int, f: dict, minute: datetime, status: str = "INVALIDATED") -> dict:
        return ent(t, "ANCHOR_LOST", d, status="WATCH", anchor_status=status,
                   reason=f"{'V_CONTACT' if status == 'INVALIDATED' else 'ANCHOR_CONTACT_TIME_AMBIGUOUS'}:x#obs@{zs(minute)}",
                   previous_anchor={"epoch": str(f["record"]["anchor_epoch"]), "status": status,
                                    "interval": f"x#obs@{zs(minute)}"})

    end = T0 + 300 * MIN
    for d in (1, -1):
        tag = "LONG" if d > 0 else "SHORT"
        # 1. REVISE before confirmation; the confirmation belongs to the revised formulation only
        mk = market(d, {1: (0, 5, -1, 4), 14: (0, 1, -1.5, -1), 20: (0, 6, -1, 5.5)})
        birth = born(T0 - 30 * MIN, d)
        a = pub(T0, "ARM", d, mk, 1, str(Decimal(1000) + 50 * d), src_off=-15)
        rv = pub(T0 + 15 * MIN, "REVISE", d, mk, 2, str(Decimal(1000) + 50 * d),
                 prev={"epoch": "1", "status": "SUPERSEDED", "reason": "LOWER_CLEAN_REACTION_REANCHOR"}, src_off=0)
        ok_min = T0 + 20 * MIN
        cf = conf(T0 + 21 * MIN, d, ok_min, mk, rv, 2)
        o = chain([birth, a, rv, cf, term(T0 + 60 * MIN, d, "TIME_EXPIRED", "CONFIRMED_HARD_DEADLINE")], mk, end)
        check(f"{tag} REVISE: first formulation superseded, confirmation on the revised one",
              o["category"] == "CONFIRMED_ON_REVISED_FORMULATION" and o["segments"][0]["end_category"]
              == "SUPERSEDED_BY_REVISION" and o["confirmed"]["epoch"] == 2)
        check(f"{tag} REVISE: the earlier qualifying minute 1 is an audit note of formulation 1, never its confirmation",
              any(n.startswith("UNRECORDED_QUALIFYING_MINUTE") for n in o["segments"][0]["audit"]))
        # 2. ANCHOR_LOST -> WATCH -> REARM, confirmation on the rearmed formulation, then V after confirmation
        mk = market(d, {5: (0, 1, -9, -8), 14: (0, 1, -12, -11), 20: (0, 2, -5, 2), 40: (0, 1, -20, -19)})
        a = pub(T0, "ARM", d, mk, 1, str(Decimal(1000) + 50 * d), src_off=-15)
        ls = lost(T0 + 6 * MIN, d, a, T0 + 5 * MIN)
        ra = pub(T0 + 15 * MIN, "REARM", d, mk, 2, str(Decimal(1000) + 50 * d),
                 prev={"epoch": "1", "status": "INVALIDATED", "reason": "V_CONTACT"}, src_off=0)
        cf = conf(T0 + 21 * MIN, d, T0 + 20 * MIN, mk, ra, 2)
        o = chain([born(T0 - 30 * MIN, d), a, ls, ra, cf,
                   term(T0 + 41 * MIN, d, "INVALIDATED", f"V_CONTACT:x#obs@{zs(T0 + 40 * MIN)}")], mk, end)
        check(f"{tag} LOST->WATCH->REARM: gap ends REARM, confirmation on the rearmed formulation, V after confirmation",
              o["category"] == "CONFIRMED_ON_REARMED_FORMULATION" and [s["end_category"] for s in o["segments"]]
              == ["ANCHOR_LOST_CERTIFIED", "REARM", "CONFIRMED_ON_THIS_FORMULATION"]
              and o["terminal"]["class"] == "V_CONTACT" and o["detail"] == "V_CONTACT")
        # 3. destination before confirmation: while armed, and in an observation gap
        mk = market(d, {7: (0, 60, -1, 0)})
        a = pub(T0, "ARM", d, mk, 1, str(Decimal(1000) + 50 * d), src_off=-15)
        o = chain([born(T0 - 30 * MIN, d), a,
                   term(T0 + 8 * MIN, d, "DESTINATION_REACHED", f"DESTINATION_CONTACT:x#obs@{zs(T0 + 7 * MIN)}")],
                  mk, end)
        check(f"{tag} destination while armed = destination before confirmation (never a continuation)",
              o["category"] == "ARMED_NEVER_CONFIRMED" and o["detail"] == "DESTINATION_BEFORE_CONFIRMATION"
              and o["confirmed"] is None)
        mk = market(d, {5: (0, 1, -9, -8), 9: (0, 60, -1, 0)})
        a = pub(T0, "ARM", d, mk, 1, str(Decimal(1000) + 50 * d), src_off=-15)
        o = chain([born(T0 - 30 * MIN, d), a, lost(T0 + 6 * MIN, d, a, T0 + 5 * MIN),
                   term(T0 + 10 * MIN, d, "DESTINATION_REACHED", f"DESTINATION_CONTACT:x#obs@{zs(T0 + 9 * MIN)}")],
                  mk, end)
        check(f"{tag} destination in the WATCH gap is separate from a destination while armed",
              o["detail"] == "DESTINATION_IN_OBSERVATION_GAP")
        # 4. publication and contact in the same dispatch
        mk = market(d, {14: (0, 1, -12, -11)})
        a = pub(T0, "ARM", d, mk, 1, str(Decimal(1000) + 50 * d), src_off=-15)
        ls = lost(T0 + 15 * MIN, d, a, T0 + 14 * MIN)
        ra = pub(T0 + 15 * MIN, "REARM", d, mk, 2, str(Decimal(1000) + 50 * d),
                 prev={"epoch": "1", "status": "INVALIDATED", "reason": "V_CONTACT"}, src_off=0)
        o = chain([born(T0 - 30 * MIN, d), a, ls, ra], mk, end)
        check(f"{tag} loss and REARM in one dispatch: journal order decides, zero-length gap, nothing confirmed",
              [s["end_category"] for s in o["segments"]] == ["ANCHOR_LOST_CERTIFIED", "REARM", "OPEN_AT_DATA_END"]
              and o["segments"][1]["published_at"] == o["segments"][1]["ended_at"])
        bad = conf(T0 + 16 * MIN, d, T0 + 14 * MIN, mk, ra, 2)  # a minute of the source bar / before publication
        o = chain([born(T0 - 30 * MIN, d), a, ls, ra, bad], mk, end)
        check(f"{tag} a confirmation on a minute before the publication (source bar) is rejected as linkage",
              o["category"] == "NOT_RECONSTRUCTABLE" and "publication" in o["detail"])
        mk = market(d, {-1: (0, 1, -6, -5), 13: (0, 1, -6.5, -6), 14: (0, 5, -1, 4)})
        a = pub(T0, "ARM", d, mk, 1, str(Decimal(1000) + 50 * d), src_off=-15)
        rv = pub(T0 + 15 * MIN, "REVISE", d, mk, 2, str(Decimal(1000) + 50 * d),
                 prev={"epoch": "1", "status": "SUPERSEDED", "reason": "LOWER_CLEAN_REACTION_REANCHOR"}, src_off=0)
        o = chain([born(T0 - 30 * MIN, d), a, rv], mk, end)
        check(f"{tag} a minute qualifying for the old formulation in the superseding dispatch is reported, not credited",
              o["segments"][0]["audit"] == [f"QUALIFYING_MINUTE_IN_ENDING_DISPATCH:{zs(T0 + 14 * MIN)}"]
              and o["confirmed"] is None)
        # 5. ambiguous interval and insufficient linkage
        mk = market(d, {5: (0, 1, -9, -8)})
        a = pub(T0, "ARM", d, mk, 1, str(Decimal(1000) + 50 * d), src_off=-15)
        o = chain([born(T0 - 30 * MIN, d), a,
                   lost(T0 + 6 * MIN, d, a, T0 + 5 * MIN, status="UNASSESSABLE")], mk, end)
        check(f"{tag} an ambiguous anchor contact is its own end category", o["segments"][0]["end_category"]
              == "ANCHOR_LOST_AMBIGUOUS")
        o = chain([born(T0 - 30 * MIN, d), a,
                   ent(T0 + 3 * MIN, "CONFIRM", d, status="CONFIRMED", anchor_epoch=2, reason="x#obs@x")], mk, end)
        check(f"{tag} a confirmation not linked to the active epoch is NOT_RECONSTRUCTABLE, kept with its reason",
              o["category"] == "NOT_RECONSTRUCTABLE" and "does not link" in o["detail"])
        o = chain([born(T0 - 30 * MIN, d), a,
                   term(T0 + 8 * MIN, d, "DESTINATION_REACHED", f"DESTINATION_CONTACT:x#obs@{zs(T0 + 7 * MIN)}")],
                  mk, end)
        check(f"{tag} a destination contact its minute does not show is NOT_RECONSTRUCTABLE",
              o["category"] == "NOT_RECONSTRUCTABLE" and "not corroborated" in o["detail"])
        o = chain([born(T0 - 30 * MIN, d),
                   term(T0, d, "UNASSESSABLE", "FIRST_ARM_DESTINATION_CONTACT_TIME_AMBIGUOUS:x")], mk, end)
        check(f"{tag} terminal vocabulary: ambiguity is AMBIGUOUS", o["detail"] == "AMBIGUOUS"
              and o["category"] == "NEVER_ARMED")
        # 6. trigger/destination compatibility including the tick
        mk = market(d)
        sb = mk.m15[T0 - 15 * MIN]
        K = sb.h if d > 0 else sb.lo
        for off, want in ((Decimal("0.1"), "INCOMPATIBLE"), (Decimal("0.2"), "COMPATIBLE"), (Decimal(0), "INCOMPATIBLE"),
                          (Decimal("-0.5"), "INCOMPATIBLE")):
            a = pub(T0, "ARM", d, mk, 1, str(K + off * d), src_off=-15)
            f = formulation(a, mk, d, 1)
            check(f"{tag} B = K {'+' if d > 0 else '-'} {off}: {want}", f["derived_trigger_destination"] == want)
    # 7. the whole tabulation path on a two-scenario synthetic journal (rearmed confirmation + never armed)
    d = 1
    mk = market(d, {5: (0, 1, -9, -8), 14: (0, 1, -12, -11), 20: (0, 2, -5, 2), 40: (0, 1, -20, -19)})
    a = pub(T0, "ARM", d, mk, 1, "1050", src_off=-15)
    ls = lost(T0 + 6 * MIN, d, a, T0 + 5 * MIN)
    ra = pub(T0 + 15 * MIN, "REARM", d, mk, 2, "1050",
             prev={"epoch": "1", "status": "INVALIDATED", "reason": "V_CONTACT"}, src_off=0)
    s1 = [born(T0 - 30 * MIN, d), a, ls, ra, conf(T0 + 21 * MIN, d, T0 + 20 * MIN, mk, ra, 2),
          term(T0 + 41 * MIN, d, "INVALIDATED", f"V_CONTACT:x#obs@{zs(T0 + 40 * MIN)}")]
    s2 = [born(T0 - 15 * MIN, d), term(T0 + 15 * MIN, d, "EXPIRED", "SPENT_HIGH_BEYOND_B_BEFORE_REACTION")]
    journal, n = [], 0
    for sid, es in (("S1", s1), ("S2", s2)):
        for e in sorted(es, key=lambda e: e["seq"]):
            n += 1
            journal.append({**e, "seq": n, "record_id": f"{sid}-{n}", "record": {**e["record"], "scenario_id": sid}})
    journal.append({"seq": n + 1, "kind": "entry_attempt", "record_id": "c1", "clock_time": zs(T0 + 41 * MIN),
                    "factual_cursor": 0, "record": {"family": "A", "scenario_id": "S1", "transition": "TERMINAL",
                                                    "state": "TERMINAL", "reason": "SCENARIO_TERMINAL:INVALIDATED"}})
    got = run(journal, mk, end)
    ev = got["res"]["tables"]["evaluation"]
    check("tabulation: categories, cross-tab and reconciliations on a synthetic journal",
          ev["categories"] == {"CONFIRMED_ON_REARMED_FORMULATION": 1, "NEVER_ARMED": 1}
          and ev["confirmed_terminal_crosstab"] == {"revised_or_rearmed": {"V_CONTACT": 1}}
          and got["res"]["all_checks_pass"] and ev["formulations"] == 2 and ev["observation_gaps"] == 1
          and ev["first_formulation_fate"] == {
              "first formulation ANCHOR_LOST_CERTIFIED -> later confirmation on another formulation": 1})
    rows = scenarios_csv(got["obs"]).splitlines()
    check("tabulation: one summary row per scenario linked to its full formulation sequence",
          len(rows) == 3 and len(formulations_csv(got["obs"]).splitlines()) == 4
          and "ARM1[ANCHOR_LOST_CERTIFIED]>WATCH[REARM]>REARM2[CONFIRMED_ON_THIS_FORMULATION]" in rows[1]
          and json.loads(sequences_json(got["obs"]))[0]["segments"][2]["epoch"] == 2)
    out = {"cases": results, "passed": sum(results.values()), "total": len(results)}
    return out


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        r = selftest()
        for k, v in r["cases"].items():
            print(("ok   " if v else "FAIL ") + k)
        print(f"{r['passed']}/{r['total']}")
        (Path(__file__).resolve().parent / "selftest.json").write_text(json.dumps(r, indent=1) + "\n",
                                                                      encoding="utf-8", newline="\n")
        sys.exit(0 if r["passed"] == r["total"] else 1)
    elif sys.argv[1] == "run":
        main_run(Path(sys.argv[2]), Path(sys.argv[3]))
