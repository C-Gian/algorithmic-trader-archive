"""Historical check of the v0.6 A/B/C conditional expectations, September-December 2025 (descriptive; DESIGN.md).

Reads only existing artifacts: the v0.6 journal and the admitted trade 1m bars of the 12 October offline processing
(no engine run, no replay). For every scenario: one observation at its FIRST published ARM (the first complete
conditional thesis: trigger, invalidation, destination, premise and original expiry all published), the promise as
published at that record, the scenario's MarketView role at that dispatch, its later revisions, the outcome under the
ORIGINAL promise within the scenario's actual life, and the engine lifecycle terminal. Calls are linked only to tell
expectation from proposal. No economic quantity, no call outcome.

Promise (q = d * price; d = +1 LONG, -1 SHORT; tick = pack tick * trigger_ticks):
  antecedent: a complete 1m bar starting >= cutoff, available < original expiry H, close_q >= K0_q + tick;
  invalidation: 1m low_q <= V0_q (before or after activation); premise: complete 15m close_q < P_q (published
  "15m close beyond P"); destination: 1m high_q >= B_q; after activation the life is the family's registered hard
  horizon from the activation publication (A 4h, B 6h, C 2h; the rule known at the cutoff, not a later reference).
Dispatch order at each minute end t (engine order): timer (t >= H before activation, t >= D after) -> 1m contacts of
the bar ending at t (V and B in one bar = AMBIGUOUS) -> 15m premise of the bar ending at t -> activation (pre only).
Life bound: an engine terminal earlier than the resolution (or at the same dispatch with an earlier rank, or the same
rank and a different kind) ends the promise as SCENARIO_ENDED (no later contact recovers a success).

  .venv/Scripts/python.exe delivery/evidence/V06-EXPECTATION-HISTORICAL-CHECK/expectations.py <run_dir> <out_dir>
  .venv/Scripts/python.exe delivery/evidence/V06-EXPECTATION-HISTORICAL-CHECK/expectations.py --selftest
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WINDOW = ("2025-09-01T00:00:00Z", "2026-01-01T00:00:00Z")
HARD = {"A": timedelta(hours=4), "B": timedelta(hours=6), "C": timedelta(hours=2)}  # v0.6 register (checked)
TICK = Decimal("0.1")  # pack tick_sz x trigger_ticks 1 (checked against the antecedent text)
MIN = timedelta(minutes=1)
Q15 = timedelta(minutes=15)
CODE_SEG = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
NUM = re.compile(r"-?\d+(?:\.\d+)?")
ANTE = re.compile(r"close [<>]= (-?\d+(?:\.\d+)?) with (?:low >|high <) (-?\d+(?:\.\d+)?)")


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def zs(t: datetime | None) -> str | None:
    return None if t is None else t.isoformat().replace("+00:00", "Z")


def code(reason: str | None) -> str | None:
    if reason is None:
        return None
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
    avail: datetime
    o: Decimal
    h: Decimal
    lo: Decimal
    c: Decimal


class Market:
    """Admitted trade 1m bars (gaps as None) and the complete UTC 15m bars derived from them."""

    def __init__(self, bars: dict[datetime, Bar | None]) -> None:
        self.m1 = bars
        self.first = min(bars)
        self.last_end = max(bars) + MIN
        self.m15: dict[datetime, Bar] = {}
        q = self.first
        while q + Q15 <= self.last_end:
            ms = [bars.get(q + i * MIN) for i in range(15)]
            if all(m is not None for m in ms):
                self.m15[q + Q15] = Bar(q, q + Q15, max(m.avail for m in ms), ms[0].o, max(m.h for m in ms),
                                        min(m.lo for m in ms), ms[-1].c)
            q += Q15


def tq(b: Bar, d: int) -> tuple[Decimal, Decimal, Decimal]:
    """(high_q, low_q, close_q) in the direction-transformed domain."""
    return (b.h, b.lo, b.c) if d > 0 else (-b.lo, -b.h, -b.c)


# ----------------------------------------------------------------------------------------------------------------------
# the original promise
# ----------------------------------------------------------------------------------------------------------------------

RANK_TIMER, RANK_1M, RANK_15M = 0, 1, 2


def classify(mk: Market, d: int, family: str, cutoff: datetime, K0: Decimal, V0: Decimal, B: Decimal, P: Decimal,
             H: datetime) -> dict:
    """Outcome of the original promise from the market alone (before the life bound)."""
    k, v, b, p = d * K0 + TICK, d * V0, d * B, d * P
    act = None
    deadline = None
    t = cutoff + MIN
    while True:
        if t > mk.last_end:
            return {"category": "INSUFFICIENT_DATA", "detail": "CENSORED_AT_DATA_END", "t": zs(mk.last_end),
                    "rank": None, "activated_at": zs(act), "kind": None}
        phase_end = H if act is None else deadline
        if t >= phase_end:
            if act is None:
                return {"category": "ANTECEDENT_NEVER_ACTIVATED", "detail": "ORIGINAL_EXPIRY", "t": zs(phase_end),
                        "rank": RANK_TIMER, "activated_at": None, "kind": "EXPIRY"}
            return {"category": "EXPIRED_WITHOUT_DESTINATION", "detail": "HARD_HORIZON_AFTER_ACTIVATION",
                    "t": zs(phase_end), "rank": RANK_TIMER, "activated_at": zs(act), "kind": "TIME"}
        m = mk.m1.get(t - MIN)
        if m is None:
            return {"category": "INSUFFICIENT_DATA", "detail": "MISSING_TRADE_MINUTE", "t": zs(t), "rank": None,
                    "activated_at": zs(act), "kind": None}
        hq, lq, cq = tq(m, d)
        hv, hb = lq <= v, hq >= b
        pre = act is None
        if hv and hb:
            return {"category": "AMBIGUOUS", "detail": "V_AND_DESTINATION_SAME_MINUTE" + ("_BEFORE_ACTIVATION" if pre else ""),
                    "t": zs(t), "rank": RANK_1M, "activated_at": zs(act), "kind": "AMBIGUOUS"}
        if hv:
            if pre:
                return {"category": "ANTECEDENT_NEVER_ACTIVATED", "detail": "ORIGINAL_INVALIDATION_CONTACT",
                        "t": zs(t), "rank": RANK_1M, "activated_at": None, "kind": "V"}
            return {"category": "INVALIDATED", "detail": "V_CONTACT", "t": zs(t), "rank": RANK_1M,
                    "activated_at": zs(act), "kind": "V"}
        if hb:
            if pre:
                return {"category": "ANTECEDENT_NEVER_ACTIVATED", "detail": "DESTINATION_BEFORE_ACTIVATION",
                        "t": zs(t), "rank": RANK_1M, "activated_at": None, "kind": "DEST"}
            return {"category": "DESTINATION_REACHED", "detail": "DESTINATION_CONTACT", "t": zs(t), "rank": RANK_1M,
                    "activated_at": zs(act), "kind": "DEST"}
        q = mk.m15.get(t)
        if q is not None and q.end > (cutoff if pre else act) and tq(q, d)[2] < p:
            if pre:
                return {"category": "ANTECEDENT_NEVER_ACTIVATED", "detail": "PREMISE_15M_CLOSE_BEYOND", "t": zs(t),
                        "rank": RANK_15M, "activated_at": None, "kind": "PREMISE"}
            return {"category": "INVALIDATED", "detail": "PREMISE_15M_CLOSE_BEYOND", "t": zs(t), "rank": RANK_15M,
                    "activated_at": zs(act), "kind": "PREMISE"}
        if pre and cq >= k:
            act = t
            deadline = t + HARD[family]
        t += MIN


ENGINE_KIND = {"INVALIDATED:V_CONTACT": "V", "DESTINATION_REACHED:DESTINATION_CONTACT": "DEST",
               "PRICE_PREMISE_FAILED:15M_CLOSE_BEYOND_PREMISE": "PREMISE",
               "PRICE_PREMISE_FAILED:15M_CLOSE_BEYOND_U_MINUS_Z": "PREMISE",
               "WITHDRAWN:RETURNED_INSIDE_BEFORE_RETEST": "PREMISE",
               "WITHDRAWN:CLOSE_BEYOND_LOWER_FAR_EDGE_BEFORE_TRIGGER": "PREMISE",
               "EXPIRED:ORIGINAL_SETUP_DEADLINE": "EXPIRY", "TIME_EXPIRED:CONFIRMED_HARD_DEADLINE": "TIME",
               "UNASSESSABLE:DESTINATION_AND_INVALIDATION_SAME_INTERVAL": "AMBIGUOUS",
               "UNASSESSABLE:DESTINATION_AND_LOCAL_ANCHOR_CONTACT_SAME_INTERVAL": "AMBIGUOUS"}


def engine_rank(term: str) -> int:
    """Dispatch position of an engine terminal: timers/staleness first, then 1m intervals (contacts, progress), then
    15m closes and gates (withdrawals, premise, spend)."""
    if term.startswith(("EXPIRED:ORIGINAL_SETUP_DEADLINE", "TIME_EXPIRED", "UNASSESSABLE:REQUIRED",
                        "EXPIRED:BOX_RETIRED:BOX_EXPIRY")):
        return RANK_TIMER
    if term.startswith(("INVALIDATED", "DESTINATION_REACHED", "STALLED", "UNASSESSABLE")):
        return RANK_1M
    return RANK_15M


def bound(res: dict, term: str | None, term_t: str | None) -> dict:
    """Apply the scenario's actual life: an engine terminal first ends the promise (SCENARIO_ENDED)."""
    if term is None or res["t"] is None:
        return res
    if res["category"] == "INSUFFICIENT_DATA" and term_t <= res["t"]:
        pass
    elif term_t > res["t"]:
        return res
    elif term_t == res["t"] and res["rank"] is not None:
        er = engine_rank(term)
        if er > res["rank"] or (er == res["rank"] and ENGINE_KIND.get(term) == res["kind"]):
            return res
    # amendment 3: an activation at or after the scenario's end never happened within its life (an engine terminal
    # at the activation dispatch precedes it: terminals are processed before confirmations)
    pre = res["activated_at"] is None or res["activated_at"] >= term_t
    return {"category": "ANTECEDENT_NEVER_ACTIVATED" if pre else "SCENARIO_ENDED_AFTER_ACTIVATION",
            "detail": f"SCENARIO_ENDED:{term}", "t": term_t, "rank": engine_rank(term),
            "activated_at": None if pre else res["activated_at"], "kind": "ENGINE",
            "unbounded": res["category"] + ":" + res["detail"]}


