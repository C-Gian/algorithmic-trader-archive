"""Adviser v0.7 (``delivery/V07-TRIGGER-DESTINATION-RELEASE.md``): the approved tdc correction (57fa14e) as a product
version. Identity and isolation, behavioural equivalence with the approved EXPERIMENTAL v0.6-tdc fold, operational
identity with the frozen v0.6, restore refusal across identities, the inspection verdict, report v7, reconciliation
v10 and the live path. Synthetic tapes through the ordinary entry only (``adviser_tdc_fixtures``)."""

from __future__ import annotations

import functools
import json
from decimal import Decimal

import adviser_tdc_fixtures as fx
import pytest
from adviser3_fixtures import Stepper, T
from test_mp004_versions import _norm
from test_tdc_trigger_destination import ALL, INCOMPATIBLE, OPERATIONAL, _pair

from algotrader.adviser import engine, methods
from algotrader.adviser import reconcile as rec
from algotrader.adviser import report7
from algotrader.adviser import contracts as sc
from algotrader.adviser.compare import TDC_LIMITATION
from algotrader.adviser.core7 import AdviserCoreV7
from algotrader.adviser.harness import make_runtime, run_pure

V7 = "v0.7"
D = Decimal


def run(ms, method=V7):
    return run_pure(fx.DAY1, ms, method=method, eval_start=fx.DAY2)


@functools.cache
def _v7(name):
    return run(ALL[name]())


# -- identity -----------------------------------------------------------------------------------------------------------

def test_v07_is_a_distinct_selectable_product_version_and_v06_is_unchanged():
    v6, v7, tdc = methods.get("v0.6"), methods.get(V7), methods.get("v0.6-tdc", experimental=True)
    assert methods.DEFAULT == "v0.2" and [m["method"] for m in methods.selectable()] == [
        "v0.2", "v0.3", "v0.4", "v0.5", "v0.6", "v0.7"]
    assert (v7.model, v7.rules_version, v7.implementation, v7.core_state_format, v7.runtime_format, v7.engine_format,
            v7.report_version, v7.reconciliation_version, v7.deep_version) == (
        "btc.context-action.v0.7", "tdc.rules.v0.7", "adviser.core.v7", "algotrader.adviser-state.v7",
        "algotrader.adviser-runtime.v7", "observe.stream.v8", "adviser.report.v7", "10", "11")
    for other in (v6, tdc):
        for f in ("model", "rules_version", "implementation", "core_state_format", "runtime_format", "engine_format"):
            assert getattr(v7, f) != getattr(other, f), f
    # frozen v0.6 identity (pinned references of the A v0.6 studies)
    assert v6.rules_sha256() == "57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66"
    assert v6.register_sha256() == "98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda"
    assert "v0.6-tdc" in methods.EXPERIMENTAL and "v0.6-a2x" in methods.EXPERIMENTAL  # variants kept, not releases
    files = [m["file"] for m in v7.rules_manifest()]
    assert files[:4] == ["V07-TRIGGER-DESTINATION-RELEASE.md", "A-TRIGGER-DESTINATION-CORRECTION.md",
                         "A-TRIGGER-DESTINATION-SEMANTIC-REVIEW.md", "MP-005-V06-INITIAL-RESPONSE-INCOMPATIBILITY.md"]
    assert "A-SECOND-ATTEMPT-DESIGN.md" not in files  # no a2x
    root = methods.idn.METHOD_DIR
    for name in ("V07-TRIGGER-DESTINATION-RELEASE.md", "A-TRIGGER-DESTINATION-CORRECTION.md"):
        assert (root / name).read_bytes().replace(b"\r\n", b"\n") == \
            (root.parents[3] / "delivery" / name).read_bytes().replace(b"\r\n", b"\n")
    # the correction rules are exactly those approved at 57fa14e (same packaged text as the experimental variant's)
    assert next(m for m in v7.rules_manifest() if m["file"] == "A-TRIGGER-DESTINATION-CORRECTION.md")["sha256_lf"] == \
        next(m for m in tdc.rules_manifest() if m["file"] == "A-TRIGGER-DESTINATION-CORRECTION.md")["sha256_lf"]
    p6, p7 = v6.params(), v7.params()
    assert {k: v for k, v in p6.__dict__.items() if k != "raw"} == {k: v for k, v in p7.__dict__.items() if k != "raw"}
    assert {k for k in v7.register() if v7.register()[k] != tdc.register().get(k)} == {
        "model", "status", "rules_version", "identity", "trigger_destination_compatibility"}
    assert sc.SEMANTIC_V2_EMITTED_REVISION["btc.context-action.v0.7"] == 6 == sc.SEMANTIC_V2_REVISION
    assert sc.SEMANTIC_V2_EMITTED_REVISION["btc.context-action.v0.6"] == 5
    assert sc.KIND_CONTRACTS_V7 == sc.KIND_CONTRACTS_V6
    core = make_runtime(eval_start=fx.DAY2, method=V7).core
    assert type(core) is AdviserCoreV7 and core.KINDS is sc.KIND_CONTRACTS_V7
    assert "AdviserCoreA2X" not in [c.__name__ for c in type(core).__mro__]


# -- behaviour: exactly the approved tdc fold; operationally exactly v0.6 ---------------------------------------------

@pytest.mark.parametrize("name", sorted(n for n in ALL if n.startswith("new_")) + [
    "a_fade", "mp003_arm_source_touches_b", "mp004_two_valid", "box_b", "mp005_h3"])
