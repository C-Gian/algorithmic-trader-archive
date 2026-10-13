"""EXPERIMENTAL v0.6-a2x second attempt (``delivery/A-SECOND-ATTEMPT-DESIGN.md``, design b20919e, ratification
3705fd0): synthetic proofs only, through the ordinary pure kernel order (cold day-1 history -> warmup, readiness,
context, scale; no scenario, anchor or call placed in any state). Expected levels and times are written by hand from
the tape constants in ``adviser_a2x_fixtures`` (LONG); SHORT runs are the reflection x -> 200000 - x.
"""

from __future__ import annotations

import functools
import hashlib
import json
import zlib
from datetime import timedelta
from decimal import Decimal

import adviser_a2x_fixtures as fx
import pytest
from adviser3_fixtures import Stepper, T, delayed_events, index_of
from test_mp004_versions import _norm  # id-token normalization shared with the v0.5/v0.6 parity tests
from test_mp005_paths import PARITY

from algotrader.adviser import contracts as sc
from algotrader.adviser import core_a2x as a2x
from algotrader.adviser import engine, methods
from algotrader.adviser.harness import build_events, make_runtime, run_pure, temporal_for
from algotrader.adviser.params import load_register
from algotrader.feed.ordering import canonical
from algotrader.temporal import engine as te

X = "v0.6-a2x"
SIDES = ("L", "S")
D = Decimal


def run(ms, method=X, **kw):
    kw.setdefault("eval_start", fx.DAY2)
    return run_pure(fx.DAY1, ms, method=method, **kw)


def side(ms, s):
    return ms if s == "L" else fx.short(ms)


def px(x, s):
    return D(str(x)) if s == "L" else 200000 - D(str(x))


def scen(res, prefix=("AL", "AS")):
    return [e["record"] for e in res.journal if e["kind"] == "scenario" and e["record"]["scenario_id"][:2] in prefix]


def a2x_obs(res):
    return [e["record"] for e in res.journal if e["kind"] == "observation" and e["record"]["name"] == "a_second_attempt"]


def steps(res, sid):
    return [(r["env"]["clock_time"][11:19], r["transition"], (r["reason"] or "").split(":")[0] or None,
             r["terminal_state"]) for r in scen(res) if r["scenario_id"] == sid]


def ids_by_birth(res):
    """(first-attempt id, successor id or None) of the impulse born at 03:30."""
    recs = scen(res)
    s1 = next(r["scenario_id"] for r in recs if r["transition"] == "BIRTH" and r["env"]["clock_time"][11:16] == "03:30")
    s2 = next((r["scenario_id"] for r in recs if r["setup"].get("attempt") == "2"), None)
    return s1, s2


# -- identity, isolation, selection ---------------------------------------------------------------------------------

def test_variant_identity_is_separate_explicit_and_not_selectable():
    v6, vx = methods.get("v0.6"), methods.get(X, experimental=True)
    with pytest.raises(methods.UnknownMethod):
        methods.get(X)  # every application path (API, controls, jobs, live) calls get() without the flag
    assert X not in methods.RELEASES and X not in {m["method"] for m in methods.selectable()}
    assert methods.DEFAULT == "v0.2" and set(methods.RELEASES) == {"v0.2", "v0.3", "v0.4", "v0.5", "v0.6"}
    for f in ("model", "rules_version", "implementation", "core_state_format", "runtime_format", "engine_format"):
        assert getattr(vx, f) != getattr(v6, f), f
    assert vx.rules_sha256() != v6.rules_sha256() and vx.register_sha256() != v6.register_sha256()
    # the frozen v0.6 identity is unchanged (references registered for the A v0.6 studies)
    assert v6.rules_sha256() == "57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66"
    assert v6.register_sha256() == "98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda"
    root = methods.idn.METHOD_DIR
    packaged = (root / "A-SECOND-ATTEMPT-DESIGN.md").read_bytes().replace(b"\r\n", b"\n")
    assert packaged == (root.parents[3] / "delivery/A-SECOND-ATTEMPT-DESIGN.md").read_bytes().replace(b"\r\n", b"\n")
    assert [m["role"] for m in vx.rules_manifest()][:2] == ["DELTA", "BASE_MP005_RULES"]
    # every numerical convention is the MP-005 register unchanged (no new number)
    p6, px_ = load_register(v6.register_file), load_register(vx.register_file)
    assert {k: v for k, v in p6.__dict__.items() if k != "raw"} == {k: v for k, v in px_.__dict__.items() if k != "raw"}
    r6, rx = v6.register(), vx.register()
    assert {k for k in rx if rx[k] != r6.get(k)} == {"model", "status", "rules_version", "identity", "second_attempt"}


def test_v06_behaviour_is_preserved_when_the_variant_is_not_selected():
    res = run(fx.two_calls(), method="v0.6")
    assert not a2x_obs(res) and len(res.calls()) == 1
    assert not [r for r in scen(res) if r["setup"].get("attempt")]
    s1, _ = ids_by_birth(res)
    assert steps(res, s1)[-1] == ("04:04:00", "TERMINAL", "V_CONTACT", "INVALIDATED")


@pytest.mark.parametrize("name", sorted(PARITY))
def test_without_a_confirmed_v_contact_the_variant_equals_v06(name):
    """Every pinned v0.3-v0.6 tape: no review is opened by any other terminal (STALLED, TIME_EXPIRED,
    PRICE_PREMISE_FAILED, DESTINATION_REACHED, UNASSESSABLE, pre-confirmation anchor loss, child-only terminals) and the
    whole journal equals v0.6; with a confirmed V contact every record before that dispatch is identical."""
    r6, rx = run(PARITY[name](), method="v0.6"), run(PARITY[name]())
    kinds = tuple(sorted({e["kind"] for e in r6.journal} | {e["kind"] for e in rx.journal}))
    fail = [r for r in scen(r6) if r["terminal_state"] == "INVALIDATED" and r["confirmed_at"]
            and str(r["reason"]).startswith("V_CONTACT")]
    if not fail:
        assert not a2x_obs(rx)
        assert _norm(rx.journal, kinds) == _norm(r6.journal, kinds)
        return
    cut = fail[0]["env"]["clock_time"]
    assert [x for x in _norm(rx.journal, kinds) if x[1] < cut] == [x for x in _norm(r6.journal, kinds) if x[1] < cut]
    assert a2x_obs(rx)[0]["category"] in ("REVIEW_OPEN", "REVIEW_NOT_OPENED")