# ----------------------------------------------------------------------------------------------------------------------
# journal -> observations
# ----------------------------------------------------------------------------------------------------------------------

def observe(journal: list[dict], mk: Market) -> list[dict]:
    scen: dict[str, list[dict]] = defaultdict(list)
    views: list[tuple[str, dict]] = []
    calls: dict[str, list[dict]] = defaultdict(list)
    for e in journal:
        r = e["record"]
        if e["kind"] == "scenario":
            scen[r["scenario_id"]].append(r)
        elif e["kind"] == "market_view":
            views.append((r["env"]["clock_time"], r))
        elif e["kind"] == "call":
            calls[r["scenario_id"]].append(r)
    vtimes = [t for t, _ in views]
    out = []
    import bisect
    for sid, recs in scen.items():
        r0 = recs[0]
        fam, d = r0["family"], 1 if r0["direction"] == "LONG" else -1
        born = r0["env"]["clock_time"]
        last = recs[-1]
        term = f"{last['terminal_state']}:{code(last['reason'])}" if last["status"] == "TERMINAL" else None
        term_t = last["env"]["clock_time"] if term else None
        obs = {"scenario_id": sid, "family": fam, "direction": r0["direction"], "born_at": born,
               "window": window_of(born), "first_record": r0["transition"], "engine_terminal": term or "OPEN_AT_DATA_END",
               "engine_terminal_at": term_t, "engine_confirmed": any(r["transition"] == "CONFIRM" for r in recs),
               "calls": len(calls.get(sid, [])), "call_ids": [c["call_id"] for c in calls.get(sid, [])]}
        arm = next((r for r in recs if r["transition"] == "ARM"), None)
        if arm is None:
            obs.update(published=False, hypothesis_end=term or "OPEN_AT_DATA_END")
            out.append(obs)
            continue
        c = arm["env"]["clock_time"]
        obs["published"] = True
        obs["cutoff"] = c
        prem = arm["premise"]
        pnum = NUM.findall(prem or "")
        promise = {"antecedent": arm["antecedent"], "trigger_level": arm["trigger_level"],
                   "invalidation_level": arm["invalidation_level"], "destination": arm["destination"],
                   "destination_type": arm["destination_type"], "premise": prem,
                   "premise_level": pnum[-1] if pnum else None, "original_expiry": arm["original_expiry"],
                   "s15": arm["setup"].get("s15")}
        obs["promise"] = promise
        # MarketView role at the cutoff dispatch (the latest view at or before it)
        i = bisect.bisect_right(vtimes, c) - 1
        v = views[i][1] if i >= 0 else None
        role = "NO_VIEW"
        if v is not None:
            if (v["principal"] or {}).get("scenario_id") == sid:
                role = "PRINCIPAL"
            elif any(a["scenario_id"] == sid for a in v["alternatives"]):
                role = "ALTERNATIVE"
            elif any(a["scenario_id"] == sid for a in v["watch"]):
                role = "WATCH"
            else:
                role = "ABSENT"
        obs["view"] = {"role": role, "view_at": v["env"]["clock_time"] if v else None,
                       "table_row": v["table_row"] if v else None, "expected_direction": v["expected_direction"] if v else None}
        missing = [k for k in ("trigger_level", "invalidation_level", "destination", "premise_level", "original_expiry")
                   if promise[k] is None]
        # revisions after the cutoff (the original promise stays as recorded at the cutoff)
        revs = [{"t": r["env"]["clock_time"], "transition": r["transition"], "reason": code(r["reason"]),
                 "K": r["trigger_level"], "V": r["invalidation_level"], "expiry": r["original_expiry"],
                 "destination": r["destination"]}
                for r in recs if r["env"]["clock_time"] >= c and r is not arm
                and r["transition"] in ("REVISE", "ANCHOR_LOST", "REARM")]
        conf = next((r for r in recs if r["transition"] == "CONFIRM"), None)
        obs["revisions"] = revs
        obs["engine_confirmation"] = None if conf is None else {
            "t": conf["env"]["clock_time"], "K": conf["trigger_level"], "V": conf["invalidation_level"],
            "confirmed_deadline": conf["confirmed_deadline"], "destination": conf["destination"]}
        if missing:
            obs["original"] = {"category": "NOT_EVALUABLE", "detail": "MISSING:" + ",".join(missing), "t": None}
            out.append(obs)
            continue
        thr = ANTE.search(arm["antecedent"])  # amendment 2: the levels after the comparison signs ("1m" is not one)
        obs["antecedent_text_consistent"] = bool(thr) and Decimal(thr.group(1)) == Decimal(arm["trigger_level"]) \
            + d * TICK and Decimal(thr.group(2)) == Decimal(arm["invalidation_level"])
        res = classify(mk, d, fam, dt(c), Decimal(arm["trigger_level"]), Decimal(arm["invalidation_level"]),
                       Decimal(arm["destination"]), Decimal(promise["premise_level"]), dt(arm["original_expiry"]))
        obs["original_unbounded"] = dict(res)
        res = bound(res, term, term_t)
        obs["original"] = res
        rt = res["t"]
        obs["revised_before_resolution"] = bool(rt) and any(x["t"] < rt for x in revs)
        if conf is not None:
            same_levels = conf["trigger_level"] == arm["trigger_level"] and conf["invalidation_level"] == arm["invalidation_level"]
            same_time = res.get("activated_at") == conf["env"]["clock_time"]
            obs["engine_confirmation_vs_original"] = (
                "SAME_LEVELS_SAME_TIME" if same_levels and same_time else "SAME_LEVELS_OTHER_TIME" if same_levels
                else "REVISED_LEVELS")
            if same_levels and same_time:
                obs["deadline_rule_check"] = zs(dt(conf["env"]["clock_time"]) + HARD[fam]) == conf["confirmed_deadline"]
        out.append(obs)
    return sorted(out, key=lambda o: (o["born_at"], o["scenario_id"]))


