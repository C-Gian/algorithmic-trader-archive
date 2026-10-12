"""Paired synthetic tapes isolating the A confirmation / anchor-loss boundary of v0.6 (12 October 2026).

Two hand-made OHLC tapes (engineering inputs, NOT market data) on the MP-002 base A LONG geometry of
``tests/adviser3_fixtures.a3_base`` (A 97000, B 100900, birth S15 2000, z 200; ARM 03:45; REVISE at 04:00: R 99900,
K 100049.9, V 99700, confirmation threshold K + 1 tick = 100050). They are identical except for ONE trade close: the
first resumption minute [04:00,04:01) closes at 100049.9 (variant N, just below K + tick) or 100050 (variant C, at
K + tick). Its mark/index closes are pinned to 100050 in both, so no reference series differs. Then, identically:

* [04:01,04:02) o 100050 h 100050 l 99700 c 99950: contact with V 99700, no 15m close at/below A+z 97200;
* [04:02,04:15) drift to 99800: the 15m bar [04:00,04:15) (h 100050, l 99700, c 99800) is the next reaction;
* [04:15,04:25) resumption to 100150, then to 100950 (beyond B) by 05:05, then a flat tail.

Both tapes go through the ordinary pure kernel order of the v0.6 release (feed event -> temporal clock -> professional
barriers -> admission; ``harness.run_pure`` / the tests' ``Stepper``, which only pauses to READ the encoded state).
No state is injected and no gate bypassed. The SHORT pair is the positive-price reflection about 100000.

Writes ``comparison.json`` next to this script; ``tests/test_a_confirmation_boundary_pair.py`` asserts the same facts.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import adviser3_fixtures as f3  # noqa: E402
from adviser3_fixtures import DAY1, DAY2, Stepper, T, flat, minute, walk  # noqa: E402

from algotrader.adviser.harness import Minute, build_events  # noqa: E402

METHOD = "v0.6"
CLOSES = {"N": Decimal("100049.9"), "C": Decimal("100050")}  # LONG; SHORT = reflection
# dispatches after which the encoded state is read (minute ends; the dispatch at t has run)
SNAPSHOTS = (T(4, 0), T(4, 1), T(4, 2), T(4, 15), T(4, 23), T(5, 3), T(5, 30))
# encoded-state keys that are aggregations / derived market state (must not depend on the single close)
AGGREGATIONS = ("m15", "h1", "broad", "last_sealed_end", "gaps", "s15", "s15_hist", "phase", "ctx", "part",
                "landmarks", "pending_pivots", "box", "box_token", "comp_prev", "disl", "qa_last", "funding_last",
                "events")


def tape(variant: str, side: str = "L") -> list[Minute]:
    ms = f3.a3_base()[:-1]  # up to and including the REVISE at 04:00 (the base confirmation minute is replaced)
    ref = Decimal("100050")
    ms.append(Minute(Decimal("99950"), Decimal("100050"), Decimal("99950"), CLOSES[variant], mark=ref, index=ref))
    post = [minute(100050, 100050, 99700, 99950)]
    post += walk(99950, 99800, 13) + walk(99800, 100150, 10) + walk(100150, 100950, 40)
    ms = ms + post + flat(420, post[-1].c)
    return f3.mirror(ms) if side == "S" else ms


def tape_difference(side: str) -> list[dict]:
    """Every feed event that differs between the two tapes (expected: the one trade bar [04:00,04:01))."""
    a, _ = build_events(DAY1, tape("N", side))
    b, _ = build_events(DAY1, tape("C", side))
    if len(a) != len(b):
        raise SystemExit("tapes differ in length")
    out = []
    for x, y in zip(a, b):
        if x.model_dump(mode="json") != y.model_dump(mode="json"):
            out.append({"family": x.channel.family.value, "start": x.event_time.isoformat(),
                        "N_payload": x.payload.model_dump(mode="json"), "C_payload": y.payload.model_dump(mode="json")})
    return out


def run(variant: str, side: str = "L") -> tuple[list[dict], dict[str, dict]]:
    st = Stepper(tape(variant, side), method=METHOD)
    states = {}
    for t in SNAPSHOTS:
        st.run_until(t)
        states[t.isoformat()] = json.loads(json.dumps(st.core.encode(), default=str))
    st.finish()
    return st.journal, states


def _drop_env(x):
    if isinstance(x, dict):
        return {k: _drop_env(v) for k, v in x.items() if k != "env"}
    if isinstance(x, list):
        return [_drop_env(v) for v in x]
    return x


def norm(journal: list[dict]) -> list[tuple[str, str, str]]:
    return [(e["kind"], e["record"]["env"]["clock_time"], json.dumps(_drop_env(e["record"]), sort_keys=True))
            for e in journal]


def lifecycle(journal: list[dict]) -> list[dict]:
    """A scenario / entry-attempt / call records of every A owner, in journal order."""
    out = []
    for e in journal:
        r = e["record"]
        if e["kind"] not in ("scenario", "entry_attempt", "call") or not str(r.get("scenario_id", "")).startswith("A"):
            continue
        out.append({"clock": r["env"]["clock_time"], "kind": e["kind"], "owner": r["scenario_id"].split("-", 1)[1][:25],
                    "transition": r.get("transition"), "reason": (r.get("reason") or "").split(":")[0] or None,
                    "status": r.get("status"), "terminal": r.get("terminal_state"), "epoch": r.get("anchor_epoch"),
                    "K": r.get("trigger_level"), "V": r.get("invalidation_level"),
                    "antecedent": r.get("antecedent") if e["kind"] == "scenario" else None})
    return out


def views(journal: list[dict], lo: str, hi: str) -> list[dict]:
    out = []
    for e in journal:
        r = e["record"]
        if e["kind"] != "market_view" or not (lo <= r["env"]["clock_time"] <= hi):
            continue
        p = r.get("principal") or {}
        out.append({"clock": r["env"]["clock_time"], "expected_direction": r.get("expected_direction"),
                    "table_row": r.get("table_row"), "principal_status": p.get("status"),
                    "principal_antecedent": p.get("antecedent"), "trigger_level": p.get("trigger_level"),
                    "invalidation_level": p.get("invalidation_level"),
                    "watch_antecedents": [w.get("antecedent") for w in r.get("watch") or []]})
    return out


def compare(side: str) -> dict:
    jn, sn = run("N", side)
    jc, sc_ = run("C", side)
    a, b = norm(jn), norm(jc)
    only_n = [x for x in a if x not in set(b)]
    only_c = [x for x in b if x not in set(a)]
    contact = T(4, 2).isoformat().replace("+00:00", "Z")
    state_diff = {}
    for t in sn:
        keys = sorted(set(sn[t]) | set(sc_[t]))
        diff = [k for k in keys if sn[t].get(k) != sc_[t].get(k)]
        v3 = [k for k in sorted(set(sn[t].get("v3", {})) | set(sc_[t].get("v3", {})))
              if sn[t].get("v3", {}).get(k) != sc_[t].get("v3", {}).get(k)]
        state_diff[t] = {"differing_keys": diff, "differing_v3_keys": v3,
                         "aggregations_identical": all(sn[t].get(k) == sc_[t].get(k) for k in AGGREGATIONS),
                         "latch": {"N": sn[t].get("latch"), "C": sc_[t].get("latch")},
                         "a_owner_held": {"N": bool((sn[t].get("v3", {}).get("a_owner") or {}).get("1" if side == "L" else "-1")),
                                          "C": bool((sc_[t].get("v3", {}).get("a_owner") or {}).get("1" if side == "L" else "-1"))}}
    return {
        "tape_difference": tape_difference(side),
        "journal_counts": {"N": dict(Counter(k for k, _, _ in a)), "C": dict(Counter(k for k, _, _ in b))},
        "first_differing_clock": min(t for _, t, _ in only_n + only_c),
        "records_only_in_N": [(k, t) for k, t, _ in only_n],
        "records_only_in_C": [(k, t) for k, t, _ in only_c],
        "differences_before_V_contact": {"N": [(k, t) for k, t, _ in only_n if t < contact],
                                         "C": [(k, t) for k, t, _ in only_c if t < contact]},
        "identical_kinds_throughout": sorted({k for k, _, _ in a + b} - {k for k, _, _ in only_n + only_c}),
        "calls": {"N": sum(1 for e in jn if e["kind"] == "call"), "C": sum(1 for e in jc if e["kind"] == "call")},
        "state_after_dispatch": state_diff,
        "lifecycle": {"N": lifecycle(jn), "C": lifecycle(jc)},
        "views_04_00_to_05_30": {"N": views(jn, "2025-09-01T04:00:00Z", "2025-09-01T05:30:00Z"),
                                 "C": views(jc, "2025-09-01T04:00:00Z", "2025-09-01T05:30:00Z")},
    }


def main() -> None:
    out = {"method": METHOD, "closes_long": {k: str(v) for k, v in CLOSES.items()},
           "generated_from": "hand-made synthetic tapes (engineering inputs, not market data)",
           "LONG": compare("L"), "SHORT": compare("S")}
    text = json.dumps(out, indent=1, sort_keys=True, default=str) + "\n"
    (HERE / "comparison.json").write_text(text, encoding="utf-8", newline="\n")
    for side in ("LONG", "SHORT"):
        o = out[side]
        print(side, "tape differences:", len(o["tape_difference"]), "first differing clock:", o["first_differing_clock"])
        print("  before V contact, only C:", o["differences_before_V_contact"]["C"],
              "only N:", o["differences_before_V_contact"]["N"])
        for v in ("N", "C"):
            print(f"  {v}:", [(x["clock"][11:16], x["kind"][0], x["transition"], x["reason"]) for x in o["lifecycle"][v]])


if __name__ == "__main__":
    main()