# -- the main tape: LONG and SHORT up to an effective successor call -------------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_successor_reaches_an_issued_call_long_and_short(s):
    res = run(side(fx.two_calls(), s))
    s1, s2 = ids_by_birth(res)
    assert s2 is not None and s2 != s1
    assert steps(res, s1) == [("03:30:00", "BIRTH", "FALSE_AT_OR_AFTER_RELEASE_TO_TRUE", None), ("03:45:00", "ARM", None, None),
                              ("04:00:00", "REVISE", "LOWER_CLEAN_REACTION_REANCHOR", None),
                              ("04:01:00", "CONFIRM", "okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-09-01T04", None),
                              ("04:04:00", "TERMINAL", "V_CONTACT", "INVALIDATED")]
    assert steps(res, s2) == [("04:30:00", "ARM", "SECOND_ATTEMPT_FRESH_POST_FAILURE_REACTION", None),
                              ("04:31:00", "CONFIRM", "okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-09-01T04", None),
                              ("05:04:00", "TERMINAL", "DESTINATION_CONTACT", "DESTINATION_REACHED")]
    arm, conf = [r for r in scen(res) if r["scenario_id"] == s2][:2]
    # hand-computed levels: R2 = new low 99650, K2 = the anchor bar's high 100050, V2 = R2 - z = 99450; impulse frozen
    assert (D(arm["reaction_level"]), D(arm["trigger_level"]), D(arm["invalidation_level"])) == (
        px(99650, s), px(100050, s), px(99450, s))
    assert (D(arm["setup"]["impulse_A"]), D(arm["setup"]["impulse_B"]), D(arm["destination"])) == (
        px(97000, s), px(100900, s), px(100900, s))
    assert (D(arm["setup"]["s15"]), D(arm["setup"]["zone_halfwidth"])) == (2000, 200)
    assert arm["setup"]["attempt"] == "2" and arm["setup"]["parent_scenario_id"] == s1 == arm["setup"]["impulse_id"]
    assert arm["setup"]["review_opened_at"] == "2025-09-01T04:04:00+00:00"
    assert arm["setup"]["formation_origin"] == "2025-09-01T04:15:00+00:00"
    assert D(arm["setup"]["failed_attempt_R"]) == px(99900, s)
    assert arm["anchor_source"].endswith("/15m/2025-09-01T04:15:00+00:00")
    assert arm["destination_monitoring_from"] == arm["anchor_published_at"] == "2025-09-01T04:30:00Z"
    assert arm["original_expiry"] == "2025-09-01T05:30:00Z" and arm["anchor_epoch"] == 1
    # clocks bounded by H0 = 05:30: progress at C2 + (H0 - C2)/2 = 04:31 + 29.5 min
    assert (conf["confirmed_at"], conf["confirmed_deadline"], conf["progress_check_at"]) == (
        "2025-09-01T04:31:00Z", "2025-09-01T05:30:00Z", "2025-09-01T05:00:30Z")
    assert D(conf["confirmation_close"]) == px("100050.1", s)
    # two distinct calls: call 2 belongs to the successor, hard deadline H0, progress at issue + (H0 - issue)/2
    c1, c2 = res.calls()
    assert c1["attempt_id"] == f"{s1}#entry" and c2["attempt_id"] == f"{s2}#entry"
    assert (c2["issued_at"], c2["hard_deadline"], c2["progress_check_at"], c2["hard_deadline_origin"]) == (
        "2025-09-01T04:34:00Z", "2025-09-01T05:30:00Z", "2025-09-01T05:02:00Z", "ORIGINAL_IMPULSE_EXPIRY")
    assert (D(c2["invalidation"]), D(c2["issue_reference"]), c2["entry_mode"]) == (px(99450, s), px(99865, s), "RETURN")
    assert c2["confirmed_at"] == "2025-09-01T04:31:00Z" and c2["scenario_id"] == s2
    assert c1["hard_deadline"] == "2025-09-01T08:01:00Z" and c1["hard_deadline_origin"] == "STRUCTURAL_CONFIRMATION_PUBLICATION"
    obs = [(o["env"]["clock_time"][11:19], o["category"]) for o in a2x_obs(res)]
    assert obs == [("04:04:00", "REVIEW_OPEN"), ("04:30:00", "SUCCESSOR_ARMED")]
    assert res.runtime.core.counters["a2x"]["successors_armed"] == 1


@pytest.mark.parametrize("s", SIDES)
def test_first_attempt_child_and_call_records_are_exactly_v06(s):
    ms = side(fx.two_calls(), s)
    r6, rx = run(ms, method="v0.6"), run(ms)
    kinds = tuple(sorted({e["kind"] for e in r6.journal} | {e["kind"] for e in rx.journal}))
    # every record before the failure dispatch, of every kind, is identical
    assert [x for x in _norm(rx.journal, kinds) if x[1] < "2025-09-01T04:04:00Z"] == \
        [x for x in _norm(r6.journal, kinds) if x[1] < "2025-09-01T04:04:00Z"]
    s1x, s2x = ids_by_birth(rx)
    s16, _ = ids_by_birth(r6)
    c1x, c16 = rx.calls()[0]["call_id"], r6.calls()[0]["call_id"]

    def first(res, sid, cid):
        keep = []
        for e in res.journal:
            r = e["record"]
            if (e["kind"] in ("scenario", "entry_attempt") and r["scenario_id"] == sid) or \
                    (e["kind"] in ("call", "call_revision") and r["call_id"] == cid):
                keep.append(e)
        return _norm(keep, ("scenario", "entry_attempt", "call", "call_revision"))

    assert first(rx, s1x, c1x) == first(r6, s16, c16)  # S1, its child and call 1 with their whole history
    assert all(r["call_id"] != c1x for r in rx.revisions() if r["env"]["clock_time"] > "2025-09-01T04:04:00Z")


# -- fresh facts only; no third attempt ------------------------------------------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_old_bars_and_the_old_confirmation_are_never_new_facts(s):
    res = run(side(fx.no_fresh_facts(), s))
    s1, s2 = ids_by_birth(res)
    assert s2 is None and [x[1] for x in steps(res, s1)].count("CONFIRM") == 1
    # the old K 100049.9 is exceeded by later closes without any new confirmation
    mins = side(fx.no_fresh_facts(), s)
    k_old = px("100049.9", s)
    later = mins[index_of(T(4, 15)):index_of(T(5, 30))]
    assert any((m.c > k_old if s == "L" else m.c < k_old) for m in later)
    obs = [(o["env"]["clock_time"][11:19], o["category"], o["values"].get("state")) for o in a2x_obs(res)]
    assert obs == [("04:04:00", "REVIEW_OPEN", None), ("05:30:00", "REVIEW_CLOSED", "EXPIRED")]
    closed = a2x_obs(res)[-1]["values"]
    # [04:15,04:30) had a contrary close (c < o) but its low 99950 is not below R1 99900: new low recorded, no arm
    assert closed["contrary_close_seen"] == "true" and D(closed["new_reaction_low"]) == px(99940, s)  # quiet-bar low
    assert closed["new_bars"] == "4"  # [04:15,04:30)..[05:00,05:15): the failure bar never counts; the bar ending at H0 follows the timer


@pytest.mark.parametrize("s", SIDES)
def test_an_earlier_recovery_and_the_old_confirmation_never_confirm_the_successor(s):
    ms = side(fx.old_recovery_before_arm(), s)
    k2_tick = px("100050.1", s)
    early = ms[index_of(T(4, 4)):index_of(T(4, 15))]
    assert any((m.c >= k2_tick if s == "L" else m.c <= k2_tick) for m in early)  # a recovery-like close exists early
    res = run(ms)
    s1, s2 = ids_by_birth(res)
    assert [x[1] for x in steps(res, s1)].count("CONFIRM") == 1  # the old K exceeded: no re-confirmation of S1
    arm, conf = [r for r in scen(res) if r["scenario_id"] == s2][:2]
    assert D(arm["trigger_level"]) == px(100050, s)  # K2 from the fresh bar only (the failure bar's 100100 excluded)
    assert conf["transition"] == "CONFIRM" and conf["reason"].endswith("@2025-09-01T04:30:00Z")
    assert conf["confirmed_at"] == "2025-09-01T04:31:00Z" > arm["anchor_published_at"]