# ----------------------------------------------------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------------------------------------------------

def tally(xs) -> dict:
    return dict(sorted(Counter(xs).items()))


def table(obs: list[dict], fam: str, window: str) -> dict:
    xs = [o for o in obs if o["family"] == fam and o["window"] == window]
    pub = [o for o in xs if o["published"]]
    ev = [o for o in pub if o["original"]["category"] != "NOT_EVALUABLE"]
    act = [o for o in ev if o["original"].get("activated_at")]
    out = {
        "unit": "scenario (one observation per scenario, at its first published ARM)",
        "hypotheses_born": len(xs),
        "never_published_as_expectation": len(xs) - len(pub),
        "never_published_by_end": tally(o["hypothesis_end"] for o in xs if not o["published"]),
        "published_expectations": len(pub),
        "view_role_at_cutoff": tally(o["view"]["role"] for o in pub),
        "view_row_when_absent": tally(o["view"]["table_row"] for o in pub if o["view"]["role"] in ("ABSENT", "NO_VIEW")),
        "not_evaluable": tally(o["original"]["detail"] for o in pub if o["original"]["category"] == "NOT_EVALUABLE"),
        "evaluable": len(ev),
        "original_antecedent_activated": len(act),
        "original_outcome": tally(o["original"]["category"] for o in ev),
        "original_outcome_detail": tally(f"{o['original']['category']}:{o['original']['detail']}" for o in ev),
        "revised_before_resolution": len([o for o in ev if o["revised_before_resolution"]]),
        "original_outcome_without_revision_before_resolution": tally(
            o["original"]["category"] for o in ev if not o["revised_before_resolution"]),
        "original_outcome_with_revision_before_resolution": tally(
            o["original"]["category"] for o in ev if o["revised_before_resolution"]),
        "revision_transitions_after_cutoff": tally(r["transition"] for o in pub for r in o["revisions"]),
        "engine_confirmed": len([o for o in pub if o["engine_confirmed"]]),
        "engine_confirmation_vs_original": tally(o.get("engine_confirmation_vs_original") for o in pub if o["engine_confirmed"]),
        "engine_lifecycle_terminal": tally(o["engine_terminal"] for o in pub),
        "lifecycle_destination_after_engine_confirmation_but_not_under_original": len([
            o for o in ev if o["engine_confirmed"] and o["engine_terminal"].startswith("DESTINATION_REACHED")
            and o["original"]["category"] != "DESTINATION_REACHED"]),
        "scenarios_with_a_call": len([o for o in pub if o["calls"]]),
        "calls": sum(o["calls"] for o in xs),
    }
    oo = out["original_outcome"]
    out["reconciliation"] = {
        "born = never_published + published": out["hypotheses_born"] == out["never_published_as_expectation"] + len(pub),
        "published = not_evaluable + evaluable": len(pub) == sum(out["not_evaluable"].values()) + len(ev),
        "evaluable = sum(original_outcome)": len(ev) == sum(oo.values()),
        "evaluable = without + with revision": len(ev) == sum(out["original_outcome_without_revision_before_resolution"].values())
        + sum(out["original_outcome_with_revision_before_resolution"].values()),
        "published = sum(view roles)": len(pub) == sum(out["view_role_at_cutoff"].values()),
        "activated >= post-activation outcomes": len(act) >= sum(oo.get(k, 0) for k in (
            "DESTINATION_REACHED", "EXPIRED_WITHOUT_DESTINATION", "SCENARIO_ENDED_AFTER_ACTIVATION")),
    }
    return out


