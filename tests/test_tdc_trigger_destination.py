"""EXPERIMENTAL v0.6-tdc trigger/destination compatibility (``delivery/A-TRIGGER-DESTINATION-CORRECTION.md``; Director
review ``delivery/A-TRIGGER-DESTINATION-SEMANTIC-REVIEW.md``): synthetic proofs through the ordinary pure kernel order
(cold day-1 history; no scenario, anchor or call placed in any state, except the one explicitly labelled white-box
supplement at the end). Expected levels and times are written by hand from ``adviser_tdc_fixtures`` (LONG); SHORT runs
are the reflection x -> 200000 - x.
"""

from __future__ import annotations

import functools
import json
import zlib
from datetime import timedelta
from decimal import Decimal

import adviser_tdc_fixtures as fx
import pytest
from test_mp004_versions import _ids, _norm, _sub
from test_mp005_paths import PARITY

from algotrader.adviser import engine, methods
from algotrader.adviser.core_tdc import AdviserCoreTDC
from algotrader.adviser.harness import build_events, make_runtime, run_pure, temporal_for
from algotrader.feed.ordering import canonical
from algotrader.temporal import engine as te

X = "v0.6-tdc"
SIDES = ("L", "S")
D = Decimal
INCOMPATIBLE = "current recovery condition incompatible with its destination"
OPERATIONAL = ("entry_attempt", "call", "call_revision", "material_change", "landmark", "observation", "candidate")


def run(ms, method=X):
    return run_pure(fx.DAY1, ms, method=method, eval_start=fx.DAY2)


def side(ms, s):
    return ms if s == "L" else fx.short(ms)


def px(x, s):
    return D(str(x)) if s == "L" else 200000 - D(str(x))


def scen(res, sid=None):
    return [e["record"] for e in res.journal if e["kind"] == "scenario" and (sid is None or e["record"]["scenario_id"] == sid)]


def views(res):
    return [e["record"] for e in res.journal if e["kind"] == "market_view"]


def view_at(res, hm):
    """The view in force after the dispatch at ``hm`` (latest published at or before it)."""
    t = f"2025-09-01T{hm}:00Z"
    return [v for v in views(res) if v["env"]["clock_time"] <= t][-1]


def a_sid(res, born="03:30"):
    return next(r["scenario_id"] for r in scen(res) if r["transition"] == "BIRTH" and r["family"] == "A"
                and r["env"]["clock_time"][11:16] == born)


# -- identity and isolation -------------------------------------------------------------------------------------------

def test_variant_identity_is_separate_explicit_not_selectable_and_contains_no_a2x():
    v6, vx = methods.get("v0.6"), methods.get(X, experimental=True)
    with pytest.raises(methods.UnknownMethod):
        methods.get(X)  # every application path calls get() without the flag
    assert X not in methods.RELEASES and X not in {m["method"] for m in methods.selectable()}
    assert methods.DEFAULT == "v0.2" and set(methods.RELEASES) == {"v0.2", "v0.3", "v0.4", "v0.5", "v0.6", "v0.7"}
    for f in ("model", "rules_version", "implementation", "core_state_format", "runtime_format", "engine_format"):
        assert getattr(vx, f) != getattr(v6, f), f
    # the frozen v0.6 identity is unchanged (references registered for the A v0.6 studies)
    assert v6.rules_sha256() == "57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66"
    assert v6.register_sha256() == "98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda"
    root = methods.idn.METHOD_DIR
    for name in ("A-TRIGGER-DESTINATION-CORRECTION.md", "A-TRIGGER-DESTINATION-SEMANTIC-REVIEW.md"):
        assert (root / name).read_bytes().replace(b"\r\n", b"\n") == \
            (root.parents[3] / "delivery" / name).read_bytes().replace(b"\r\n", b"\n")
    files = [m["file"] for m in vx.rules_manifest()]
    assert files[:3] == ["A-TRIGGER-DESTINATION-CORRECTION.md", "A-TRIGGER-DESTINATION-SEMANTIC-REVIEW.md",
                         "MP-005-V06-INITIAL-RESPONSE-INCOMPATIBILITY.md"]
    assert "A-SECOND-ATTEMPT-DESIGN.md" not in files  # no a2x content
    p6, pxx = methods.get("v0.6").params(), vx.params()
    assert {k: v for k, v in p6.__dict__.items() if k != "raw"} == {k: v for k, v in pxx.__dict__.items() if k != "raw"}
    r6, rx = v6.register(), vx.register()
    assert {k for k in rx if rx[k] != r6.get(k)} == {"model", "status", "rules_version", "identity",
                                                     "trigger_destination_compatibility"}
    core = make_runtime(eval_start=fx.DAY2, method=X).core
    assert type(core) is AdviserCoreTDC and "AdviserCoreA2X" not in [c.__name__ for c in type(core).__mro__]