@pytest.mark.parametrize("s", SIDES)
def test_no_third_attempt(s):
    res = run(side(fx.third_attempt_refused(), s))
    s1, s2 = ids_by_birth(res)
    assert steps(res, s2)[-1] == ("04:38:00", "TERMINAL", "V_CONTACT", "INVALIDATED")
    assert [o["category"] for o in a2x_obs(res)] == ["REVIEW_OPEN", "SUCCESSOR_ARMED"]  # nothing after S2's failure
    assert [r["scenario_id"] for r in scen(res) if r["setup"].get("attempt") == "2"] and \
        {r["scenario_id"] for r in scen(res) if r["setup"].get("attempt") == "2"} == {s2}
    late = [r for r in scen(res) if r["env"]["clock_time"] > "2025-09-01T04:38:00Z" and r["transition"] in ("ARM", "CONFIRM")]
    assert late == []
    c = res.runtime.core.counters["a2x"]
    assert (c["reviews_opened"], c["successors_armed"]) == (1, 1)
    assert len(res.calls()) == 2 and res.revisions()[-1]["thesis_status"] == "INVALIDATED"


# -- precedences: premise, B, gap/staleness, H0 -----------------------------------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_premise_close_before_arm_ends_the_review(s):
    res = run(side(fx.premise_before_arm(), s))
    assert ids_by_birth(res)[1] is None
    o = a2x_obs(res)
    assert [(x["env"]["clock_time"][11:19], x["category"], x["values"].get("reason")) for x in o] == [
        ("04:04:00", "REVIEW_OPEN", None), ("04:30:00", "REVIEW_CLOSED", "CLOSE_AT_OR_BEYOND_A_PLUS_ZONE")]


@pytest.mark.parametrize("s", SIDES)
def test_premise_close_in_the_failure_dispatch_excludes_the_review_and_keeps_v06(s):
    ms = side(fx.premise_in_failure_dispatch(), s)
    r6, rx = run(ms, method="v0.6"), run(ms)
    o = a2x_obs(rx)
    assert [(x["env"]["clock_time"][11:19], x["category"], x["values"]["reason"]) for x in o] == [
        ("04:15:00", "REVIEW_NOT_OPENED", "PREMISE_CLOSE_AT_OR_BEYOND_A_PLUS_Z_KNOWN")]
    kinds = tuple(sorted({e["kind"] for e in r6.journal}))
    strip = [e for e in rx.journal if not (e["kind"] == "observation" and e["record"]["name"] == "a_second_attempt")]
    assert _norm(strip, kinds) == _norm(r6.journal, kinds)  # otherwise exactly v0.6 (owner released at 04:15)


@pytest.mark.parametrize("s", SIDES)
def test_destination_gap_and_staleness_close_the_review(s):
    b = run(side(fx.destination_in_review(), s))
    g = run(side(fx.gap_in_review(), s))
    ms = side(fx.two_calls(), s)
    st = Stepper(ms, method=X, events=delayed_events(ms, {index_of(T(4, 20 + k)): 270 - 60 * k for k in range(5)}))
    st.finish()
    stale = [e["record"] for e in st.journal if e["kind"] == "observation" and e["record"]["name"] == "a_second_attempt"]
    got = [[(x["env"]["clock_time"][11:19], x["values"].get("state"), x["values"].get("reason", "").split(":")[0])
            for x in o if x["category"] == "REVIEW_CLOSED"] for o in (a2x_obs(b), a2x_obs(g), stale)]
    assert got == [[("04:55:00", "DESTINATION_REACHED", "DESTINATION_CONTACT")],
                   [("04:21:00", "UNASSESSABLE", "REQUIRED_MONITORING_GAP")],
                   [("04:22:00", "UNASSESSABLE", "REQUIRED_TRADE_1M_STALE")]]
    assert all(ids_by_birth(r)[1] is None for r in (b, g))
    assert not [r for r in (e["record"] for e in st.journal if e["kind"] == "scenario") if r["setup"].get("attempt")]


@pytest.mark.parametrize("s", SIDES)
def test_original_expiry_precedes_an_arm_completing_at_h0(s):
    res = run(side(fx.late(4, None), s))
    assert ids_by_birth(res)[1] is None
    assert [(o["env"]["clock_time"][11:19], o["category"], o["values"].get("state")) for o in a2x_obs(res)][-1] == (
        "05:30:00", "REVIEW_CLOSED", "EXPIRED")


# -- time edges -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_failure_exactly_on_a_15m_frontier(s):
    res = run(side(fx.frontier_failure(), s))
    s1, s2 = ids_by_birth(res)
    opened = a2x_obs(res)[0]["values"]
    assert opened["opened_at"] == opened["formation_origin"] == "2025-09-01T04:15:00+00:00"
    assert steps(res, s1)[-1] == ("04:15:00", "TERMINAL", "V_CONTACT", "INVALIDATED")
    assert steps(res, s2)[0][:2] == ("04:30:00", "ARM")  # the bar starting at tf is fully post-failure
    assert [r for r in scen(res) if r["scenario_id"] == s2][0]["anchor_source"].endswith("/15m/2025-09-01T04:15:00+00:00")


@pytest.mark.parametrize("s", SIDES)
def test_residual_exactly_30_minutes_confirms(s):
    res = run(side(fx.late(1, (4, 59)), s))
    _, s2 = ids_by_birth(res)
    conf = [r for r in scen(res) if r["scenario_id"] == s2 and r["transition"] == "CONFIRM"]
    assert [(r["confirmed_at"], r["confirmed_deadline"], r["progress_check_at"]) for r in conf] == [
        ("2025-09-01T05:00:00Z", "2025-09-01T05:30:00Z", "2025-09-01T05:15:00Z")]
    assert not [o for o in a2x_obs(res) if o["category"].startswith("RECOVERY_EXCLUDED")]
    ent = [e["record"] for e in res.journal if e["kind"] == "entry_attempt" and e["record"]["scenario_id"] == s2]
    assert ent[0]["transition"] == "WAIT_OPEN" and "TOO_LATE" not in ent[0]["blockers"]


@pytest.mark.parametrize("s", SIDES)
def test_residual_below_30_minutes_is_recorded_not_confirmed(s):
    res = run(side(fx.late(1, (5, 0)), s))
    _, s2 = ids_by_birth(res)
    assert steps(res, s2) == [("04:45:00", "ARM", "SECOND_ATTEMPT_FRESH_POST_FAILURE_REACTION", None),
                              ("05:01:00", "TERMINAL", "SECOND_ATTEMPT_RECOVERY_WITH_INSUFFICIENT_RESIDUAL", "EXPIRED")]
    x = [o for o in a2x_obs(res) if o["category"] == "RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL"]
    assert len(x) == 1
    v = x[0]["values"]
    assert (v["bar_start"], v["bar_end"], v["available_at_dispatch"], v["original_expiry"]) == (
        "2025-09-01T05:00:00+00:00", "2025-09-01T05:01:00+00:00", "2025-09-01T05:01:00+00:00",
        "2025-09-01T05:30:00+00:00")
    assert (D(v["close"]), v["residual_seconds"], v["required_residual_minutes"], v["operational"]) == (
        px("100050.1", s), "1740", "30", "false")
    assert v["successor_id"] == s2 and v["bar"].endswith("@2025-09-01T05:00:00Z")
    assert len(res.calls()) == 1  # only call 1


