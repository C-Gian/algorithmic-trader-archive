"""Paired synthetic tapes at the v0.6 A confirmation / anchor-loss boundary (evidence, no rule change).

The tapes and the comparison live in ``delivery/evidence/A-CONFIRMATION-BOUNDARY-PAIR/pair.py``: two OHLC tapes
through the ordinary pure v0.6 kernel order, identical except for the close of the first resumption minute
[04:00,04:01): 100049.9 (N, below K + tick) or 100050 (C, at K + tick). The SHORT pair is the reflection about 100000.
These assertions document current behaviour; they are not acceptance of a correction.
"""

from __future__ import annotations

import importlib.util
import json
from decimal import Decimal
from pathlib import Path

import pytest

from algotrader.adviser.harness import run_pure

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "a_confirmation_boundary_pair", ROOT / "delivery/evidence/A-CONFIRMATION-BOUNDARY-PAIR/pair.py")
pair = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pair)

SIDES = ("L", "S")
CONTACT = "2025-09-01T04:02:00Z"


@pytest.fixture(scope="module")
def runs():
    return {(side, v): pair.run(v, side) for side in SIDES for v in ("N", "C")}


def steps(journal):
    return [(x["clock"][11:16], x["kind"], x["transition"], x["reason"], x["terminal"]) for x in pair.lifecycle(journal)]


@pytest.mark.parametrize("side", SIDES)
def test_the_tapes_differ_only_in_the_close_of_the_first_resumption_minute(side):
    [d] = pair.tape_difference(side)
    assert d["family"] == "trade_bar_1m" and d["start"] == "2025-09-01T04:00:00+00:00"
    changed = {k for k in d["N_payload"] if d["N_payload"][k] != d["C_payload"][k]}
    assert changed == {"close", "volume_quote"}  # the fixture's quote volume is close x base volume
    n, c = Decimal(d["N_payload"]["close"]), Decimal(d["C_payload"]["close"])
    assert (n, c) == ((Decimal("100049.9"), Decimal("100050")) if side == "L" else (Decimal("99950.1"), Decimal("99950")))


@pytest.mark.parametrize("side", SIDES)
def test_before_the_v_contact_only_the_confirmation_and_its_consequences_differ(side, runs):
    a, b = pair.norm(runs[side, "N"][0]), pair.norm(runs[side, "C"][0])
    assert [x for x in a if x[1] < "2025-09-01T04:01:00Z"] == [x for x in b if x[1] < "2025-09-01T04:01:00Z"]
    before_n = [x for x in a if x[1] < CONTACT and x not in set(b)]
    before_c = [(k, t) for k, t, _ in b if t < CONTACT and (k, t, _) not in set(a)]
    assert before_n == []
    assert before_c == [("scenario", "2025-09-01T04:01:00Z"), ("entry_attempt", "2025-09-01T04:01:00Z"),
                        ("market_view", "2025-09-01T04:01:00Z")]
    # observations and landmarks are identical over the whole tape; no call in either variant
    for kind in ("observation", "landmark"):
        assert [x for x in a if x[0] == kind] == [x for x in b if x[0] == kind]
    assert not [e for e in runs[side, "N"][0] + runs[side, "C"][0] if e["kind"] == "call"]