# -- the criterion at the tick borders (LONG and SHORT) ---------------------------------------------------------------

@pytest.mark.parametrize("h,compatible", [(fx.H_BEFORE, True), (fx.H_AT, False), (fx.H_BEYOND, False)])
@pytest.mark.parametrize("s", SIDES)
def test_first_arm_at_the_tick_borders_publication_and_market_view(h, compatible, s):
    ms = side(fx.hold(h), s)
    rx, r6 = run(ms), run(ms, "v0.6")
    sid = a_sid(rx)
    arm = next(r for r in scen(rx, sid) if r["transition"] == "ARM")
    arm6 = next(r for r in scen(r6, a_sid(r6)) if r["transition"] == "ARM")
    thr = px(D(str(h)) + D("0.1"), s)  # hand-derived effective threshold
    assert (arm["env"]["clock_time"][11:16], D(arm["trigger_level"]), D(arm["destination"])) == ("03:45", px(h, s), px(fx.B, s))
    v, v6 = view_at(rx, "03:45"), view_at(r6, "03:45")
    assert (v6["table_row"], v6["expected_direction"], v6["principal"]["scenario_id"][:2]) == (
        "CONDITIONAL_SCENARIO", "UP" if s == "L" else "DOWN", "AL" if s == "L" else "AS")
    if compatible:
        assert arm["antecedent"] == arm6["antecedent"] and INCOMPATIBLE not in arm["antecedent"]
        assert (v["table_row"], v["expected_direction"], v["principal"]["scenario_id"]) == (
            "CONDITIONAL_SCENARIO", "UP" if s == "L" else "DOWN", sid)
    else:
        assert arm["antecedent"].startswith(INCOMPATIBLE)
        assert f"close {'>=' if s == 'L' else '<='} {thr} is at or beyond the destination {px(fx.B, s)}" in arm["antecedent"]
        assert "confirms continuation" in arm6["antecedent"]  # the v0.6 sentence the review found contradictory
        assert (v["table_row"], v["expected_direction"], v["principal"], v["alternatives"]) == (
            "WATCH_ONLY", "UNCERTAIN", None, [])
        assert [(w["scenario_id"], w["status"]) for w in v["watch"]] == [(sid, "ARMED")]
        assert f"A {'LONG' if s == 'L' else 'SHORT'} armed, not counted as directional support: {arm['antecedent']}" in v["reasons"]
    # the incompatibility persists until the scenario's terminal: every view of its life says the same
    life = [x for x in views(rx) if "03:45" <= x["env"]["clock_time"][11:16] < "05:30"]
    assert life and all((x["principal"] is None) != compatible for x in life)
    # terminal identical: EXPIRED at the original expiry 05:30 in both policies
    assert [(r["transition"], r["terminal_state"]) for r in scen(rx, sid)][-1] == ("TERMINAL", "EXPIRED")
    assert [r["env"]["clock_time"] for r in scen(rx, sid)] == [r["env"]["clock_time"] for r in scen(r6, a_sid(r6))]


@pytest.mark.parametrize("s", SIDES)
def test_the_criterion_function_is_exact_on_the_tick_grid(s):
    """Tq < Bq strict, Decimal, with the effective tick and trigger ticks of the core (no rounding)."""
    for h, expect in ((fx.H_BEFORE, False), (fx.H_AT, True), (fx.H_BEYOND, True)):
        st = __import__("adviser3_fixtures").Stepper(side(fx.hold(h), s), method=X)
        st.run_until(fx.T(3, 45))
        c = st.core
        sc_ = next(x for x in c.scen.values() if x.family == "A")
        assert c.tick == D("0.1") and c.p.trigger_ticks == 1
        assert c.trigger_reaches_destination(sc_) is expect, (h, s)
        st.finish()


