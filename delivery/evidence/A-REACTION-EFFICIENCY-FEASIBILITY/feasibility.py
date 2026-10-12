"""A reaction directional efficiency: synthetic feasibility step (separate from the product; engineering inputs only).

Feeds synthetic OHLC through the ordinary v0.6 entry paths, i.e. the pure historical kernel order (``harness.run_pure``:
temporal clock, readiness, admission) from the first warm-up minute, and one live session (``LiveSession.start`` with
catch-up, then recorded receipts) for the recorded-time case. Then it reads ONLY the published scenario records and the
admitted trade bars (``available_time``) to compute, outside the engine:

* the oriented domain q = d * price, Aq / Bq from the transformed extremes of the A source window, q0 = the source bar
  close, and E = (q0 - qn) / sum |qj - q(j-1)| on the admitted prefix (zero denominator UNDEFINED, never 0);
* the single primary observation at the first ARM publication (cutoff), its comparison key, and
* the frozen outcome after the cutoff (B before the premise failure within the original structural horizon), with
  explicit coverage of the horizon, checked also on a few targeted hand-built cases of the classifier alone.

Nothing here injects a scenario, anchor, call or guidance, or touches a gate, readiness or timestamp. Synthetic paths
are not market data; no result here is an economic or predictive finding.

Run from the repository root:  .venv/Scripts/python.exe delivery/evidence/A-REACTION-EFFICIENCY-FEASIBILITY/feasibility.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))

from adviser3_fixtures import DAY1, DAY2, a3_base, bar15, a3_return_long, flat, minute, mirror, walk  # noqa: E402
from algotrader.adviser.harness import Minute, build_events, run_pure  # noqa: E402

D = Decimal
MIN = timedelta(minutes=1)
M15 = timedelta(minutes=15)
METHOD = "v0.6"
OUT = Path(__file__).resolve().parent / "results.json"
BIN = D("0.25")  # comparison bin, in birth-S15 units (the method's own reaction_min_scale unit; not a quality threshold)


def T(h: int, m: int = 0) -> datetime:
    return DAY2 + timedelta(hours=h, minutes=m)


def idx(t: datetime) -> int:
    return int((t - DAY1) / MIN)


def iso(t: datetime | None) -> str | None:
    return None if t is None else t.isoformat().replace("+00:00", "Z")


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# ----------------------------------------------------------------------------------------------------------------------
# synthetic paths (the a3_base A LONG episode; only the minutes inside the first reaction bar and after the cutoff vary)
# ----------------------------------------------------------------------------------------------------------------------

BASE = a3_base()
I_REACT, I_CUT = idx(T(3, 30)), idx(T(3, 45))  # reaction bar [03:30,03:45); first ARM expected at 03:45


def m(o, h, lo, c) -> Minute:
    return minute(o, h, lo, c)


def from_closes(o, closes) -> list[Minute]:
    out, p = [], D(str(o))
    for c in closes:
        c = D(str(c))
        out.append(m(p, max(p, c), min(p, c), c))
        p = c
    return out


# Every prefix has the 15m aggregate o 100700 h 100700 l 100000 c 100049.9 of the existing fixture bar.
PREFIX = {
    # existing fixture bar15(..., "HL"): 5 flat minutes at 100700, 5 down to 100000, 5 up to 100049.9
    "BASE": BASE[I_REACT:I_CUT],
    # same endpoints and total variation, front-loaded: down in 2 minutes, 12 flat, up in the last
    "FRONT": from_closes(100700, [100350, 100000] + [100000] * 12 + ["100049.9"]),
    # same endpoints, same 15m OHLC, alternating recoveries
    "ALT": from_closes(100700, [100300, 100600, 100150, 100550, 100000, 100450, 100100, 100500, 100050, 100400,
                                100000, 100350, 100100, 100300, "100049.9"]),
    # BASE with the minute [03:37,03:38) MISSING (no fill)
    "GAP": BASE[I_REACT:I_REACT + 7] + [Minute(D(0), D(0), D(0), D(0), gap=True)] + BASE[I_REACT + 8:I_CUT],
}

AFTER = BASE[I_CUT:]  # [03:45,04:00) REVISE bar + [04:00,04:01) confirming minute of the fixture


def cont_b() -> list[Minute]:
    """The existing a3_return_long continuation: confirmation, RETURN call, rally through B 100900."""
    return a3_return_long()[I_CUT:]


def cont_h() -> list[Minute]:
    """REVISE, confirmation, then flat around 100050: neither B nor the premise before the horizon."""
    return AFTER + flat(420, AFTER[-1].c)


def cont_f() -> list[Minute]:
    """REVISE at 04:00, ANCHOR_LOST inside [04:00,04:15), REARM at 04:15, decline to a 15m close <= A+z at 05:00,
    then a rally through B before the horizon (B after the failure)."""
    ms = BASE[I_CUT:I_CUT + 15]                                   # [03:45,04:00): REVISE (R 99900, V 99700)
    ms += bar15(99950, 99960, 99600, 99650, order="HL")            # [04:00,04:15): low 99600 <= V, close 99650
    ms += walk(99650, 97100, 45)                                   # [04:15,05:00): 15m close 97100 at 05:00
    ms += walk(97100, 101000, 25)                                  # [05:00,05:25): through B 100900
    return ms + flat(420, 101000)


def cont_g() -> list[Minute]:
    """As cont_h with the trade minute [04:30,04:31) MISSING."""
    ms = cont_h()
    k = idx(T(4, 30)) - I_CUT
    return ms[:k] + [Minute(D(0), D(0), D(0), D(0), gap=True)] + ms[k + 1:]


def cont_x() -> list[Minute]:
    """The first minute after the cutoff [03:45,03:46) reaches B (100900) and closes 100100; then flat."""
    return [m("100049.9", 100900, "100049.9", 100100)] + flat(480, 100100)


CONT = {"B": cont_b, "H": cont_h, "F": cont_f, "G": cont_g, "X": cont_x}


def tape(prefix: str, cont: str, side: str) -> list[Minute]:
    ms = BASE[:I_REACT] + PREFIX[prefix] + CONT[cont]()
    return ms if side == "LONG" else mirror(ms)


# ----------------------------------------------------------------------------------------------------------------------
# running through the ordinary entry paths
# ----------------------------------------------------------------------------------------------------------------------

@dataclass
class Bar1:
    start: datetime
    end: datetime
    known_at: datetime
    o: Decimal
    h: Decimal
    lo: Decimal
    c: Decimal


def run_historical(ms: list[Minute]):
    res = run_pure(DAY1, ms, eval_start=DAY2, method=METHOD)
    evs, _ = build_events(DAY1, ms)  # the very events run_pure admitted (same builder, same order)
    bars, gaps = [], []
    for e in evs:
        if e.channel.family.value != "trade_bar_1m":
            continue
        if e.kind.value == "bar_observation":
            p = e.payload
            bars.append(Bar1(e.event_time, e.event_end_time, e.available_time, p.open, p.high, p.low, p.close))
        else:
            gaps.append(e.event_time)
    return res.journal, bars, gaps


def run_live(ms: list[Minute], until: datetime):
    import test_mp004_live as L  # existing live helper: catch-up start at 03:16, then recorded receipts

    sess, _ = L.session(ms, until, method=METHOD)
    journal, _, tp = sess.driver.take()
    bars = []
    for x in tp:
        e = x.get("event")
        if x.get("cmd") != "admit" or e is None or e["channel"]["family"] != "trade_bar_1m" \
                or e["kind"] != "bar_observation":
            continue
        p = e["payload"]
        bars.append(Bar1(dt(e["event_time"]), dt(e["event_end_time"]), dt(e["available_time"]), D(p["open"]),
                         D(p["high"]), D(p["low"]), D(p["close"])))
    # minutes before the session's catch-up interval are not on the tape: rebuild them from the same tape input
    first = min(b.start for b in bars)
    pre = [Bar1(DAY1 + i * MIN, DAY1 + (i + 1) * MIN, DAY1 + (i + 1) * MIN, x.o, x.h, x.lo, x.c)
           for i, x in enumerate(ms) if DAY1 + i * MIN < first]
    return journal, sorted(pre + bars, key=lambda b: b.start), []


# ----------------------------------------------------------------------------------------------------------------------
# the external measure (never fed back to the engine)
# ----------------------------------------------------------------------------------------------------------------------

def tq(b: Bar1, d: int):
    """Transformed (o, high_q, low_q, close_q): SHORT high_q = -low, low_q = -high."""
    return (d * b.o, d * b.h, d * b.lo, d * b.c) if d > 0 else (d * b.o, d * b.lo, d * b.h, d * b.c)


def efficiency(q0: Decimal, qs: list[Decimal]) -> dict:
    if not qs:
        return {"status": "INSUFFICIENT_DATA", "E": None, "n": 0}
    tv = sum((abs(b - a) for a, b in zip([q0] + qs, qs)), D(0))
    if tv == 0:
        return {"status": "UNDEFINED_ZERO_DENOMINATOR", "E": None, "n": len(qs), "net": "0", "tv": "0"}
    return {"status": "VALUE", "E": str(((q0 - qs[-1]) / tv).quantize(D("0.00001"))), "n": len(qs),
            "net": str(q0 - qs[-1]), "tv": str(tv)}


def prefix_at(bars: list[Bar1], gaps: list[datetime], origin: datetime, t: datetime):
    """Admitted complete minutes wholly after the origin, ending <= t and known_at <= t; a missing minute inside the
    covered span makes the prefix INCOMPLETE (no fill); a bar crossing the origin is excluded and reported."""
    use = [b for b in bars if b.start >= origin and b.end <= t and b.known_at <= t]
    crossing = [b for b in bars if b.start < origin < b.end]
    covered_until = max([b.end for b in use], default=origin)
    expected = int((covered_until - origin) / MIN)
    missing = [iso(g) for g in gaps if origin <= g < t] + \
        [iso(origin + i * MIN) for i in range(expected) if not any(b.start == origin + i * MIN for b in use)]
    return use, sorted(set(missing)), crossing


def measure(bars, gaps, origin, q0, d, t) -> dict:
    use, missing, crossing = prefix_at(bars, gaps, origin, t)
    out = efficiency(q0, [tq(b, d)[3] for b in use])
    if missing:
        out = {"status": "INCOMPLETE_MISSING_MINUTE", "E": None, "n": len(use), "missing": missing}
    out["crossing_origin_excluded"] = [iso(b.start) for b in crossing]
    out["last_bar"] = None if not use else {"interval": [iso(use[-1].start), iso(use[-1].end)],
                                            "known_at": iso(use[-1].known_at)}
    return out


def agg15(bars: list[Bar1], start: datetime):
    xs = [b for b in bars if start <= b.start < start + M15]
    if len(xs) != 15:
        return None
    return xs[0].o, max(b.h for b in xs), min(b.lo for b in xs), xs[-1].c


def outcome(bars, gaps, d, cutoff, horizon, bq, pq) -> dict:
    """Frozen at the cutoff. Walks the 1m grid in market time, from the minute containing the cutoff to the last
    minute starting before the horizon H, and resolves at the first of:
    * B contact: a complete 1m bar wholly after the cutoff with high_q >= Bq;
    * premise failure: a complete 15m close_q <= Aq + z, the 15m bar ending after the cutoff.
    An event counts only if its bar ends before H and is made known before H (inherited order: timers precede
    intervals and 15m closes admitted at the same instant). Market-time order of interval ends; no intrabar order is
    inferred. HORIZON_OBSERVED_NO_B requires complete coverage: every minute starting before H present and, if it ends
    before H, known before H. Otherwise:
    * a minute missing (gap or absent) -> INCOMPLETE_CENSORED / INTERRUPTED;
    * a minute ending before H but made known only at/after H -> INCOMPLETE_CENSORED / DELAYED;
    * a B contact in the minute reaching H (start < H <= end), never knowable before H -> AMBIGUOUS / HORIZON;
    * a B contact in the minute straddling the cutoff -> AMBIGUOUS / CUTOFF."""
    by_start = {b.start: b for b in bars}
    gapset = set(gaps)
    t = cutoff.replace(second=0, microsecond=0)
    notes = []
    while t < horizon:
        b = None if t in gapset else by_start.get(t)
        if b is None:
            return {"class": "INCOMPLETE_CENSORED", "kind": "INTERRUPTED", "at": iso(t),
                    "detail": f"trade minute [{iso(t)},{iso(t + MIN)}) MISSING before resolution"}
        _, hq, _, _ = tq(b, d)
        if b.start < cutoff:  # straddles the cutoff publication
            if hq >= bq:
                return {"class": "AMBIGUOUS", "kind": "CUTOFF", "at": iso(b.end),
                        "detail": f"B reached in [{iso(b.start)},{iso(b.end)}) straddling the cutoff {iso(cutoff)}"}
            t = b.end
            continue
        if b.end >= horizon:  # the minute reaching H: its content is never known before H
            if hq >= bq:
                return {"class": "AMBIGUOUS", "kind": "HORIZON", "at": iso(b.end),
                        "detail": f"B reached in [{iso(b.start)},{iso(b.end)}) reaching the horizon {iso(horizon)}, "
                                  f"made known at {iso(b.known_at)}"}
            a = agg15(bars, b.end - M15) if b.end.minute % 15 == 0 and b.end.second == 0 else None
            if a is not None and tq(Bar1(b.start, b.end, b.known_at, *a), d)[3] <= pq:
                notes.append(f"15m close {a[3]} at {iso(b.end)}, not before the horizon: outside")
            break
        if b.known_at >= horizon:
            return {"class": "INCOMPLETE_CENSORED", "kind": "DELAYED", "at": iso(b.end),
                    "detail": f"[{iso(b.start)},{iso(b.end)}) ends before the horizon {iso(horizon)} but was made "
                              f"known at {iso(b.known_at)}"}
        if hq >= bq:
            return {"class": "B_BEFORE_PREMISE_FAILURE", "at": iso(b.end), "detail": f"1m high {b.h}"}
        if b.end.minute % 15 == 0 and b.end.second == 0:
            a = agg15(bars, b.end - M15)
            if a is not None and tq(Bar1(b.start, b.end, b.known_at, *a), d)[3] <= pq:
                later = next((x for x in bars if x.start >= b.end and x.known_at < horizon and tq(x, d)[1] >= bq), None)
                return {"class": "PREMISE_FAILURE_BEFORE_B", "at": iso(b.end), "detail": f"15m close {a[3]}",
                        "later_B_contact_not_counted": None if later is None else iso(later.end)}
        t = b.end
    return {"class": "HORIZON_OBSERVED_NO_B", "at": iso(horizon), "coverage": "COMPLETE",
            "detail": f"every minute of [{iso(cutoff)},{iso(horizon)}) present and, ending before the horizon, known "
                      f"before it; B not reached", "notes": notes}


def classifier_cases() -> list[dict]:
    """A few targeted synthetic cases of outcome() alone (hand-built 1m bars, not engine runs): LONG flat at 100050
    with Bq 100900 and premise 97200; SHORT = the same tape mirrored about 100000 (every q shifted by -200000).
    'hist': known_at = end, cutoff 03:45:00, H 05:30:00 (on the grid). 'live': known_at = end + 1 s, cutoff and H
    at +1.5 s, so [05:30,05:31) reaches H."""
    def build(clock, edits=None, drop=(), late=None):
        edits, late = edits or {}, late or {}
        lag = timedelta(0) if clock == "hist" else timedelta(seconds=1)
        out = []
        for k in range(int((T(5, 45) - T(3, 30)) / MIN)):
            s = T(3, 30) + k * MIN
            if s in drop:
                continue
            o, h, lo, c = edits.get(s, (D(100050),) * 4)
            out.append(Bar1(s, s + MIN, late.get(s, s + MIN + lag), o, h, lo, c))
        return out

    def mir(bs):
        return [Bar1(b.start, b.end, b.known_at, 200000 - b.o, 200000 - b.lo, 200000 - b.h, 200000 - b.c) for b in bs]

    B1 = (D(100050), D(100910), D(100050), D(100050))  # 1m touching B, closing back
    P15 = (D(100050), D(100050), D(97100), D(97100))  # 1m closing its 15m bar at 97100 <= 97200
    cases = [
        ("complete coverage, no B", "hist", {}, (), {}, "HORIZON_OBSERVED_NO_B", None),
        ("interrupted: feed stops after 05:09", "hist", {}, [T(5, 10) + k * MIN for k in range(35)], {},
         "INCOMPLETE_CENSORED", "INTERRUPTED"),
        ("delayed, no event: [05:00,05:01) known 05:40", "hist", {}, (), {T(5, 0): T(5, 40)},
         "INCOMPLETE_CENSORED", "DELAYED"),
        ("delayed B contact: [05:00,05:01) touches B, known 05:40", "hist", {T(5, 0): B1}, (), {T(5, 0): T(5, 40)},
         "INCOMPLETE_CENSORED", "DELAYED"),
        ("B in the minute reaching H [05:29,05:30)", "hist", {T(5, 29): B1}, (), {}, "AMBIGUOUS", "HORIZON"),
        ("premise 15m close exactly at H (05:30)", "hist", {T(5, 29): P15}, (), {}, "HORIZON_OBSERVED_NO_B", None),
        ("minute reaching H missing", "hist", {}, (T(5, 29),), {}, "INCOMPLETE_CENSORED", "INTERRUPTED"),
        ("live: B in [05:29,05:30), known 05:30:01 < H", "live", {T(5, 29): B1}, (), {},
         "B_BEFORE_PREMISE_FAILURE", None),
        ("live: B in [05:30,05:31) straddling H 05:30:01.5", "live", {T(5, 30): B1}, (), {}, "AMBIGUOUS", "HORIZON"),
        ("live: complete coverage, no B", "live", {}, (), {}, "HORIZON_OBSERVED_NO_B", None),
    ]
    res = []
    for name, clock, edits, drop, late, want, kind in cases:
        off = timedelta(0) if clock == "hist" else timedelta(seconds=1.5)
        cut, hor = T(3, 45) + off, T(5, 30) + off
        for side in ("LONG", "SHORT"):
            bs = build(clock, edits, drop, late)
            d, shift = (1, D(0)) if side == "LONG" else (-1, D(-200000))
            got = outcome(mir(bs) if d < 0 else bs, [], d, cut, hor, D(100900) + shift, D(97200) + shift)
            res.append({"case": name, "side": side, "cutoff": iso(cut), "horizon": iso(hor), "expected": want,
                        "expected_kind": kind, "got": got,
                        "pass": got["class"] == want and got.get("kind") == kind})
    return res


# ----------------------------------------------------------------------------------------------------------------------
# episode extraction from the published records
# ----------------------------------------------------------------------------------------------------------------------

def episode(name: str, journal, bars, gaps, side: str) -> dict:
    d = 1 if side == "LONG" else -1
    pre = "AL" if d > 0 else "AS"
    sc = [e for e in journal if e["kind"] == "scenario" and e["record"]["scenario_id"].startswith(pre)]
    birth = next(e for e in sc if e["record"]["transition"] == "BIRTH")
    sid = birth["record"]["scenario_id"]
    sc = [e for e in sc if e["record"]["scenario_id"] == sid]
    rec = birth["record"]
    born = dt(birth["clock_time"])
    src_end = born.replace(second=0, microsecond=0)  # source bar = the 15m bar whose close fired the birth
    src = [agg15(bars, src_end - M15 * (k + 1)) for k in range(7)]
    lows_q = [x[2] if d > 0 else -x[1] for x in src]  # SHORT: low_q = -high
    highs_q = [x[1] if d > 0 else -x[2] for x in src]  # SHORT: high_q = -low
    aq, bq = min(lows_q), max(highs_q)
    z, s15 = D(rec["setup"]["zone_halfwidth"]), D(rec["setup"]["s15"])
    q0 = d * src[0][3]
    check = {"Aq_matches_record": aq == d * D(rec["setup"]["impulse_A"]),
             "Bq_matches_record": bq == d * D(rec["setup"]["impulse_B"]), "Iq": str(bq - aq)}
    arm = next((e for e in sc if e["record"]["transition"] == "ARM"), None)
    lifecycle = [{"clock": e["clock_time"], "transition": e["record"]["transition"], "reason": e["record"]["reason"],
                  "terminal": e["record"]["terminal_state"]} for e in sc]
    others = [{"clock": e["clock_time"], "kind": e["kind"],
               "what": e["record"].get("transition") or e["record"].get("status") or e["record"].get("state")}
              for e in journal if e["kind"] in ("entry_attempt", "call", "call_revision")
              and (e["record"].get("scenario_id", "") == sid or e["kind"] != "entry_attempt")]
    out = {"episode": name, "side": side, "scenario_id": sid, "birth_published": iso(born), "origin": iso(src_end),
           "q0": str(q0), "source_close": str(src[0][3]), "Aq": str(aq), "Bq": str(bq), "zone": str(z),
           "s15_birth": str(s15), "record_check": check, "lifecycle": lifecycle, "entries_calls": others[:12]}
    if arm is None:
        out["cutoff"] = None
        out["E_at_cutoff"] = {"status": "NO_FIRST_ARM_NOT_IN_POPULATION"}
        out["E_trajectory"] = [{"t": iso(src_end + k * MIN), **measure(bars, gaps, src_end, q0, d, src_end + k * MIN)}
                               for k in range(0, 31, 5)]
        return out
    cut = dt(arm["clock_time"])
    ar = arm["record"]
    before = [x for x in lifecycle if dt(x["clock"]) < cut and x["transition"] != "BIRTH"]
    out["cutoff"] = iso(cut)
    out["arm_record"] = {"activated_at": ar["activated_at"], "destination_monitoring_from":
                         ar["destination_monitoring_from"], "R": str(ar["reaction_level"]),
                         "K": str(ar["trigger_level"]), "V": str(ar["invalidation_level"]),
                         "bars_seen": ar["setup"]["bars_seen"], "original_expiry": ar["original_expiry"],
                         "premise": ar["premise"]}
    out["no_transition_between_birth_and_cutoff"] = not before
    e_cut = measure(bars, gaps, src_end, q0, d, cut)
    out["E_at_cutoff"] = e_cut
    # descriptive trajectory: every admitted minute until the first confirmation / terminal (append-only)
    stop = next((dt(x["clock"]) for x in lifecycle if x["transition"] in ("CONFIRM", "TERMINAL")), cut + 45 * MIN)
    traj = []
    for b in [b for b in bars if b.start >= src_end and b.known_at <= stop]:
        r = measure(bars, gaps, src_end, q0, d, b.known_at)
        traj.append({"interval": [iso(b.start), iso(b.end)], "known_at": iso(b.known_at), "close": str(b.c),
                     "q": str(tq(b, d)[3]), "status": r["status"], "E": r["E"], "n": r["n"]})
    out["E_trajectory_first"] = {"t": iso(src_end), **measure(bars, gaps, src_end, q0, d, src_end)}
    out["E_trajectory"] = traj
    # E on the prefix known at each published scenario transition: one profile, never reset by REVISE/REARM
    out["E_at_lifecycle_without_reset"] = [
        {"clock": x["clock"], "transition": x["transition"],
         **{k: v for k, v in measure(bars, gaps, src_end, q0, d, dt(x["clock"])).items() if k in ("status", "E", "n")}}
        for x in lifecycle if dt(x["clock"]) <= stop]
    # comparison key at the cutoff (all orientation-free; S15 = frozen birth scale)
    mv = next((e["record"] for e in journal if e["kind"] == "market_view" and e["clock_time"] == arm["clock_time"]),
              None)
    use, _, _ = prefix_at(bars, gaps, src_end, cut)
    qc = tq(use[-1], d)[3] if use else None
    pq = aq + z
    if qc is not None:
        db, dp = (bq - qc) / s15, (qc - pq) / s15
        phase = mv["phase"] if mv else None  # an ARM excludes opposite EXPANSION: EXPANSION here is with d
        out["comparison"] = {"age_bars": int((cut.replace(second=0, microsecond=0) - src_end) / M15),
                             "phase": phase, "dB_s15": str(db.quantize(D("0.0001"))),
                             "dP_s15": str(dp.quantize(D("0.0001"))), "bin_dB": int(db // BIN),
                             "bin_dP": int(dp // BIN), "context_at_cutoff": mv["observed_context"] if mv else None,
                             "derived_I_s15": str(((bq - aq) / s15).quantize(D("0.0001"))),
                             "derived_x": str(((bq - qc) / (bq - aq)).quantize(D("0.0001"))),
                             "R_depth_I_descriptive": str(((bq - d * D(str(ar["reaction_level"]))) /
                                                           (bq - aq)).quantize(D("0.0001")))}
    horizon = born + timedelta(minutes=120)
    out["horizon_matches_record"] = dt(str(ar["original_expiry"])) == horizon
    out["frozen_at_cutoff"] = {"Bq": str(bq), "premise_q_15m_close_at_or_below": str(pq), "horizon": iso(horizon)}
    out["outcome"] = outcome(bars, gaps, d, cut, horizon, bq, pq)
    out["engine_after_cutoff"] = [x for x in lifecycle if dt(x["clock"]) > cut]
    return out


def main() -> None:
    plan = [("BASE", "B"), ("BASE", "F"), ("BASE", "H"), ("BASE", "G"), ("BASE", "X"),
            ("FRONT", "B"), ("ALT", "B"), ("GAP", "H")]
    eps = []
    for side in ("LONG", "SHORT"):
        for p, c in plan:
            j, bars, gaps = run_historical(tape(p, c, side))
            eps.append(episode(f"{p}+{c}/historical", j, bars, gaps, side))
        j, bars, gaps = run_live(tape("BASE", "X", side), T(4, 0))
        eps.append(episode("BASE+X/live", j, bars, gaps, side))
    # reflection: every LONG/SHORT pair must give identical E, keys and outcome classes
    refl = []
    for a in eps:
        if a["side"] != "LONG":
            continue
        b = next(x for x in eps if x["side"] == "SHORT" and x["episode"] == a["episode"])
        refl.append({"episode": a["episode"], "E_equal": a["E_at_cutoff"].get("E") == b["E_at_cutoff"].get("E")
                     and a["E_at_cutoff"]["status"] == b["E_at_cutoff"]["status"],
                     "key_equal": {k: v for k, v in (a.get("comparison") or {}).items() if k != "context_at_cutoff"}
                     == {k: v for k, v in (b.get("comparison") or {}).items() if k != "context_at_cutoff"},
                     "outcome_equal": (a.get("outcome") or {}).get("class") == (b.get("outcome") or {}).get("class"),
                     "times_equal": a.get("cutoff") == b.get("cutoff") and a["birth_published"] == b["birth_published"],
                     "Iq_equal": a["record_check"]["Iq"] == b["record_check"]["Iq"]})
    # the LONG prefixes differ only inside the reaction bar: their BIRTH and ARM records must be identical
    def birth_arm(p):
        j, _, _ = run_historical(tape(p, "B", "LONG"))
        return [{k: v for k, v in e["record"].items() if k != "env"} | {"clock": e["clock_time"]} for e in j
                if e["kind"] == "scenario" and e["record"]["transition"] in ("BIRTH", "ARM")]
    ref = birth_arm("BASE")
    same = {p: birth_arm(p) == ref for p in ("FRONT", "ALT")}
    for e in eps:  # eligibility for the single E -> outcome relation (section 4 of the note)
        ok_e = e["E_at_cutoff"].get("status") == "VALUE"
        cls = (e.get("outcome") or {}).get("class")
        e["eligible"] = ok_e and cls in ("B_BEFORE_PREMISE_FAILURE", "PREMISE_FAILURE_BEFORE_B",
                                         "HORIZON_OBSERVED_NO_B")
        e["Y"] = None if not e["eligible"] else int(cls == "B_BEFORE_PREMISE_FAILURE")
    doc = {"prefix_birth_arm_records_identical_to_BASE": same, "purpose": "A reaction directional efficiency: synthetic feasibility (engineering inputs, not market data)",
           "method": METHOD, "episodes": eps, "reflection": refl, "classifier_cases": classifier_cases()}
    OUT.write_text(json.dumps(doc, indent=1, default=str) + "\n", encoding="utf-8")
    print(f"{'episode':24} {'side':5} {'cutoff':22} {'E@cut':9} {'n':>3} {'key (age,phase,binB,binP)':34} outcome")
    for e in eps:
        c = e.get("comparison") or {}
        key = (c.get("age_bars"), c.get("phase"), c.get("bin_dB"), c.get("bin_dP")) if c else None
        print(f"{e['episode']:24} {e['side']:5} {str(e['cutoff']):22} {str(e['E_at_cutoff'].get('E') or e['E_at_cutoff']['status'])[:9]:9} "
              f"{str(e['E_at_cutoff'].get('n', '')):>3} {str(key):34} {(e.get('outcome') or {}).get('class')}")
    print("prefix BIRTH/ARM records identical to BASE:", same)
    print("reflection all equal:", all(all(v for k, v in r.items() if k != "episode") for r in refl))
    cc = doc["classifier_cases"]
    for c in cc:
        print(f"  classifier {c['side']:5} {c['case']:58} {c['got']['class']}/{c['got'].get('kind')}"
              f" {'ok' if c['pass'] else 'FAIL'}")
    print(f"classifier cases passed: {sum(c['pass'] for c in cc)}/{len(cc)}")


if __name__ == "__main__":
    main()