@pytest.mark.parametrize("s", SIDES)
def test_recovery_available_exactly_at_h0_is_preceded_by_the_timer(s):
    res = run(side(fx.late(3, (5, 29)), s))
    _, s2 = ids_by_birth(res)
    assert steps(res, s2) == [("05:15:00", "ARM", "SECOND_ATTEMPT_FRESH_POST_FAILURE_REACTION", None),
                              ("05:30:00", "OWNER_RELEASE", "ORIGINAL_SETUP_EXPIRY", None),
                              ("05:30:00", "TERMINAL", "ORIGINAL_SETUP_DEADLINE", "EXPIRED")]
    assert not [o for o in a2x_obs(res) if o["category"].startswith("RECOVERY_EXCLUDED")]


# -- reservation, ordinary births and latch ---------------------------------------------------------------------------

AFTER_RELEASE = (102500, 101800, 101300, 101200, 102000, 102800, 103300)


def _trace(method):
    p, after = D(102400), []
    for c in AFTER_RELEASE:
        after += fx.bar15(p, D(c) + 20, min(p, D(c)) - 10, D(c), order="LH")
        p = D(c)
    st = Stepper(fx.reservation_defers_birth(after=after), method=method)
    out = {}
    for h, m in [(4, 15), (5, 0), (5, 15), (5, 30), (5, 45), (6, 0), (7, 15), (7, 30)]:
        st.run_until(T(h, m))
        c = st.core
        out[f"{h}:{m:02d}"] = (c.qa_last["1"], c.latch["1"], c.a_owner["1"] is not None)
    st.finish()
    births = [e["record"]["env"]["clock_time"][11:16] for e in st.journal
              if e["kind"] == "scenario" and e["record"]["transition"] == "BIRTH"]
    return out, births, st


def test_reservation_defers_an_ordinary_birth_then_releases_with_the_ordinary_latch():
    t6, b6, _ = _trace("v0.6")
    tx, bx, st = _trace(X)
    assert b6 == ["03:30", "05:15", "07:30"]  # v0.6: the ordinary same-direction impulse is born at 05:15
    assert bx == ["03:30", "07:30"]  # the variant defers it (policy change), then renews only after false -> true
    assert t6["5:15"] == (True, "NEED_FALSE", True) and tx["5:15"] == (True, "NEED_FALSE", True)
    # during the reservation a Q_A false never readies the latch (no banked false); v0.6 readied it at 04:15
    assert t6["4:15"][1] == "READY" and tx["4:15"] == (False, "NEED_FALSE", True) and tx["5:00"] == (False, "NEED_FALSE", True)
    # release at H0 05:30: Q_A still true but no birth (needs a false observed at/after the release)
    assert tx["5:30"] == (True, "NEED_FALSE", False) and tx["5:45"] == (True, "NEED_FALSE", False)
    assert tx["6:00"] == (False, "READY", False) and tx["7:30"] == (True, "NEED_FALSE", True)
    obs = [(e["record"]["env"]["clock_time"][11:19], e["record"]["category"]) for e in st.journal
           if e["kind"] == "observation" and e["record"]["name"] == "a_second_attempt"]
    assert obs == [("04:02:00", "REVIEW_OPEN"), ("05:15:00", "ORDINARY_BIRTH_DEFERRED"), ("05:30:00", "REVIEW_CLOSED")]
    assert st.core.counters["a2x"]["ordinary_births_deferred"] == 1


# -- routing of the successor's child --------------------------------------------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_successor_routing_keeps_temporary_blockers_and_terminal_endings_distinct(s):
    res = run(side(fx.two_calls(), s))
    _, s2 = ids_by_birth(res)
    ent = [e["record"] for e in res.journal if e["kind"] == "entry_attempt" and e["record"]["scenario_id"] == s2]
    assert [(r["env"]["clock_time"][11:16], r["transition"]) for r in ent] == [
        ("04:31", "WAIT_OPEN"), ("04:32", "BLOCKERS"), ("04:33", "BLOCKERS"), ("04:33", "RESPONSE_REFERENCE"),
        ("04:34", "ISSUE")]
    assert "CLOSE_OUTSIDE_RETURN_CORRIDOR" in ent[1]["blockers"] and ent[2]["blockers"] == []  # temporary: kept waiting
    assert ent[0]["clocks"]["hard_deadline"] == "2025-09-01T05:30:00+00:00"
    c = run(side(fx.successor_child_contradicted(), s))
    _, s2c = ids_by_birth(c)
    ent = [e["record"] for e in c.journal if e["kind"] == "entry_attempt" and e["record"]["scenario_id"] == s2c]
    assert [(r["env"]["clock_time"][11:16], r["transition"], (r["reason"] or "").split(":")[0]) for r in ent][-1] == (
        "04:34", "TERMINAL", "LOCAL_RESPONSE_CONTRADICTED")
    assert len(c.calls()) == 1  # the later valid recovery never reopens the consumed child
    assert steps(c, s2c)[-1] == ("05:00:30", "TERMINAL", "SCENARIO_PROGRESS_BELOW_HALF_SCALE", "STALLED")
    assert [o["category"] for o in a2x_obs(c)] == ["REVIEW_OPEN", "SUCCESSOR_ARMED"]


# -- persistence -----------------------------------------------------------------------------------------------------

def _engine_doc(rt, end):
    cfg, rel = rt.core.cfg, methods.get(X, experimental=True)
    return {"format": rel.engine_format, "adviser": {
        "method": rel.key, "format": rel.runtime_format,
        "identity": rel.composite_identity(cfg.profile, {"instrument": cfg.instrument}, None),
        "profile": cfg.profile.model_dump(mode="json"), "tick": str(cfg.tick), "clock_policy": cfg.clock_policy,
        "eval_start": fx.DAY2.isoformat(), "eval_end": end.isoformat(), "origin": cfg.origin,
        "channels": cfg.channel_ids, "evaluator": rt.ev.identity(), "build": None}}


def _fold(ms, cuts=()):
    evs, cov = build_events(fx.DAY1, ms)
    end = fx.DAY1 + len(ms) * timedelta(minutes=1)
    rt, temporal = make_runtime(eval_start=fx.DAY2, eval_end=end, method=X), temporal_for(cov)
    rt.attach(temporal)
    eng = _engine_doc(rt, end)
    journal, records, cuts, states = [], [], sorted(cuts), {}
    for i, e in enumerate(evs):
        while cuts and e.available_time > cuts[0]:
            j, r = rt.take()
            journal += j
            records += r
            blob, sha = engine.pack_runtime(rt)
            states[cuts[0]] = json.loads(zlib.decompress(blob))
            temporal = te.unpack(*te.pack(temporal))
            rt = engine.unpack_runtime(blob, sha, eng)  # production codec: exact round trip or refusal
            assert canonical(rt.encode()) == zlib.decompress(blob)
            rt.attach(temporal)
            cuts.pop(0)
        temporal.on_event(e, i)
        rt.before_admit(e)
        rt.admit(e, i)
    temporal.finish(end)
    rt.finish(end)
    j, r = rt.take()
    return journal + j, records + r, states