# -- no retroactive confirmation; terminals preserved -----------------------------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_reaching_the_threshold_contacts_the_destination_first_and_never_confirms(s):
    for h, confirms in ((fx.H_AT, False), (fx.H_BEFORE, True)):
        ms = side(fx.reach_threshold(h), s)
        rx, r6 = run(ms), run(ms, "v0.6")
        steps = [(r["env"]["clock_time"][11:16], r["transition"], r["terminal_state"]) for r in scen(rx, a_sid(rx))]
        steps6 = [(r["env"]["clock_time"][11:16], r["transition"], r["terminal_state"]) for r in scen(r6, a_sid(r6))]
        assert steps == steps6
        if confirms:  # T = B - tick: the close 100899.9 < B confirms at 04:01 (both policies)
            assert ("04:01", "CONFIRM", None) in steps
        else:  # T = B: the minute closing at T has high = B -> DESTINATION_REACHED at 04:01, never a CONFIRM
            assert steps[-1] == ("04:01", "TERMINAL", "DESTINATION_REACHED")
            assert "CONFIRM" not in [x[1] for x in steps]
            assert all(r["antecedent"].startswith(INCOMPATIBLE) for r in scen(rx, a_sid(rx)) if r["transition"] != "BIRTH")


# -- revision restores support only from its own publication ------------------------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_a_revision_that_makes_the_condition_compatible_restores_support_only_from_its_publication(s):
    ms = side(fx.revision_restores(), s)
    rx, r6 = run(ms), run(ms, "v0.6")
    sid = a_sid(rx)
    recs = scen(rx, sid)
    arm, rev, conf = recs[1], recs[2], recs[3]
    assert (arm["transition"], rev["transition"], conf["transition"]) == ("ARM", "REVISE", "CONFIRM")
    assert arm["antecedent"].startswith(INCOMPATIBLE) and D(arm["trigger_level"]) == px(100900, s)
    assert not rev["antecedent"].startswith(INCOMPATIBLE) and D(rev["trigger_level"]) == px("100049.9", s)
    # the earlier ARM record is never rewritten: the same record (digest) as published at 03:45
    j_arm = [e for e in rx.journal if e["kind"] == "scenario" and e["record"]["transition"] == "ARM"][0]
    assert j_arm["record"]["antecedent"].startswith(INCOMPATIBLE)
    assert view_at(rx, "03:59")["principal"] is None  # no support between the ARM and the REVISE publication
    v = view_at(rx, "04:00")
    assert v["env"]["clock_time"] == "2025-09-01T04:00:00Z" and v["principal"]["scenario_id"] == sid
    assert v["expected_direction"] == ("UP" if s == "L" else "DOWN")
    # confirmation, child and call exactly v0.6 (the restored support never touched the operational path)
    assert (conf["env"]["clock_time"], conf["confirmed_at"]) == ("2025-09-01T04:01:00Z", "2025-09-01T04:01:00Z")
    k = ("entry_attempt", "call", "call_revision")
    assert _norm(rx.journal, k) == _norm(r6.journal, k) and len(rx.calls()) == 1


# -- another valid scenario: the incompatible one never forces the reading ---------------------------------------------

@pytest.mark.parametrize("s", SIDES)
def test_a_valid_scenario_keeps_supporting_while_an_incompatible_one_is_excluded(s):
    ms = side(fx.valid_and_incompatible(), s)
    rx, r6 = run(ms), run(ms, "v0.6")
    s1, s2 = a_sid(rx), a_sid(rx, "07:30")
    arm2 = next(r for r in scen(rx, s2) if r["transition"] == "ARM")
    assert (arm2["env"]["clock_time"][11:16], D(arm2["trigger_level"]), D(arm2["destination"])) == (
        "07:45", px(101460, s), px(101460, s))  # K2 = B2: T2 = B2 + tick
    assert arm2["antecedent"].startswith(INCOMPATIBLE)
    up = "UP" if s == "L" else "DOWN"
    v, v6 = view_at(rx, "07:45"), view_at(r6, "07:45")
    # with the valid confirmed S1: the same directional reading; S2 is no longer an alternative, it is a hypothesis
    assert (v["table_row"], v["expected_direction"], v["principal"]["scenario_id"]) == ("CONDITIONAL_SCENARIO", up, s1)
    assert (v6["table_row"], v6["expected_direction"], v6["principal"]["scenario_id"][:2]) == (
        "CONDITIONAL_SCENARIO", up, s1[:2])
    assert [a["scenario_id"].rsplit("-", 1)[0] for a in v6["alternatives"]] == [s2.rsplit("-", 1)[0]]  # ids hash rules
    assert v["alternatives"] == [] and [(w["scenario_id"], w["status"]) for w in v["watch"]] == [(s2, "ARMED")]
    # after S1's terminal (08:01) only the impossible S2 remains: v0.6 reads it as a directional expectation
    v, v6 = view_at(rx, "08:01"), view_at(r6, "08:01")
    assert (v6["table_row"], v6["expected_direction"]) == ("CONDITIONAL_SCENARIO", up)
    assert (v["table_row"], v["expected_direction"], v["principal"]) == ("WATCH_ONLY", "UNCERTAIN", None)
    assert len(rx.calls()) == len(r6.calls()) == 1  # S1's call, identical (operational parity below)


