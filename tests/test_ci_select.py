"""The CI/local test selector (scripts/ci_select.py) on the repository's own dependency graph.

Pure: no database, browser or network. Changes are simulated, so the examples do not depend on git history: a
documentation edit, a documentation file read by tests, a UI edit, an engine edit, shared components, unknown or
deleted paths and an explicit full request. Each must be classified, select the right tests and never drop a test
silently (selected + excluded = all test files)."""

# ci_select: no-references (the paths below are simulated changes, not files this test reads)

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ci_select", ROOT / "scripts" / "ci_select.py")
cs = importlib.util.module_from_spec(_spec)
sys.modules["ci_select"] = cs  # dataclasses resolve annotations through the module
_spec.loader.exec_module(cs)


def sel(*paths: str, status: str = "M", forced: str | None = None) -> dict:
    r = cs.select("HEAD", False, forced, changes=[cs.Change(p, status) for p in paths])
    assert sorted(r["selected"] + r["excluded"]) == sorted(set(r["selected"] + r["excluded"]))
    assert len(r["selected"]) + len(r["excluded"]) == r["all_tests"]  # nothing dropped silently
    shards = [f for m in r["matrix"] for f in m["files"].split()]
    assert sorted(shards) == r["selected"] and len(shards) == len(set(shards))  # every selected file runs once
    return r


def names(r: dict, kind: str | None = None) -> set[str]:
    return {Path(t).name for t in r["selected"] if kind is None or (kind == "e2e") == t.startswith("tests/e2e/")}


def test_documentation_only_runs_no_test_suite():
    r = sel("STATE.md", "task.md", "strategic_reviews/SR-003-DIRECTOR-DISPOSITION.md")
    assert r["scope"] == "docs" and r["selected"] == [] and r["matrix"] == []
    assert not r["web"] and not r["compose"]
    md = cs.markdown(r)
    assert "FAST — documentation" in md and "not the full-suite acceptance" in md
    assert f"Excluded test files ({r['all_tests']})" in md


def test_a_documentation_file_read_by_tests_selects_those_tests():
    # the reconstruction read by the market-reading E2E only
    r = sel("delivery/evidence/LIVE-V06-USE-SESSION/reconstruction/saved-live-payload.json")
    assert r["scope"] == "docs" and names(r) == {"test_live_market_reading_e2e.py"}
    # the Director's copy of the MP-001 rules: compared byte for byte with the packaged copy, whose file name the
    # method code also uses -> a method document, selected broadly (conservative)
    r = sel("delivery/MP-001-INTEGRATED-METHOD-PROPOSAL.md")
    assert r["scope"] == "docs" and {"test_adviser_method.py", "test_mp002_versions.py"} <= names(r)


def test_ui_presentation_runs_web_checks_the_web_reading_tests_and_every_e2e():
    r = sel("web/src/views/LiveProposal.tsx")
    assert r["scope"] == "ui" and r["web"] and r["compose"]
    e2e = {p.name for p in (ROOT / "tests" / "e2e").glob("test_*.py")}
    assert names(r, "e2e") == e2e
    assert names(r, "unit") == {"test_ux_wording.py"}  # reads web/src; the API tests use web_dist="no-ui"
    assert "FAST — UI presentation" in cs.markdown(r)


def test_engine_change_selects_the_tests_that_reach_it_and_excludes_the_others():
    r = sel("src/algotrader/adviser/core7.py")
    assert r["scope"] == "engine" and not r["web"] and r["compose"]
    got = names(r, "unit")
    assert {"test_v07_release.py", "test_v07_db.py", "test_tdc_trigger_destination.py"} <= got
    assert not {"test_risk.py", "test_temporal.py", "test_marketdata.py", "test_ci_select.py"} & got
    assert names(r, "e2e")  # the E2E stack starts the whole app (python -m algotrader.cli)
    assert r["excluded"]


def test_a_module_reached_by_every_test_through_conftest_selects_everything():
    r = sel("src/algotrader/db.py")  # imported by tests/conftest.py
    assert r["scope"] == "engine" and r["excluded"] == []


def test_a_changed_test_or_test_helper_selects_its_dependants():
    assert names(sel("tests/test_risk.py")) == {"test_risk.py"}
    r = sel("tests/adviser_tdc_fixtures.py")
    assert {"test_tdc_trigger_destination.py", "test_v07_live_e2e.py"} <= names(r)
    # the selector's own test names paths only as simulated changes (no reference edges), so it is not selected
    assert "test_ci_select.py" not in names(sel("STATE.md", "src/algotrader/adviser/core7.py"))
    assert names(sel("tests/test_ci_select.py")) == {"test_ci_select.py"}


@pytest.mark.parametrize("path", ["pyproject.toml", "uv.lock", ".github/workflows/ci.yml", "tests/conftest.py",
                                  "scripts/ci_select.py", "Dockerfile", ".nvmrc"])
def test_shared_components_fall_back_to_the_full_suite(path):
    r = sel(path)
    assert r["scope"] == "full" and r["excluded"] == [] and r["web"] and r["compose"]
    assert any(path in x for x in r["full_reasons"])
    assert "FULL suite" in cs.markdown(r) and "not the full-suite acceptance" not in cs.markdown(r)


def test_unknown_unreached_deleted_and_mixed_changes_are_conservative():
    assert sel("0")["scope"] == "full"  # unknown path
    assert sel("notes/new-idea.txt", "README.md")["scope"] == "full"
    assert sel("src/algotrader/risk.py", status="D")["scope"] == "full"  # its former dependants are unknown
    r = sel("scripts/never-referenced-by-a-test.py", status="A")
    assert r["scope"] == "full" and "no test reaches this file" in r["full_reasons"][0]
    # one transversal file in an otherwise documentation-only change makes the whole change full
    assert sel("STATE.md", "web/src/views/LiveProposal.tsx", "uv.lock")["scope"] == "full"