@pytest.mark.parametrize("s", SIDES)
def test_restore_at_every_critical_point_reproduces_the_uninterrupted_run(s):
    ms = side(fx.two_calls(), s)
    # a cut at t + 90 s holds the state right after the dispatch at t (the next minute's events wait admitted)
    cuts = tuple(T(h, m) + timedelta(seconds=90) for h, m in
                 [(4, 3), (4, 4), (4, 20), (4, 30), (4, 31), (4, 32), (4, 33), (4, 34), (5, 10)])
    base_j, base_r, _ = _fold(ms)
    j, r, states = _fold(ms, cuts)
    assert [e["digest"] for e in j] == [e["digest"] for e in base_j]  # no duplicate, no missing record
    assert [x["digest"] for x in r] == [x["digest"] for x in base_r]
    d = "1" if s == "L" else "-1"
    st = {(k - timedelta(seconds=90)).strftime("%H:%M"): v for k, v in states.items()}
    assert st["04:03"]["core"]["a2x"]["reviews"] == []
    rv = st["04:04"]["core"]["a2x"]["reviews"]
    assert len(rv) == 1 and rv[0]["origin"] == "2025-09-01T04:15:00+00:00" and rv[0]["bars"] == 0
    assert st["04:04"]["core"]["v3"]["a_owner"][d]["reserved_for"] == rv[0]["impulse"]
    assert st["04:20"]["core"]["a2x"]["reviews"][0]["bars"] == 0  # the fresh bar is not complete yet
    s2 = [x for x in st["04:30"]["core"]["v3"]["scen"] if x.get("attempt") == 2]
    assert st["04:30"]["core"]["a2x"]["reviews"] == [] and len(s2) == 1 and s2[0]["status"] == "ARMED"
    s2c = [x for x in st["04:31"]["core"]["v3"]["scen"] if x.get("attempt") == 2][0]
    assert (s2c["status"], s2c["conf_deadline"], s2c["progress_at"]) == (
        "CONFIRMED", "2025-09-01T05:30:00+00:00", "2025-09-01T05:00:30+00:00")  # no clock prolonged by restore
    assert st["04:33"]["core"]["v3"]["waits"][0]["phase"] == "WAIT_RESPONSE"
    assert st["05:10"]["core"]["a2x"]["reviews"] == []
    assert sum(1 for e in j if e["kind"] == "call") == 2
    assert sum(1 for e in j if e["kind"] == "observation" and e["record"]["name"] == "a_second_attempt") == 2
    raw6 = None
    with pytest.raises(engine.AdviserStateError):  # a variant state never decodes as v0.6 (no silent continuation)
        eng6 = {"adviser": {**_engine_doc(make_runtime(eval_start=fx.DAY2, method=X), T(8))["adviser"],
                            "method": "v0.6"}}
        raw6 = engine.unpack_runtime(*engine.pack_runtime(make_runtime(eval_start=fx.DAY2, method=X)), eng6)
    assert raw6 is None


@pytest.mark.parametrize("name,terminal", [("confirmed_time_expired", ("TIME_EXPIRED", "CONFIRMED_HARD_DEADLINE")),
                                           ("confirmed_b_and_v_same_minute",
                                            ("UNASSESSABLE", "DESTINATION_AND_INVALIDATION_SAME_INTERVAL"))])
@pytest.mark.parametrize("s", SIDES)
def test_other_confirmed_terminals_never_open_a_review(name, terminal, s):
    """With STALLED, DESTINATION_REACHED, monitoring-gap UNASSESSABLE and child-only terminals covered by the parity
    sweep, these two confirmed terminals complete the exclusions (an A PRICE_PREMISE_FAILED cannot precede a V contact
    on complete data: V = R - z lies above A)."""
    ms = side(getattr(fx, name)(), s)
    r6, rx = run(ms, method="v0.6"), run(ms)
    s1, _ = ids_by_birth(rx)
    last = [r for r in scen(rx) if r["scenario_id"] == s1][-1]
    assert (last["terminal_state"], last["reason"].split(":")[0]) == terminal and last["confirmed_at"]
    assert not a2x_obs(rx)
    kinds = tuple(sorted({e["kind"] for e in r6.journal}))
    assert _norm(rx.journal, kinds) == _norm(r6.journal, kinds)



# -- context gate (1h) and adverse 15m expansion: opening, closing, same-dispatch qualification ------------------------
#
# Hand derivations: ``adviser_a2x_fixtures`` (context / phase section). Every contrary tape has a control differing only
# where the gate is decided (1h: one day-1 bar; 15m: the closes building the expansion), showing what the gate stops.

CTX = {  # cause -> case -> (contrary tape, control tape)
    "1h": {"open": (lambda: fx.ctx_balanced_from_0500(fx.failure_after_0500()), fx.failure_after_0500),
           "close": (lambda: fx.ctx_balanced_from_0500(fx.late(3, (5, 15))), lambda: fx.late(3, (5, 15))),
           "same": (lambda: fx.ctx_balanced_from_0500(fx.late(2, (5, 0))), lambda: fx.late(2, (5, 0)))},
    "15m": {"open": (lambda: fx.frontier_failure_closing(98500), lambda: fx.frontier_failure_closing(99600)),
            "close": (lambda: fx.failure_bar_expansion(98500), lambda: fx.failure_bar_expansion(99400)),
            "same": (lambda: fx.qualifying_bar_with_expansion(99000, 98950),
                     lambda: fx.qualifying_bar_with_expansion(99300, 99250))},
}
CAUSES = ("1h", "15m")


def _gate(reason, cause, s):
    """1h: a non-concordant (BALANCED) context with no 15m EXPANSION; 15m: a concordant context with an EXPANSION
    adverse to the direction."""
    code, rest = reason.split(":", 1)
    ctx, phase = rest.split("/")
    assert code == "CONTEXT_OR_ADVERSE_EXPANSION", reason
    if cause == "1h":
        assert ctx == "BALANCED" and not phase.startswith("EXPANSION"), reason
    else:
        assert (ctx, phase) == (("UP", "EXPANSION:DOWN") if s == "L" else ("DOWN", "EXPANSION:UP")), reason


def _when(res):
    return [(o["env"]["clock_time"][11:19], o["category"], o["values"].get("state")) for o in a2x_obs(res)]


def _hm(x):
    return int(x[:2]), int(x[3:5])


def _ownership(ms, d, times):
    """(Q_A last, latch, discovery owner) of direction ``d`` after the dispatch at each time, v0.6 and the variant
    (read only: nothing is placed in any state)."""
    out = {}
    for method in ("v0.6", X):
        st = Stepper(ms, method=method)
        for h, m in times:
            st.run_until(T(h, m))
            own = st.core.a_owner[d]
            out[(method, f"{h:02d}:{m:02d}")] = (st.core.qa_last[d], st.core.latch[d], own and own["sid"])
        st.finish()
    return out


def _released_like_v06(ms, s, s1, during, at):
    """During the review the slot is reserved (latch NEED_FALSE: no banked false); at the closing dispatch it is
    released and the ordinary latch reads the false Q_A observed after the release (READY), exactly as v0.6 by then."""
    d = "1" if s == "L" else "-1"
    own = _ownership(ms, d, [during, at])
    dt, at_ = f"{during[0]:02d}:{during[1]:02d}", f"{at[0]:02d}:{at[1]:02d}"
    assert own[(X, dt)] == (False, "NEED_FALSE", f"{s1}#review")
    assert own[(X, at_)] == (False, "READY", None) == own[("v0.6", at_)]