# -- the WATCH_ONLY reason never claims WATCH-only states when an incompatible ARMED scenario is among them -----------

OBSERVED = "observed hypotheses without current directional support: "
V06_WATCH = "only conditional WATCH hypotheses: "
INC = " ARMED (recovery condition incompatible with its destination)"


def _dname(s):
    return "LONG" if s == "L" else "SHORT"


@pytest.mark.parametrize("s", SIDES)
def test_watch_only_reason_with_only_an_incompatible_armed_scenario(s):
    rx, r6 = run(side(fx.hold(fx.H_AT), s)), run(side(fx.hold(fx.H_AT), s), "v0.6")
    v = view_at(rx, "03:45")
    assert v["table_row"] == "WATCH_ONLY" and [w["status"] for w in v["watch"]] == ["ARMED"]
    assert v["reasons"][0] == f"{OBSERVED}A {_dname(s)}{INC} (not a forecast, not a call)"
    assert not any(r.startswith(V06_WATCH) for r in v["reasons"])
    assert any(r.startswith(f"A {_dname(s)} armed, not counted as directional support: {INCOMPATIBLE}") for r in v["reasons"])
    assert view_at(r6, "03:45")["table_row"] == "CONDITIONAL_SCENARIO"  # v0.6 untouched


@pytest.mark.parametrize("s", SIDES)
def test_watch_only_reason_with_watch_and_incompatible_armed_together(s):
    """``watch_and_incompatible``: A ARM at 08:45 (K = B_A, incompatible) while the B hypothesis born at 08:30 is
    still WATCH (its retest window ends at 09:30): both listed with their actual states."""
    ms = side(fx.watch_and_incompatible(), s)
    rx, r6 = run(ms), run(ms, "v0.6")
    for hm in ("08:45", "09:15"):
        v = view_at(rx, hm)
        assert [(w["family"], w["status"]) for w in v["watch"]] == [("A", "ARMED"), ("B", "WATCH")]
        assert v["reasons"][0] == f"{OBSERVED}A {_dname(s)}{INC}, B {_dname(s)} WATCH (not a forecast, not a call)"
        assert not any(r.startswith(V06_WATCH) for r in v["reasons"])
        assert any(r.startswith(f"A {_dname(s)} armed, not counted as directional support: {INCOMPATIBLE}")
                   for r in v["reasons"])
        v6 = view_at(r6, hm)  # v0.6 still reads the impossible A as its principal
        assert (v6["table_row"], v6["expected_direction"]) == ("CONDITIONAL_SCENARIO", "UP" if s == "L" else "DOWN")


@pytest.mark.parametrize("s", SIDES)
def test_watch_only_reason_with_watch_hypotheses_only_is_the_v06_sentence(s):
    """No incompatible scenario: the v0.6 sentence and record, byte for byte (two WATCH at 08:30; one WATCH at 03:30)."""
    for ms, hm, names in ((side(fx.watch_and_incompatible(), s), "08:30", ["A", "B"]), (side(fx.hold(fx.H_AT), s), "03:30", ["A"])):
        rx, r6 = run(ms), run(ms, "v0.6")
        v, v6 = view_at(rx, hm), view_at(r6, hm)
        assert v["env"]["clock_time"] == v6["env"]["clock_time"] == f"2025-09-01T{hm}:00Z"
        assert [w["status"] for w in v["watch"]] == ["WATCH"] * len(names)
        assert v["reasons"] == v6["reasons"] == [V06_WATCH + ", ".join(f"{f} {_dname(s)}" for f in names)
                                                 + " (not a forecast, not a call)"]
        at = v["env"]["clock_time"]  # the whole published record, ids normalized over each full journal
        assert [x for x in _norm(rx.journal, ("market_view",)) if x[1] == at] ==             [x for x in _norm(r6.journal, ("market_view",)) if x[1] == at]