@pytest.mark.parametrize("path, ordinary_scope", [
    ("web/src/views/LiveProposal.tsx", "ui"),                          # UI
    ("schemas/algotrader.semantic.v2.json", "engine"),                 # schema
    ("src/algotrader/adviser/method/V07-PARAMETERS.json", "engine"),   # method document
    ("src/algotrader/adviser/method/V07-TRIGGER-DESTINATION-RELEASE.md", "engine"),
    ("delivery/evidence/V07-INTEGRATION/NOTE.md", "docs"),             # documentation
])
def test_a_deletion_of_any_type_is_full_while_the_same_ordinary_edit_keeps_its_scope(path, ordinary_scope):
    # the graph holds only the files present now: a deleted file's former dependants cannot be found
    r = sel(path, status="D")
    assert r["scope"] == "full" and r["excluded"] == []
    assert r["full_reasons"] == [f"{path}: deleted (its former dependants are not in the current graph)"]
    assert "deleted (its former dependants" in cs.markdown(r)
    ordinary = sel(path)
    assert ordinary["scope"] == ordinary_scope and ordinary["full_reasons"] == []
    if ordinary_scope == "docs":
        assert ordinary["selected"] == []  # an evidence note no test reads


def test_a_non_python_rename_is_full_while_the_same_ordinary_edit_keeps_its_scope():
    old, new = "web/src/views/LiveProposal.tsx", "web/src/views/LiveProposalView.tsx"
    r = cs.select("HEAD", False, None, changes=[cs.Change(old, "R", renamed_to=new), cs.Change(new, "A")])
    assert r["scope"] == "full" and r["excluded"] == []
    assert r["full_reasons"] == [f"{old}: renamed to {new} (its former dependants are not in the current graph)"]
    assert f"renamed to {new}" in cs.markdown(r)
    r = sel(old)
    assert r["scope"] == "ui" and names(r, "unit") == {"test_ux_wording.py"}
    for old, new in (("delivery/evidence/V07-INTEGRATION/NOTE.md", "delivery/evidence/V07-INTEGRATION/README.md"),
                     ("schemas/algotrader.semantic.v2.json", "schemas/algotrader.semantic.v2-old.json")):
        r = cs.select("HEAD", False, None, changes=[cs.Change(old, "R", renamed_to=new), cs.Change(new, "A")])
        assert r["scope"] == "full" and r["full_reasons"][0].startswith(f"{old}: renamed to {new}")


def test_git_reports_a_rename_as_the_old_path_renamed_and_the_new_path_added(monkeypatch):
    raw = "R100\0web/a.tsx\0web/b.tsx\0D\0STATE.md\0M\0README.md\0"
    monkeypatch.setattr(cs, "git", lambda *a: raw if a[0] == "diff" else "")
    got = [(c.path, c.status, c.renamed_to) for c in cs.changed_paths("HEAD~1", False)]
    assert got == [("README.md", "M", ""), ("STATE.md", "D", ""), ("web/a.tsx", "R", "web/b.tsx"),
                   ("web/b.tsx", "A", "")]


def test_explicit_request_and_unknown_base_select_everything():
    r = sel("STATE.md", forced="workflow_dispatch: scope=full")
    assert r["scope"] == "full" and r["full_reasons"][0] == "workflow_dispatch: scope=full" and r["excluded"] == []
    r = cs.select(None, False, None)
    assert r["scope"] == "full" and r["full_reasons"] == ["base commit unknown"]


def test_shards_are_deterministic_balanced_and_bounded():
    w = {f"t{i}": float(i + 1) for i in range(30)}
    a = cs.shard(list(w), w, target=60.0, max_shards=4)
    assert a == cs.shard(list(reversed(w)), w, target=60.0, max_shards=4)
    assert len(a) == 4 and sorted(f for s in a for f in s) == sorted(w)
    loads = [sum(w[f] for f in s) for s in a]
    assert max(loads) - min(loads) <= max(w.values())
    assert cs.shard([], w, 60.0, 4) == [] and len(cs.shard(["t0"], w, 60.0, 4)) == 1


def test_github_outputs_and_matrix_are_well_formed(tmp_path, monkeypatch):
    out, summ = tmp_path / "out", tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summ))
    monkeypatch.setattr(cs, "ROOT", ROOT)
    monkeypatch.chdir(tmp_path)
    r = sel("web/src/views/LiveProposal.tsx")
    cs.write_github(r, cs.markdown(r), tmp_path / "ci-selection.json")
    kv = dict(line.split("=", 1) for line in out.read_text(encoding="utf-8").splitlines())
    assert (kv["scope"], kv["web"], kv["compose"], kv["has_tests"]) == ("ui", "true", "true", "true")
    m = json.loads(kv["matrix"])["include"]
    assert {x["kind"] for x in m} == {"unit", "e2e"} and all(x["files"] for x in m)
    assert "Test selection: FAST — UI presentation" in summ.read_text(encoding="utf-8")
    assert json.loads((tmp_path / "ci-selection.json").read_text(encoding="utf-8"))["scope"] == "ui"


def test_durations_from_junit_reports(tmp_path):
    (tmp_path / "a.xml").write_text(
        '<testsuites><testsuite><testcase classname="tests.test_risk" name="a" time="1.5"/>'
        '<testcase classname="tests.test_risk.TestX" name="b" time="2"/>'
        '<testcase classname="tests.e2e.test_ui_smoke" name="c" time="30"/></testsuite></testsuites>',
        encoding="utf-8")
    assert cs.junit_durations(tmp_path) == {"files": {"tests/e2e/test_ui_smoke.py": 30.0, "tests/test_risk.py": 3.5}}