def test_v07_journal_equals_the_approved_tdc_fold_and_its_operations_equal_v06(name):
    r6, rt = _pair(name)  # (v0.6, v0.6-tdc) of the tdc sweep
    r7 = _v7(name)
    kinds = tuple(sorted({e["kind"] for e in rt.journal} | {e["kind"] for e in r7.journal}))
    assert _norm(r7.journal, kinds) == _norm(rt.journal, kinds)  # same records (ids/envelopes normalized)
    assert _norm(r7.journal, OPERATIONAL) == _norm(r6.journal, OPERATIONAL)
    assert len(r7.calls()) == len(r6.calls())


# -- restore: only under a compatible identity ------------------------------------------------------------------------

def test_a_v07_state_never_decodes_under_another_method_and_vice_versa():
    for src, dst in ((V7, "v0.6"), (V7, "v0.6-tdc"), ("v0.6", V7), ("v0.6-tdc", V7)):
        rt = make_runtime(eval_start=fx.DAY2, method=src)
        blob, sha = engine.pack_runtime(rt)
        rel = methods.get(dst, experimental=True)
        eng = {"adviser": {"method": rel.key, "format": rel.runtime_format}}
        with pytest.raises(engine.AdviserStateError):
            engine.unpack_runtime(blob, sha, eng)


# -- inspection verdict (the cockpit translates it; it never computes it) -----------------------------------------------

@pytest.mark.parametrize("s", ("L", "S"))
def test_inspection_rows_carry_the_engine_verdict_and_the_restoration(s):
    ms = fx.revision_restores() if s == "L" else fx.short(fx.revision_restores())
    st = Stepper(ms, method=V7)
    st.run_until(T(3, 45))
    row = next(r for r in st.core.scenarios_view(T(3, 45)) if r["family"] == "A")
    thr = D("100900.1") if s == "L" else D("99099.9")
    assert row["trigger_destination"]["compatible"] is False and D(row["trigger_destination"]["threshold"]) == thr
    assert row["trigger_destination"]["restored_by_revision"] is False
    st.run_until(T(4, 0))
    row = next(r for r in st.core.scenarios_view(T(4, 0)) if r["family"] == "A")
    td = row["trigger_destination"]
    assert (td["compatible"], td["previous_anchor_incompatible"], td["restored_by_revision"]) == (True, True, True)
    assert td["revision_published_at"] == "2025-09-01T04:00:00+00:00"
    st.finish()


# -- report v7 and reconciliation v10 -----------------------------------------------------------------------------------

def test_report_v7_counts_published_records_only():
    r = run(fx.revision_restores())
    td = report7.trigger_destination(r.journal)
    assert td["incompatible_publications_by_transition"] == {"ARM": 1}
    assert td["scenarios_with_an_incompatible_publication"] == 1 and td["restored_by_a_compatible_revision"] == 1
    assert td["restoration_examples"][0]["at"] == "2025-09-01T04:00:00Z"
    assert td["market_views_without_support_from_an_armed_scenario"] >= 1
    r = run(fx.hold(fx.H_BEFORE))  # compatible one tick before B: nothing to report
    assert report7.trigger_destination(r.journal)["incompatible_publications"] == 0


def test_reconciliation_v10_check_matches_published_levels_and_detects_a_tampered_statement():
    r = run(fx.hold(fx.H_AT))
    assert rec._v7_trigger_destination(r.journal, D("0.1")) == []
    j = json.loads(json.dumps(r.journal, default=str))
    arm = next(e for e in j if e["kind"] == "scenario" and e["record"]["transition"] == "ARM")
    arm["record"]["antecedent"] = "a later eligible complete 1m close >= 100900.0 confirms continuation"  # v0.6 text
    assert rec._v7_trigger_destination(j, D("0.1"))
    r = run(fx.hold(fx.H_BEFORE))
    j = json.loads(json.dumps(r.journal, default=str))
    arm = next(e for e in j if e["kind"] == "scenario" and e["record"]["transition"] == "ARM")
    arm["record"]["antecedent"] = INCOMPATIBLE + ": tampered"
    assert rec._v7_trigger_destination(j, D("0.1"))
    assert "Version 10 (v0.7" in rec.SCOPE_V10 and TDC_LIMITATION["id"].startswith("V07_")


# -- live path (mocked services; never an Owner live session) -----------------------------------------------------------

def test_live_v07_session_publishes_the_verdict_and_never_continues_another_method_lineage():
    from test_mp005_live import session

    sess, clock = session(fx.revision_restores(), T(3, 46), method=V7)
    v = sess.view()
    assert v["method"] == V7 and v["market_view"]["table_row"] == "WATCH_ONLY"
    assert v["market_view"]["reasons"][0].startswith("observed hypotheses without current directional support: A LONG ARMED")
    a = next(s for s in v["scenarios"] if s["family"] == "A")
    assert a["status"] == "ARMED" and a["trigger_destination"]["compatible"] is False
    assert a["antecedent"].startswith(INCOMPATIBLE)
    sess6, _ = session(fx.revision_restores(), T(3, 46), method="v0.6")
    v6 = sess6.view()
    assert v6["market_view"]["table_row"] == "CONDITIONAL_SCENARIO"  # frozen v0.6 unchanged
    assert "trigger_destination" not in next(s for s in v6["scenarios"] if s["family"] == "A")