@pytest.mark.parametrize("s", SIDES)
def test_reasons_with_another_valid_scenario_present_and_after_it_ends(s):
    ms = side(fx.valid_and_incompatible(), s)
    rx, r6 = run(ms), run(ms, "v0.6")
    v, v6 = view_at(rx, "07:45"), view_at(r6, "07:45")
    assert v["table_row"] == "CONDITIONAL_SCENARIO" and v["reasons"][0] == v6["reasons"][0]  # the valid principal's line
    assert not any(r.startswith((OBSERVED, V06_WATCH)) for r in v["reasons"])
    assert any(r.startswith(f"A {_dname(s)} armed, not counted as directional support: {INCOMPATIBLE}") for r in v["reasons"])
    v = view_at(rx, "08:01")  # the valid one ended: only the incompatible ARMED scenario remains
    assert v["reasons"][0] == f"{OBSERVED}A {_dname(s)}{INC} (not a forecast, not a call)"


# -- operational parity: every tape (new and the 75 pinned v0.3-v0.6 tapes) ---------------------------------------------

NEW = {"hold_before": lambda: fx.hold(fx.H_BEFORE), "hold_at": lambda: fx.hold(fx.H_AT),
       "hold_beyond": lambda: fx.hold(fx.H_BEYOND), "reach_at": lambda: fx.reach_threshold(fx.H_AT),
       "reach_before": lambda: fx.reach_threshold(fx.H_BEFORE), "revision": fx.revision_restores,
       "valid_and_incompatible": fx.valid_and_incompatible, "watch_and_incompatible": fx.watch_and_incompatible}
ALL = {**{f"new_{k}_{s}": (lambda f, s: lambda: side(f(), s))(f, s) for k, f in NEW.items() for s in SIDES}, **PARITY}


def _incompatible_intervals(res):
    """[start, end) per scenario while its published antecedent states the incompatibility (end = its next record
    that does not, or its terminal)."""
    out, open_ = [], {}
    for r in scen(res):
        sid, t = r["scenario_id"], r["env"]["clock_time"]
        inc = r["antecedent"].startswith(INCOMPATIBLE) and r["transition"] != "TERMINAL"
        if sid in open_ and not inc:
            out.append((open_.pop(sid), t))
        elif inc and sid not in open_:
            open_[sid] = t
    return out + [(a, "~") for a in open_.values()]


@functools.cache
def _pair(name):
    ms = ALL[name]()
    return run(ms, "v0.6"), run(ms)


@pytest.mark.parametrize("name", sorted(ALL))
def test_operational_records_are_exactly_v06_and_analytic_differences_are_confined(name):
    r6, rx = _pair(name)
    # selection, child, call, revisions, material changes, landmarks, observations: identical
    assert _norm(rx.journal, OPERATIONAL) == _norm(r6.journal, OPERATIONAL)
    # hypothetical paths of the (identical) calls: identical; view samples are analytic
    def paths(r):  # ids hash the rules identity: replaced by order-of-appearance tokens (as ``_norm``)
        ids = _ids(r.journal)
        return [_sub(json.dumps({k: v for k, v in e["record"].items() if k != "env"}, sort_keys=True, default=str), ids)
                for e in r.records if e["kind"] == "path"]
    assert paths(rx) == paths(r6)
    # scenario records: same transitions, levels, reasons, terminals, clocks; only an incompatible antecedent differs
    sx, s6 = _norm([e for e in rx.journal if e["kind"] == "scenario"], ("scenario",)), \
        _norm([e for e in r6.journal if e["kind"] == "scenario"], ("scenario",))
    assert len(sx) == len(s6)
    for a, b in zip(sx, s6, strict=True):
        ra, rb = json.loads(a[2]), json.loads(b[2])
        if ra["antecedent"] != rb["antecedent"]:
            assert ra["antecedent"].startswith(INCOMPATIBLE) and "confirms continuation" in rb["antecedent"]
        assert {k: v for k, v in ra.items() if k != "antecedent"} == {k: v for k, v in rb.items() if k != "antecedent"}
    # MarketView differences only while an incompatibility is published
    ivs = _incompatible_intervals(rx)
    vx, v6 = set(_norm(rx.journal, ("market_view",))), set(_norm(r6.journal, ("market_view",)))
    diff_t = {x[1] for x in vx ^ v6}
    assert all(any(a <= t < b for a, b in ivs) for t in diff_t), (name, sorted(diff_t), ivs)
    if not ivs:
        assert _norm(rx.journal, tuple(sorted({e["kind"] for e in r6.journal}))) == \
            _norm(r6.journal, tuple(sorted({e["kind"] for e in r6.journal})))  # whole journal equal