@pytest.mark.parametrize("cause", CAUSES)
@pytest.mark.parametrize("s", SIDES)
def test_a_contrary_gate_at_the_failure_never_opens_a_review(cause, s):
    bad, ctl = CTX[cause]["open"]
    ms = side(bad(), s)
    r6, rx = run(ms, method="v0.6"), run(ms)
    tf = {"1h": "05:05:00", "15m": "04:45:00"}[cause]
    s1, s2 = ids_by_birth(rx)
    assert steps(rx, s1)[-1] == (tf, "TERMINAL", "V_CONTACT", "INVALIDATED") and s2 is None
    o = a2x_obs(rx)
    assert _when(rx) == [(tf, "REVIEW_NOT_OPENED", None)]
    assert o[0]["values"]["impulse_id"] == s1 and o[0]["values"]["original_expiry"] == "2025-09-01T05:30:00+00:00"
    _gate(o[0]["values"]["reason"], cause, s)
    # otherwise exactly v0.6 (owner released at tf, ordinary latch), including every later record
    kinds = tuple(sorted({e["kind"] for e in r6.journal}))
    strip = [e for e in rx.journal if not (e["kind"] == "observation" and e["record"]["name"] == "a_second_attempt")]
    assert _norm(strip, kinds) == _norm(r6.journal, kinds)
    # a later close beyond the old K (100049.9) before H0 reopens nothing and never re-confirms S1
    k_old = px("100049.9", s)
    later = ms[index_of(T(*_hm(tf))):index_of(T(5, 30))]
    assert any((m.c > k_old if s == "L" else m.c < k_old) for m in later)
    assert [x[1] for x in steps(rx, s1)].count("CONFIRM") == 1
    # control: the same failure with the gate concordant opens the review
    assert _when(run(side(ctl(), s)))[0] == (tf, "REVIEW_OPEN", None)


@pytest.mark.parametrize("cause", CAUSES)
@pytest.mark.parametrize("s", SIDES)
def test_an_open_review_ends_when_the_gate_turns_contrary(cause, s):
    """1h: the review opened at 04:04 waits on quiet bars; the 1h close at 05:00 turns the context BALANCED while the
    bar [04:45,05:00) does not qualify. 15m: the review opened at 04:41; the failure bar [04:30,04:45) (never a new fact)
    completes an adverse EXPANSION at 04:45. Then a fresh contrary reaction and its recovery follow (at 05:15 the 15m
    gate is concordant again): nothing reopens."""
    bad, ctl = CTX[cause]["close"]
    ms = side(bad(), s)
    rx = run(ms)
    s1, s2 = ids_by_birth(rx)
    opened, closed, bars = {"1h": ("04:04:00", "05:00:00", "2"), "15m": ("04:41:00", "04:45:00", "0")}[cause]
    assert _when(rx) == [(opened, "REVIEW_OPEN", None), (closed, "REVIEW_CLOSED", "WITHDRAWN")]
    v = a2x_obs(rx)[1]["values"]
    _gate(v["reason"], cause, s)
    assert (v["new_bars"], v["contrary_close_seen"], v["impulse_id"]) == (bars, "false", s1)
    assert s2 is None and not [r for r in scen(rx) if r["setup"].get("attempt")]
    assert len(rx.calls()) == 1
    # release and ordinary latch at the closing dispatch
    _released_like_v06(ms, s, s1, _hm(opened), _hm(closed))
    # after the release the ordinary records (scenarios, children, calls) are exactly v0.6's
    r6 = run(ms, method="v0.6")
    k = ("scenario", "entry_attempt", "call", "call_revision")
    cut = f"2025-09-01T{closed}Z"
    assert [x for x in _norm([e for e in rx.journal if e["kind"] in k], k) if x[1] > cut] == \
        [x for x in _norm([e for e in r6.journal if e["kind"] in k], k) if x[1] > cut]
    # control: with the gate concordant the same later reaction arms the successor at 05:15 (its recovery at 05:16 has
    # 14 minutes left: recorded, excluded); in the contrary tape it arms nothing
    assert _when(run(side(ctl(), s))) == [(opened, "REVIEW_OPEN", None), ("05:15:00", "SUCCESSOR_ARMED", None),
                                          ("05:16:00", "RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL", None)]
    if cause == "15m":  # the reaction completing at 05:15 meets a concordant gate again: still no reopening
        st = Stepper(ms, method=X)
        st.run_until(T(5, 15))
        assert st.core.context(T(5, 15)) == ("UP" if s == "L" else "DOWN") and st.core.phase_now(T(5, 15)) != "EXPANSION"
        st.finish()


@pytest.mark.parametrize("cause", CAUSES)
@pytest.mark.parametrize("s", SIDES)
def test_a_bar_qualifying_in_the_dispatch_where_the_gate_turns_contrary_arms_nothing(cause, s):
    """1h: [04:45,05:00) (h 100050, l 99650, c 99750: contrary, R2 < R1) qualifies at 05:00, the dispatch whose 1h close
    turns the context BALANCED. 15m: [04:30,04:45) (l 98950, c 99000 < the previous new close) qualifies at 04:45, the
    dispatch completing an adverse EXPANSION. The gate is applied first (design §6): WITHDRAWN, no successor; the bar is
    not even counted (the closing values still describe the earlier bars)."""
    bad, ctl = CTX[cause]["same"]
    ms = side(bad(), s)
    rx = run(ms)
    s1, s2 = ids_by_birth(rx)
    t, bars, low = {"1h": ("05:00:00", "2", 99930), "15m": ("04:45:00", "1", 99300)}[cause]
    assert _when(rx) == [("04:04:00", "REVIEW_OPEN", None), (t, "REVIEW_CLOSED", "WITHDRAWN")]
    v = a2x_obs(rx)[1]["values"]
    _gate(v["reason"], cause, s)
    assert (v["new_bars"], v["contrary_close_seen"], D(v["new_reaction_low"])) == (bars, "false", px(low, s))
    assert s2 is None and len(rx.calls()) == 1
    assert not [r for r in scen(rx) if r["env"]["clock_time"] >= f"2025-09-01T{t}Z" and r["transition"] in ("ARM", "CONFIRM")]
    _released_like_v06(ms, s, s1, (4, 30), _hm(t))
    # control: the same bar with the gate concordant arms the successor in that dispatch
    c = run(side(ctl(), s))
    _, c2 = ids_by_birth(c)
    arm = [r for r in scen(c) if r["scenario_id"] == c2][0]
    k2, r2 = {"1h": (100050, 99650), "15m": (99470, 99250)}[cause]
    assert (arm["env"]["clock_time"][11:19], arm["transition"], D(arm["trigger_level"]), D(arm["reaction_level"])) == (
        t, "ARM", px(k2, s), px(r2, s))


@pytest.mark.parametrize("cause,case,cuts,before,after", [
    ("1h", "same", ((4, 45), (4, 59), (5, 0)), "04:59", "05:00"),
    ("15m", "close", ((4, 41), (4, 44), (4, 45)), "04:44", "04:45")])