def checks(obs: list[dict], journal: list[dict], mk: Market) -> dict:
    c = {}
    ids = [o["scenario_id"] for o in obs]
    c["one observation per scenario id"] = len(ids) == len(set(ids))
    c["every scenario's first record is BIRTH"] = all(o["first_record"] == "BIRTH" for o in obs)
    pub = [o for o in obs if o["published"]]
    c["every A cutoff = its destination-monitoring origin (first ARM)"] = all(
        next(r["record"]["destination_monitoring_from"] for r in journal if r["kind"] == "scenario"
             and r["record"]["scenario_id"] == o["scenario_id"] and r["record"]["transition"] == "ARM") == o["cutoff"]
        for o in pub if o["family"] == "A")
    c["antecedent text = trigger + tick and invalidation (every evaluable)"] = all(
        o.get("antecedent_text_consistent") for o in pub if o["original"]["category"] != "NOT_EVALUABLE")
    c["causality: resolution at or after the cutoff"] = all(
        o["original"]["t"] is None or o["original"]["t"] >= o["cutoff"] for o in pub)
    c["causality: activation after the cutoff and before the original expiry"] = all(
        o["original"].get("activated_at") is None or o["cutoff"] < o["original"]["activated_at"] < o["promise"]["original_expiry"]
        for o in pub if o["original"]["category"] != "NOT_EVALUABLE")
    c["causality (amendment 3): every activation precedes the resolution and the engine terminal"] = all(
        o["original"].get("activated_at") is None or (
            o["original"]["activated_at"] <= o["original"]["t"]
            and (o["engine_terminal_at"] is None or o["original"]["activated_at"] < o["engine_terminal_at"]))
        for o in pub if o["original"]["category"] != "NOT_EVALUABLE")
    chk = [o["deadline_rule_check"] for o in pub if "deadline_rule_check" in o]
    c["registered hard horizon = engine confirmed_deadline when activation = engine confirmation"] = all(chk) and bool(chk)
    c["coverage: no missing trade minute"] = all(v is not None for v in mk.m1.values())
    c["coverage: contiguous minutes from first to last"] = len(mk.m1) == int((mk.last_end - mk.first) / MIN)
    c["no birth in the tail"] = not [o for o in obs if o["window"] == "tail"]
    return c