def test_the_sweep_contains_incompatible_cases_on_both_sides_and_pinned_tapes():
    names = [n for n in ALL if _incompatible_intervals(_pair(n)[1])]
    assert {"new_hold_at_L", "new_hold_at_S", "new_hold_beyond_L", "new_hold_beyond_S", "new_reach_at_L",
            "new_revision_S", "new_valid_and_incompatible_L"} <= set(names)
    assert [n for n in names if not n.startswith("new_")]  # at least one pinned v0.3-v0.6 tape is affected


# -- checkpoint / restore -----------------------------------------------------------------------------------------------

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
def test_restore_around_the_incompatible_arm_and_the_restoring_revision_reproduces_the_run(s):
    ms = side(fx.revision_restores(), s)
    cuts = tuple(fx.T(h, m) + timedelta(seconds=90) for h, m in [(3, 44), (3, 45), (3, 50), (4, 0), (4, 1)])
    base_j, base_r, _ = _fold(ms)
    j, r, states = _fold(ms, cuts)
    assert [e["digest"] for e in j] == [e["digest"] for e in base_j]  # no duplicate, no missing record
    assert [x["digest"] for x in r] == [x["digest"] for x in base_r]
    st = {(k - timedelta(seconds=90)).strftime("%H:%M"): v for k, v in states.items()}
    assert st["03:45"]["format"] == "algotrader.adviser-runtime.v6-tdc"
    assert st["03:45"]["core"]["format"] == "algotrader.adviser-state.v6-tdc"
    assert st["03:50"]["core"]["view"]["principal"] is None  # restored state still excludes the incompatible one
    assert st["04:00"]["core"]["view"]["principal"] is not None
    with pytest.raises(engine.AdviserStateError):  # a variant state never decodes as v0.6 (no silent continuation)
        blob, sha = engine.pack_runtime(make_runtime(eval_start=fx.DAY2, method=X))
        eng6 = {"adviser": {**_engine_doc(make_runtime(eval_start=fx.DAY2, method=X), fx.T(8))["adviser"],
                            "method": "v0.6"}}
        engine.unpack_runtime(blob, sha, eng6)


# -- white-box supplement (state injected; NOT one of the ordinary-entry proofs) ---------------------------------------

def test_white_box_supplement_an_opposing_incompatible_scenario_does_not_force_uncertain(monkeypatch):
    """The opposing case cannot be reached through the ordinary entry on these tapes (an A SHORT needs a 1h DOWN context,
    which the confirmed A LONG's invalidation forbids on this history). This white-box table check shows the shared
    rule on it: v0.6 reads OPPOSING_SCENARIOS / UNCERTAIN, the variant keeps the valid support."""
    def core_with(method):
        core = make_runtime(eval_start=fx.DAY2, method=method).core
        Scen = core.SCEN_CLS
        monkeypatch.setattr(core, "ready_15m", lambda t: True)
        monkeypatch.setattr(core, "ready_1h", lambda t: True)
        core.scen["AL-1"] = Scen(sid="AL-1", family="A", d=1, owner="AL-1", born_at=fx.T(3), born_seq=1, sources=["s"],
                                 setup_deadline=fx.T(5), s15=D(10), z=D(1), status="CONFIRMED", k_t=D(100),
                                 v_t=D(90), dest_t=D(120), conf_at=fx.T(4), conf_deadline=fx.T(8))
        core.scen["AS-2"] = Scen(sid="AS-2", family="A", d=-1, owner="AS-2", born_at=fx.T(3, 30), born_seq=2,
                                 sources=["s"], setup_deadline=fx.T(5), s15=D(10), z=D(1), status="ARMED",
                                 k_t=D(-90), v_t=D(-100), dest_t=D("-90.1"))  # Tq = -89.9 >= Bq = -90.1
        return core

    v6 = core_with("v0.6").compute_view(fx.T(4))
    vx = core_with(X).compute_view(fx.T(4))
    assert (v6["table_row"], v6["expected_direction"]) == ("OPPOSING_SCENARIOS", "UNCERTAIN")
    assert (vx["table_row"], vx["expected_direction"], vx["principal"]["scenario_id"]) == ("CONDITIONAL_SCENARIO", "UP", "AL-1")
    assert [a["scenario_id"] for a in vx["alternatives"]] == ["AS-2"]  # an opposing hypothesis, as a v0.6 WATCH one
