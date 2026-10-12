"""EXPERIMENTAL v0.6-a2x second attempt (``delivery/A-SECOND-ATTEMPT-DESIGN.md``, design b20919e, ratification
3705fd0): synthetic proofs only, through the ordinary pure kernel order (cold day-1 history -> warmup, readiness,
context, scale; no scenario, anchor or call placed in any state). Expected levels and times are written by hand from
the tape constants in ``adviser_a2x_fixtures`` (LONG); SHORT runs are the reflection x -> 200000 - x.
"""

from __future__ import annotations

import json
import zlib
from datetime import timedelta
from decimal import Decimal

import adviser_a2x_fixtures as fx
import pytest
from adviser3_fixtures import Stepper, T, delayed_events, index_of
from test_mp004_versions import _norm  # id-token normalization shared with the v0.5/v0.6 parity tests
from test_mp005_paths import PARITY

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