def run(journal: list[dict], mk: Market) -> dict:
    obs = observe(journal, mk)
    res = {"window": WINDOW, "hard_horizons_minutes": {k: int(v / MIN) for k, v in HARD.items()}, "tick": str(TICK),
           "tables": {w: {f: table(obs, f, w) for f in "ABC"} for w in ("evaluation", "warmup")},
           "checks": checks(obs, journal, mk)}
    res["all_checks_pass"] = all(v is True for v in res["checks"].values()) and all(
        all(t["reconciliation"].values()) for w in res["tables"].values() for t in w.values())
    return {"res": res, "obs": obs}


def scenarios_csv(obs: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["window", "family", "direction", "scenario_id", "born_at", "published", "cutoff", "view_role",
                "view_row", "trigger_K0", "invalidation_V0", "destination", "destination_type", "premise_level",
                "original_expiry", "original_category", "original_detail", "original_t", "original_activated_at",
                "unbounded_original", "revisions", "revised_before_resolution", "engine_confirmation",
                "engine_confirmation_vs_original", "engine_terminal", "engine_terminal_at", "calls"])
    for o in obs:
        p = o.get("promise") or {}
        r = o.get("original") or {}
        u = o.get("original_unbounded") or {}
        w.writerow([o["window"], o["family"], o["direction"], o["scenario_id"], o["born_at"], o["published"],
                    o.get("cutoff", ""), (o.get("view") or {}).get("role", ""), (o.get("view") or {}).get("table_row", ""),
                    p.get("trigger_level", ""), p.get("invalidation_level", ""), p.get("destination", ""),
                    p.get("destination_type", ""), p.get("premise_level", ""), p.get("original_expiry", ""),
                    r.get("category", ""), r.get("detail", ""), r.get("t", ""), r.get("activated_at") or "",
                    f"{u.get('category', '')}:{u.get('detail', '')}" if u else "",
                    ";".join(f"{x['t']} {x['transition']} K={x['K']} V={x['V']}" for x in o.get("revisions", [])),
                    o.get("revised_before_resolution", ""),
                    json.dumps(o.get("engine_confirmation"), sort_keys=True) if o.get("engine_confirmation") else "",
                    o.get("engine_confirmation_vs_original", ""), o["engine_terminal"], o["engine_terminal_at"] or "",
                    o["calls"]])
    return buf.getvalue()