@pytest.mark.parametrize("s", SIDES)
def test_restore_before_the_gate_change_reproduces_the_uninterrupted_run(cause, case, cuts, before, after, s):
    ms = side(CTX[cause][case][0](), s)
    base_j, base_r, _ = _fold(ms)
    j, r, states = _fold(ms, tuple(T(h, m) + timedelta(seconds=90) for h, m in cuts))
    assert [e["digest"] for e in j] == [e["digest"] for e in base_j]  # no duplicate, no missing record
    assert [x["digest"] for x in r] == [x["digest"] for x in base_r]
    d = "1" if s == "L" else "-1"
    st = {(k - timedelta(seconds=90)).strftime("%H:%M"): v for k, v in states.items()}
    rv = st[before]["core"]["a2x"]["reviews"]
    assert len(rv) == 1 and rv[0]["bars"] == {"1h": 2, "15m": 0}[cause] and not rv[0]["contrary"]
    assert st[before]["core"]["v3"]["a_owner"][d]["reserved_for"] == rv[0]["impulse"]
    assert st[before]["core"]["latch"][d] == "NEED_FALSE"
    assert st[after]["core"]["a2x"]["reviews"] == [] and st[after]["core"]["v3"]["a_owner"][d] is None
    assert st[after]["core"]["latch"][d] == "READY"
    obs = [e["record"] for e in j if e["kind"] == "observation" and e["record"]["name"] == "a_second_attempt"]
    assert [(o["env"]["clock_time"][11:16], o["category"], o["values"].get("state")) for o in obs][-1] == (
        after, "REVIEW_CLOSED", "WITHDRAWN")
    assert not [e for e in j if e["kind"] == "scenario" and e["record"]["setup"].get("attempt")]



# -- experimental record registration (``method/A2X-EXPERIMENTAL-RECORDS.json``): additive, not a release ------------

REG = json.loads((methods.idn.METHOD_DIR / "A2X-EXPERIMENTAL-RECORDS.json").read_text(encoding="utf-8"))
ADDED_SETUP = set(REG["scenario"]["setup_keys_added"])
SWEEP = {  # every variant tape of this module (LONG and SHORT); the staleness tape is added in ``_sweep``
    "two_calls": fx.two_calls, "no_call_failure": fx.no_call_failure, "no_fresh_facts": fx.no_fresh_facts,
    "premise_before_arm": fx.premise_before_arm, "premise_in_failure_dispatch": fx.premise_in_failure_dispatch,
    "frontier_failure": fx.frontier_failure, "destination_in_review": fx.destination_in_review,
    "gap_in_review": fx.gap_in_review, "third_attempt_refused": fx.third_attempt_refused,
    "successor_child_contradicted": fx.successor_child_contradicted,
    "reservation_defers_birth": fx.reservation_defers_birth, "old_recovery_before_arm": fx.old_recovery_before_arm,
    "late_excluded": lambda: fx.late(1, (5, 0)), "late_30": lambda: fx.late(1, (4, 59)),
    "late_h0": lambda: fx.late(3, (5, 29)), "late_none": lambda: fx.late(4, None),
    **{f"{cause}_{case}_{k}": CTX[cause][case][i] for cause in CAUSES for case in CTX[cause]
       for i, k in enumerate(("contrary", "control"))},
}


@functools.cache
def _sweep() -> tuple:
    out = []
    for name in sorted(SWEEP):
        for s in SIDES:
            out.append((f"{name}/{s}", run(side(SWEEP[name](), s)).journal))
    for s in SIDES:
        ms = side(fx.two_calls(), s)
        st = Stepper(ms, method=X, events=delayed_events(ms, {index_of(T(4, 20 + k)): 270 - 60 * k for k in range(5)}))
        st.finish()
        out.append((f"stale/{s}", st.journal))
    return tuple(out)


def _role_ids(journal):
    """first-attempt ids, successor ids (from the scenario records themselves)."""
    a = [e["record"] for e in journal if e["kind"] == "scenario" and e["record"]["family"] == "A"]
    return ({r["scenario_id"] for r in a if "attempt" not in r["setup"]},
            {r["scenario_id"] for r in a if r["setup"].get("attempt") == "2"})


def test_record_registration_is_additive_experimental_and_outside_every_identity():
    vx = methods.get(X, experimental=True)
    assert REG["status"] == "EXPERIMENTAL_NOT_PUBLIC_NOT_A_SEMANTIC_V2_REVISION"
    assert REG["variant"] == {"key": vx.key, "model": vx.model, "rules_version": vx.rules_version,
                              "implementation": vx.implementation, "core_state_format": vx.core_state_format,
                              "runtime_format": vx.runtime_format, "engine_format": vx.engine_format}
    # the public semantic.v2 contract, its changelog, the emitted-revision map and the baseline are unchanged
    assert REG["base_contract"]["revision"] == sc.SEMANTIC_V2_REVISION == 5 and len(sc.SEMANTIC_V2_CHANGELOG) == 5
    assert vx.model not in sc.SEMANTIC_V2_EMITTED_REVISION and sc.KIND_CONTRACTS_V6 == sc.KIND_CONTRACTS_V5
    baseline = (methods.idn.METHOD_DIR.parents[3] / "schemas/algotrader.semantic.v2.json").read_text(encoding="utf-8")
    assert not any(w in baseline for w in ("a_second_attempt", "SECOND_ATTEMPT", "ORIGINAL_IMPULSE_EXPIRY", "a2x"))
    # not part of the variant's rules manifest or register: v0.6 and the variant keep their 048bf2d identities
    assert "A2X-EXPERIMENTAL-RECORDS.json" not in {m["file"] for m in vx.rules_manifest()}
    assert vx.register_file.name != "A2X-EXPERIMENTAL-RECORDS.json"
    assert vx.rules_sha256() == "08e3c2689c3ed6d02bc4eba28c539dc94a55cf29d7515db1562d1d9f8f9474e7"
    assert vx.register_sha256() == "b4782f7da3e64227cc50dbb2aa7beb16a0c017c3c4d2e8277a215b8cfd7a1126"
    # the code constants are the registered values
    ob = REG["observation"]
    assert (a2x.OBS_NAME, ob["kind"], ob["lens"], ob["decision_role"]) == (
        ob["name"], "observation", "structure", "A_SECOND_ATTEMPT_RESERVATION")
    assert a2x.ARM_REASON == REG["scenario"]["arm_reason"]
    assert set(REG["scenario"]["terminal_reasons_added"]) == {a2x.EXCLUDED_REASON}
    assert set(REG["call"]["hard_deadline_origin_added"]) == {a2x.HARD_ORIGIN}
    assert set(a2x._new_counters()) >= {"reviews_opened", "successors_armed"}  # counters are state, not records