@pytest.mark.parametrize("side", SIDES)
def test_lifecycles(side, runs):
    born = ("03:30", "scenario", "BIRTH", "FALSE_AT_OR_AFTER_RELEASE_TO_TRUE", None)
    arm = ("03:45", "scenario", "ARM", None, None)
    revise = ("04:00", "scenario", "REVISE", "LOWER_CLEAN_REACTION_REANCHOR", None)
    later = [("05:30", "scenario", "BIRTH", "FALSE_AT_OR_AFTER_RELEASE_TO_TRUE", None),
             ("07:30", "scenario", "OWNER_RELEASE", "ORIGINAL_SETUP_EXPIRY", None),
             ("07:30", "scenario", "TERMINAL", "ORIGINAL_SETUP_DEADLINE", "EXPIRED"),
             ("07:30", "entry_attempt", "TERMINAL", "SCENARIO_TERMINAL", None)]
    conf = "okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-09-01T04"
    assert steps(runs[side, "N"][0]) == [
        born, arm, revise,
        ("04:02", "scenario", "ANCHOR_LOST", "V_CONTACT", None),
        ("04:15", "scenario", "REARM", "NEW_COMPLETE_STRICTLY_DEEPER_CLEAN_REACTION", None),
        ("04:23", "scenario", "CONFIRM", conf, None),
        ("04:23", "entry_attempt", "WAIT_OPEN", "IMMEDIATE_ECONOMIC_FAILURE_RETURN_CORRIDOR_USABLE", None),
        ("04:24", "entry_attempt", "BLOCKERS", None, None),
        ("04:46", "entry_attempt", "BLOCKERS", None, None),
        ("04:53", "entry_attempt", "TERMINAL", "PRE_ENTRY_TARGET_CONTACT", None),
        ("05:03", "scenario", "TERMINAL", "DESTINATION_CONTACT", "DESTINATION_REACHED"), *later]
    assert steps(runs[side, "C"][0]) == [
        born, arm, revise,
        ("04:01", "scenario", "CONFIRM", conf, None),
        ("04:01", "entry_attempt", "WAIT_OPEN", "IMMEDIATE_ECONOMIC_FAILURE_RETURN_CORRIDOR_USABLE", None),
        ("04:02", "scenario", "TERMINAL", "V_CONTACT", "INVALIDATED"),
        ("04:02", "entry_attempt", "TERMINAL", "SCENARIO_TERMINAL", None), *later]
    # the replacement in N is on the SAME owner and impulse (no new birth); its levels are the next reaction's
    n = pair.lifecycle(runs[side, "N"][0])
    rearm = next(x for x in n if x["transition"] == "REARM")
    flip = (lambda x: Decimal(x)) if side == "L" else (lambda x: 200000 - Decimal(x))
    assert rearm["owner"] == n[0]["owner"] and (Decimal(rearm["K"]), Decimal(rearm["V"])) == (flip(100050), flip(99500))
    # the 05:30 birth (a new impulse formed by the continuation itself) is the same record in both variants
    bn = [x for x in pair.norm(runs[side, "N"][0]) if x[0] == "scenario" and x[1] == "2025-09-01T05:30:00Z"]
    bc = [x for x in pair.norm(runs[side, "C"][0]) if x[0] == "scenario" and x[1] == "2025-09-01T05:30:00Z"]
    assert bn == bc and len(bn) == 1


@pytest.mark.parametrize("side", SIDES)
def test_derived_state_effects_are_bounded_and_reported(side, runs):
    sn, sc = runs[side, "N"][1], runs[side, "C"][1]
    d = 1 if side == "L" else -1
    for t in sn:
        diff = {k for k in pair.AGGREGATIONS if sn[t].get(k) != sc[t].get(k)}
        assert diff <= {"disl"}, (t, diff)
        if diff:  # one matched trade/mark slot of the 60-slot baseline: about -0.01 bps in N, 0 in C
            for p in ("TRADE_MARK", "TRADE_INDEX"):
                a, b = sn[t]["disl"][p]["base"], sc[t]["disl"][p]["base"]
                idx = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
                assert len(a) == len(b) == 60 and len(idx) == 1 and b[idx[0]] == "0"
                assert abs(Decimal(a[idx[0]])) < Decimal("0.011")
    assert {t[11:16] for t in sn if sn[t]["disl"] != sc[t]["disl"]} == {"04:01", "04:02", "04:15", "04:23"}
    # renewal state: C's owner is released at the contact and its latch becomes READY at the next Q_A false
    held = {t[11:16]: (bool(sn[t]["v3"]["a_owner"].get(str(d))), bool(sc[t]["v3"]["a_owner"].get(str(d))))
            for t in sn}
    assert held == {"04:00": (True, True), "04:01": (True, True), "04:02": (True, False), "04:15": (True, False),
                    "04:23": (True, False), "05:03": (False, False), "05:30": (True, True)}
    latch = {t[11:16]: (sn[t]["latch"][str(d)], sc[t]["latch"][str(d)]) for t in sn}
    assert latch["04:15"] == latch["04:23"] == latch["05:03"] == ("NEED_FALSE", "READY")
    assert latch["05:30"] == ("NEED_FALSE", "NEED_FALSE")


def test_pausing_to_read_state_does_not_change_the_journal(runs):
    for v in ("N", "C"):
        res = run_pure(pair.DAY1, pair.tape(v), eval_start=pair.DAY2, method=pair.METHOD)
        assert pair.norm(res.journal) == pair.norm(runs["L", v][0])


def test_committed_comparison_matches_a_fresh_run():
    committed = json.loads((ROOT / "delivery/evidence/A-CONFIRMATION-BOUNDARY-PAIR/comparison.json").read_text(
        encoding="utf-8"))
    fresh = json.loads(json.dumps({"LONG": pair.compare("L")}, sort_keys=True, default=str))
    assert committed["LONG"] == fresh["LONG"]