def load_market(path: Path) -> Market:
    bars: dict[datetime, Bar | None] = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            s = dt(row["start"])
            if row["kind"] != "bar":
                bars[s] = None
                continue
            bars[s] = Bar(s, dt(row["end"]), dt(row["available_time"]), Decimal(row["open"]), Decimal(row["high"]),
                          Decimal(row["low"]), Decimal(row["close"]))
    return Market(bars)


def main_run(run_dir: Path, out: Path) -> None:
    with gzip.open(run_dir / "journal.jsonl.gz", "rt", encoding="utf-8") as f:
        journal = [json.loads(x) for x in f]
    mk = load_market(run_dir / "trade_bars.csv.gz")
    got = run(journal, mk)
    out.mkdir(parents=True, exist_ok=True)
    files = {"results.json": json.dumps(got["res"], indent=1, sort_keys=True) + "\n",
             "scenarios.csv": scenarios_csv(got["obs"]),
             "observations.json": json.dumps(got["obs"], indent=1, sort_keys=True) + "\n"}
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
        print(name, hashlib.sha256(text.encode()).hexdigest())
    print("ALL CHECKS PASS" if got["res"]["all_checks_pass"] else "CHECK FAILURE")


# ----------------------------------------------------------------------------------------------------------------------
# self-test (hand-derived)
# ----------------------------------------------------------------------------------------------------------------------