def test_every_emitted_variant_value_is_registered_and_the_coverage_is_declared():
    ob = REG["observation"]
    covered = set()
    for name, journal in _sweep():
        firsts, successors = _role_ids(journal)
        for e in journal:
            r, kind = e["record"], e["kind"]
            ids = [r.get("scenario_id"), r.get("call_id"), r.get("entry_attempt_id"), e["subject"], *r["env"]["lineage"]]
            assert not any(x and "#review" in x for x in ids), (name, kind)  # the reservation is never a record id
            if kind == "observation" and r["name"] == ob["name"]:
                cat, v = r["category"], r["values"]
                spec = ob["categories"][cat]
                keys = [k for x in spec["values"] for k in (ob["review_values"] if x == "review_values" else [x])]
                assert sorted(v) == sorted(keys), (name, cat)
                assert all(x is None or isinstance(x, str) for x in v.values())
                assert (r["lens"], r["decision_role"]) == (ob["lens"], ob["decision_role"])
                assert list(r["env"]["lineage"]) == [v[k] for k in spec["lineage"]] and e["subject"] == v[spec["lineage"][0]]
                assert v["impulse_id"] in firsts and ("successor_id" not in v or v["successor_id"] in successors)
                assert r["env"]["event_start"] is None and r["env"]["known_at"] == r["env"]["clock_time"]
                if cat == "REVIEW_NOT_OPENED":
                    assert v["reason"].split(":")[0] in spec["reasons"]
                    covered.add(f"{cat}:{v['reason'].split(':')[0]}")
                elif cat == "REVIEW_CLOSED":
                    assert v["reason"].split(":")[0] in spec["states"][v["state"]], (name, v["state"], v["reason"])
                    covered.add(f"{cat}:{v['state']}:{v['reason'].split(':')[0]}")
                elif cat == "RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL":
                    assert (v["reason"], v["operational"]) == ("INSUFFICIENT_RESIDUAL", "false")
                    covered.add(f"{cat}:{v['reason']}")
                else:
                    covered.add(cat)
                if cat == "ORDINARY_BIRTH_DEFERRED":
                    assert v["reserved_by"] in {f"{v['impulse_id']}#review"} | successors
            elif kind == "scenario" and r["family"] == "A":
                st, reason = r["setup"], (r["reason"] or "")
                if r["scenario_id"] in successors:
                    assert st["attempt"] == "2" and st["renewal"] == "SECOND_ATTEMPT"
                    assert st["impulse_id"] == st["parent_scenario_id"] in firsts
                    assert list(r["env"]["lineage"]) == [r["scenario_id"], st["impulse_id"]]
                    assert r["original_expiry"] == r["confirmed_deadline"] or r["confirmed_deadline"] is None
                    if reason.startswith("SECOND_ATTEMPT"):
                        assert reason == a2x.ARM_REASON and r["transition"] == "ARM" or (
                            reason.split(":")[0] in REG["scenario"]["terminal_reasons_added"]
                            and r["terminal_state"] == "EXPIRED")
                else:
                    assert not ADDED_SETUP & set(st) and st["renewal"] != "SECOND_ATTEMPT"
                    assert not reason.startswith("SECOND_ATTEMPT")
            elif kind == "call":
                succ = r["scenario_id"] in successors
                assert (r["hard_deadline_origin"] == a2x.HARD_ORIGIN) == succ
                assert list(r["env"]["lineage"]) == [f"{r['scenario_id']}#entry", r["scenario_id"]]
    assert sorted(covered) == sorted(REG["synthetic_coverage"]["exercised"])  # declared coverage, nothing more
    every = {f"REVIEW_NOT_OPENED:{k}" for k in ob["categories"]["REVIEW_NOT_OPENED"]["reasons"]} | {
        f"REVIEW_CLOSED:{s}:{k}" for s, ks in ob["categories"]["REVIEW_CLOSED"]["states"].items() for k in ks}
    assert covered - {"REVIEW_OPEN", "SUCCESSOR_ARMED", "ORDINARY_BIRTH_DEFERRED",
                      "RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL:INSUFFICIENT_RESIDUAL"} <= every


def test_variant_records_serialize_exactly_through_the_revision_5_contracts():
    seen = {"observation": 0, "scenario": 0, "entry_attempt": 0, "call": 0, "call_revision": 0}
    for name, journal in _sweep():
        _, successors = _role_ids(journal)
        calls = {e["record"]["call_id"] for e in journal if e["kind"] == "call" and e["record"]["scenario_id"] in successors}
        for e in journal:
            r, kind = e["record"], e["kind"]
            mine = (kind == "observation" and r["name"] == a2x.OBS_NAME) or r.get("scenario_id") in successors or (
                kind == "call_revision" and r["call_id"] in calls)
            if not mine:
                continue
            model = sc.KIND_CONTRACTS_V6[kind].model_validate(r)
            assert json.loads(model.model_dump_json()) == r, (name, kind)  # exact round trip, no extra/missing field
            assert hashlib.sha256(canonical(r)).hexdigest() == e["digest"]  # the journal digest of the same bytes
            seen[kind] = seen.get(kind, 0) + 1
    assert all(seen[k] for k in ("observation", "scenario", "entry_attempt", "call")), seen


@pytest.mark.parametrize("s", SIDES)
def test_first_attempt_reservation_and_successor_are_distinct_in_records_and_state(s):
    ms = side(fx.two_calls(), s)
    res = run(ms)
    s1, s2 = ids_by_birth(res)
    r1 = [r for r in scen(res) if r["scenario_id"] == s1]
    r2 = [r for r in scen(res) if r["scenario_id"] == s2]
    # first attempt: the v0.6 vocabulary only; its terminal still states the v0.6 release
    assert all(not ADDED_SETUP & set(r["setup"]) and list(r["env"]["lineage"]) == [s1] for r in r1)
    assert r1[-1]["transition"] == "TERMINAL" and r1[-1]["discovery_owner"] == "RELEASED"
    # reservation: an observation in the same dispatch, linked to the impulse only; a state token, never a record id
    rv = a2x_obs(res)[0]
    assert (rv["category"], rv["env"]["clock_time"], list(rv["env"]["lineage"])) == (
        "REVIEW_OPEN", r1[-1]["env"]["clock_time"], [s1])
    st = Stepper(ms, method=X)
    st.run_until(T(4, 20))
    d = "1" if s == "L" else "-1"
    assert st.core.a_owner[d] == {"sid": f"{s1}#review", "expires": "2025-09-01T05:30:00+00:00", "reserved_for": s1}
    doc = st.core.encode()  # state codec of the reservation: exact round trip
    assert canonical(type(st.core).decode(json.loads(canonical(doc)), st.core.cfg).encode()) == canonical(doc)
    st.run_until(T(4, 31))
    doc = st.core.encode()  # and of the confirmed successor (attempt lineage and frozen R1 kept)
    sx = [x for x in doc["v3"]["scen"] if x["sid"] == s2][0]
    assert (sx["attempt"], sx["impulse"], sx["status"], D(sx["failed_r1_t"]) * int(d)) == (2, s1, "CONFIRMED", px(99900, s))
    assert canonical(type(st.core).decode(json.loads(canonical(doc)), st.core.cfg).encode()) == canonical(doc)
    st.finish()
    # successor: its own id, attempt "2", lineage (successor, impulse), its own child and call with the H0 origin
    assert s2 != s1 and s2.startswith(f"A{s}-2025-09-01T04:15:00+00:00-")
    assert all(r["setup"]["attempt"] == "2" and list(r["env"]["lineage"]) == [s2, s1] for r in r2)
    c1, c2 = res.calls()
    assert (c1["scenario_id"], c1["hard_deadline_origin"]) == (s1, "STRUCTURAL_CONFIRMATION_PUBLICATION")
    assert (c2["scenario_id"], c2["hard_deadline_origin"]) == (s2, "ORIGINAL_IMPULSE_EXPIRY")
    assert list(c2["env"]["lineage"]) == [f"{s2}#entry", s2]
    ent = [e["record"] for e in res.journal if e["kind"] == "entry_attempt" and e["record"]["scenario_id"] == s2]
    assert ent and all(list(x["env"]["lineage"]) == [f"{s2}#entry", s2] for x in ent)