def selftest() -> None:
    ok = []

    def check(name, cond):
        ok.append(bool(cond))
        print(("ok   " if cond else "FAIL ") + name)

    T0 = datetime(2025, 9, 1, 10, 0, tzinfo=dt("2025-01-01T00:00:00Z").tzinfo)

    def mk_from(path: list[tuple], start=T0 - timedelta(minutes=30), base=Decimal(1000), n_after=400, mirror=False):
        """Flat 1000 (o=h=l=c) before T0 and after the path; ``path`` = (o, h, l, c) minutes from T0."""
        bars = {}
        seq = [(base,) * 4] * 30 + [tuple(Decimal(str(x)) for x in p) for p in path] + [(Decimal(str(path[-1][3])),) * 4] * n_after
        for i, (o, h, lo, c) in enumerate(seq):
            s = start + i * MIN
            if mirror:
                o, h, lo, c = 2000 - o, 2000 - lo, 2000 - h, 2000 - c
            bars[s] = Bar(s, s + MIN, s + MIN, o, h, lo, c)
        return Market(bars)

    # LONG promise: K0 1010 (threshold 1010.1), V0 990, B 1050, premise 980, H = T0 + 60 min; cutoff T0
    def cls(path, fam="A", mirror=False, H=60, **kw):
        m = mk_from(path, mirror=mirror, **kw)
        d = -1 if mirror else 1
        f = (lambda x: Decimal(2000) - Decimal(x)) if mirror else Decimal
        return classify(m, d, fam, T0, f(1010), f(990), f(1050), f(980), T0 + timedelta(minutes=H))

    for mir in (False, True):
        s = "SHORT" if mir else "LONG"
        r = cls([(1000, 1005, 995, 1005)], mirror=mir)
        check(f"{s}: no activation within the original expiry -> ANTECEDENT_NEVER_ACTIVATED:ORIGINAL_EXPIRY at H",
              (r["category"], r["detail"], r["t"]) == ("ANTECEDENT_NEVER_ACTIVATED", "ORIGINAL_EXPIRY", zs(T0 + timedelta(minutes=60))))
        r = cls([(1000, 1011, 999, "1010.1"), (1010, 1051, 1009, 1040)], mirror=mir)
        check(f"{s}: activation at close K0+tick (10:01), destination at 10:02 -> DESTINATION_REACHED",
              (r["category"], r["activated_at"], r["t"]) == ("DESTINATION_REACHED", zs(T0 + MIN), zs(T0 + 2 * MIN)))
        r = cls([(1000, 1011, 999, "1010.0")], mirror=mir)
        check(f"{s}: close K0 exactly (below K0+tick) never activates", r["category"] == "ANTECEDENT_NEVER_ACTIVATED"
              and r["detail"] == "ORIGINAL_EXPIRY")
        r = cls([(1000, 1060, 1000, 1055)], mirror=mir)
        check(f"{s}: destination touched in the would-be activation minute -> DESTINATION_BEFORE_ACTIVATION (contacts first)",
              r["detail"] == "DESTINATION_BEFORE_ACTIVATION")
        r = cls([(1000, 1005, 989, 1000)], mirror=mir)
        check(f"{s}: V0 touched before activation -> ORIGINAL_INVALIDATION_CONTACT", r["detail"] == "ORIGINAL_INVALIDATION_CONTACT")
        r = cls([(1000, 1011, 999, 1011), (1011, 1060, 985, 1000)], mirror=mir)
        check(f"{s}: V and destination in one post-activation minute -> AMBIGUOUS", r["category"] == "AMBIGUOUS")
        r = cls([(1000, 1011, 999, 1011)], mirror=mir, fam="C")
        check(f"{s}: activated, flat, C hard horizon 2h -> EXPIRED_WITHOUT_DESTINATION at activation + 120 min",
              (r["category"], r["t"]) == ("EXPIRED_WITHOUT_DESTINATION", zs(T0 + MIN + timedelta(hours=2))))
        r = cls([(1000, 1011, 999, 1011)], mirror=mir, fam="C", n_after=60)
        check(f"{s}: data ends before the horizon -> INSUFFICIENT_DATA", r["category"] == "INSUFFICIENT_DATA")
        # premise: 15m bar [10:00,10:15) closing 979 (< 980) without touching V0 990? impossible (low <= close) -> use
        # a premise above V: re-run with premise 995 and V 990: close 994 at 10:15 with lows >= 991
        m = mk_from([(1000, 1000, 991, 994)] * 15, mirror=mir)
        d = -1 if mir else 1
        f = (lambda x: Decimal(2000) - Decimal(x)) if mir else Decimal
        r = classify(m, d, "A", T0, f(1010), f(990), f(1050), f(995), T0 + timedelta(minutes=60))
        check(f"{s}: complete 15m close beyond the premise at 10:15 -> PREMISE_15M_CLOSE_BEYOND (before activation)",
              (r["detail"], r["t"]) == ("PREMISE_15M_CLOSE_BEYOND", zs(T0 + Q15)))
        r = cls([(1000, 1005, 995, 1000)] * 59 + [(1000, 1011, 999, 1011)], mirror=mir)
        check(f"{s}: a recovery available exactly at H is preceded by the timer", r["detail"] == "ORIGINAL_EXPIRY")
    # life bound
    res = {"category": "DESTINATION_REACHED", "detail": "DESTINATION_CONTACT", "t": "2025-09-01T12:00:00Z", "rank": 1,
           "activated_at": "2025-09-01T11:00:00Z", "kind": "DEST"}
    check("life bound: an earlier engine terminal ends the promise (no later success recovered)",
          bound(res, "STALLED:SCENARIO_PROGRESS_BELOW_HALF_SCALE", "2025-09-01T11:30:00Z")["category"]
          == "SCENARIO_ENDED_AFTER_ACTIVATION")
    check("life bound: the same contact in the same dispatch stands",
          bound(res, "DESTINATION_REACHED:DESTINATION_CONTACT", "2025-09-01T12:00:00Z")["category"] == "DESTINATION_REACHED")
    check("life bound: a timer terminal in the same dispatch precedes a contact",
          bound(res, "TIME_EXPIRED:CONFIRMED_HARD_DEADLINE", "2025-09-01T12:00:00Z")["category"] == "SCENARIO_ENDED_AFTER_ACTIVATION")
    check("life bound: a 15m withdrawal in the same dispatch follows a contact",
          bound(res, "WITHDRAWN:CONTEXT_OR_ADVERSE_EXPANSION", "2025-09-01T12:00:00Z")["category"] == "DESTINATION_REACHED")
    check("life bound: a later engine terminal does not matter",
          bound(res, "INVALIDATED:V_CONTACT", "2025-09-01T12:30:00Z")["category"] == "DESTINATION_REACHED")
    b = bound(res, "WITHDRAWN:CONTEXT_OR_ADVERSE_EXPANSION", "2025-09-01T10:45:00Z")
    check("life bound (amendment 3): a scenario ended before the market activation -> never activated, no activation",
          (b["category"], b["activated_at"]) == ("ANTECEDENT_NEVER_ACTIVATED", None))

    # integration on the synthetic engine tape two_calls (tests/adviser_a2x_fixtures.py), hand-derived:
    # S1 ARM 03:45 K0 100700 V0 99800 B 100900; REVISE 04:00 (K 100049.9, V 99700); engine CONFIRM 04:01 (close 100050
    # < K0 + tick 100700.1: no original activation); REF/VALID lows 99990/99992; [04:03,04:04) low 99700 <= V0 -> the
    # original promise ends ORIGINAL_INVALIDATION_CONTACT at 04:04, revised before resolution; engine INVALIDATED 04:04
    sys.path.insert(0, str(ROOT / "tests"))
    sys.path.insert(0, str(ROOT / "src"))
    import adviser_a2x_fixtures as fx

    from algotrader.adviser.harness import run_pure
    ms = fx.two_calls()
    j = json.loads(json.dumps(run_pure(fx.DAY1, ms, method="v0.6", eval_start=fx.DAY2).journal, default=str))
    bars = {}
    for i, m in enumerate(ms):
        s = fx.DAY1 + i * MIN
        bars[s] = None if m.gap else Bar(s, s + MIN, s + MIN, m.o, m.h, m.lo, m.c)
    obs = observe(j, Market(bars))
    a = next(o for o in obs if o["family"] == "A" and o["born_at"].endswith("03:30:00Z"))
    check("two_calls: cutoff 03:45 (first ARM), promise K0 100700 / V0 99800 / B 100900 / premise 97000 / H 05:30",
          (a["cutoff"][11:16], Decimal(a["promise"]["trigger_level"]), Decimal(a["promise"]["invalidation_level"]),
           Decimal(a["promise"]["destination"]), Decimal(a["promise"]["premise_level"]), a["promise"]["original_expiry"][11:16])
          == ("03:45", 100700, 99800, 100900, 97000, "05:30"))
    check("two_calls: original promise ends ORIGINAL_INVALIDATION_CONTACT at 04:04, never activated, revised before",
          (a["original"]["category"], a["original"]["detail"], a["original"]["t"][11:16], a["revised_before_resolution"])
          == ("ANTECEDENT_NEVER_ACTIVATED", "ORIGINAL_INVALIDATION_CONTACT", "04:04", True))
    check("two_calls: engine confirmed with REVISED levels, lifecycle INVALIDATED, one call (proposal, not an outcome)",
          (a["engine_confirmation_vs_original"], a["engine_terminal"], a["calls"])
          == ("REVISED_LEVELS", "INVALIDATED:V_CONTACT", 1))
    check("two_calls: MarketView role at the ARM dispatch is PRINCIPAL", a["view"]["role"] == "PRINCIPAL")
    print(f"{sum(ok)}/{len(ok)} self-test checks pass")
    if not all(ok):
        raise SystemExit(1)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main_run(Path(sys.argv[1]), Path(sys.argv[2]))
