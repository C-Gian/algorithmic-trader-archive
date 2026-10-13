"""Adviser v0.7 durable integration (DB): v0.7 adviser evaluations over a real receipt-pinned pack prepared offline from
the synthetic tape ``adviser_tdc_fixtures.revision_restores`` (first ARM 03:45 with K = 100900 > B: incompatible; REVISE
04:00 compatible; CONFIRM 04:01; RETURN call 04:03), through the observation worker (engine observe.stream.v8), next to
the frozen v0.6 path. Engineering checks only (tiny synthetic inputs; no market evidence, no economic evaluation)."""

from __future__ import annotations

import adviser_tdc_fixtures as fx
import pytest
from adviser_db import EV_END, EV_START, journal, replay, run_all, worker
from adviser3_fixtures import DAY1
from fastapi.testclient import TestClient
from pack_fixtures import connect
from psycopg.types.json import Jsonb
from test_mp004_db import _cursor, _expire_lease, _prepared, _signature, _strip, crash_once_after

from algotrader.adviser.harness import run_pure
from algotrader.api import create_app
from algotrader.observe import control, deep
from algotrader.observe.contracts import SourceKind
from algotrader.observe.job import SimulatedCrash

pytestmark = pytest.mark.db
N = int((EV_END - DAY1).total_seconds() // 60) + 365
_M = fx.revision_restores()
MINS = (_M + fx.flat(max(0, N - len(_M)), _M[-1].c))[:N]
INCOMPATIBLE = "current recovery condition incompatible with its destination"


def _launch(database_url, root, pack, method="v0.7", paused=False, speed=0):
    with connect(database_url) as c:
        return control.create_replay(c, root, SourceKind.PACK, pack["pack_id"], speed, paused,
                                     expected_manifest_sha256=pack["manifest_sha256"], run_type="adviser_evaluation",
                                     adviser_method=method)


def _a_scen(dj):
    return [e for e in dj if e["kind"] == "scenario" and e["record"]["scenario_id"].startswith("AL")]


def test_v07_pack_evaluation_equals_the_pure_fold_with_reconciliation_v10(database_url, tmp_path, monkeypatch):
    root, art, pack = _prepared(database_url, tmp_path, monkeypatch, MINS)
    rid = _launch(database_url, root, pack)
    run_all(worker(database_url, root, art, checkpoint_events=500))
    row = replay(database_url, rid)
    assert row["status"] == "completed", row["error"]
    assert row["engine_format"] == "observe.stream.v8" and row["engine"]["adviser"]["method"] == "v0.7"
    assert row["engine"]["adviser"]["format"] == "algotrader.adviser-runtime.v7"
    assert row["engine"]["adviser"]["identity"]["implementation"] == "adviser.core.v7"
    v = row["manifest"]["validation"]
    assert v["validator_version"] == "10" and row["assurance"]["state"] == "passed", \
        [c for c in v["checks"] if not c["passed"]]
    assert "Version 10 (v0.7" in v["scope"] and "Version 9 (WP-015" in v["scope"]
    assert row["manifest"]["adviser"]["method"] == "v0.7" and row["manifest"]["schema_revision"] == 10
    pure = run_pure(DAY1, MINS, eval_start=EV_START, eval_end=EV_END, method="v0.7")
    dj = journal(database_url, rid)
    assert [(e["kind"], _strip(e["record"])) for e in dj] == [(e["kind"], _strip(e["record"])) for e in pure.journal]
    tr = [(e["record"]["env"]["clock_time"][11:16], e["record"]["transition"],
           e["record"]["antecedent"].startswith(INCOMPATIBLE)) for e in _a_scen(dj)]
    assert tr[1:4] == [("03:45", "ARM", True), ("04:00", "REVISE", False), ("04:01", "CONFIRM", False)]
    views = [e["record"] for e in dj if e["kind"] == "market_view"]
    at = {r["env"]["clock_time"][11:16]: r for r in views}
    assert at["03:45"]["principal"] is None and [w["status"] for w in at["03:45"]["watch"]] == ["ARMED"]
    assert at["04:00"]["principal"]["scenario_id"].startswith("AL")  # restored only by the revision publication


@pytest.mark.parametrize("crash_at", [("incompatible_arm", (3, 45)), ("between", (3, 52)), ("revision", (4, 0)),
                                      ("call", (4, 3)), ("final_commit", None)], ids=lambda x: x[0])
def test_v07_crash_reclaim_around_the_incompatible_and_restoring_publications_gives_identical_outputs(
        database_url, tmp_path, monkeypatch, crash_at):
    root, art, pack = _prepared(database_url, tmp_path, monkeypatch, MINS)
    base = _launch(database_url, root, pack)
    run_all(worker(database_url, root, art, "observe:a", checkpoint_events=5000))
    want = _signature(database_url, base)
    total = replay(database_url, base)["total_events"]
    rid = _launch(database_url, root, pack)
    at = total if crash_at[1] is None else _cursor(*crash_at[1])
    with pytest.raises(SimulatedCrash):
        run_all(worker(database_url, root, art, "observe:b", checkpoint_events=7, after_commit=crash_once_after(rid, at)))
    _expire_lease(database_url, rid)
    run_all(worker(database_url, root, art, "observe:c", checkpoint_events=7))
    r = replay(database_url, rid)
    assert r["status"] == "completed" and r["assurance"]["state"] == "passed", r["error"]
    assert not [e for e in r["diagnostic_log"] if e["event"] in ("restore_point_rejected", "restore_fallback")]
    assert _signature(database_url, rid) == want  # no duplicate, no missing record
    tr = [e["record"]["transition"] for e in _a_scen(journal(database_url, rid))]
    assert tr.count("ARM") == 1 and tr.count("REVISE") == 1 and tr.count("CONFIRM") == 1


def test_a_v07_run_never_resumes_under_v06(database_url, tmp_path, monkeypatch):
    root, art, pack = _prepared(database_url, tmp_path, monkeypatch, MINS)
    rid = _launch(database_url, root, pack)

    def pause_at(replay_id, cursor):
        if cursor >= _cursor(3, 50):
            with connect(database_url) as c:
                control.pause(c, replay_id)
    run_all(worker(database_url, root, art, "observe:p", checkpoint_events=500, after_commit=pause_at))
    assert replay(database_url, rid)["status"] == "paused"
    before = _signature(database_url, rid)
    with connect(database_url) as c:
        eng = c.execute("SELECT engine FROM observation_replays WHERE replay_id = %s", (rid,)).fetchone()["engine"]
        eng["adviser"]["method"] = "v0.6"
        c.execute("UPDATE observation_replays SET engine = %s WHERE replay_id = %s", (Jsonb(eng), rid))
        control.resume(c, rid)
    run_all(worker(database_url, root, art, "observe:q", checkpoint_events=500))
    r = replay(database_url, rid)
    assert r["status"] == "failed" and "INCOMPATIBLE_ADVISER_IDENTITY" in (r["error"] or "")
    assert _signature(database_url, rid)[:2] == before[:2]


def test_deep_v11_matches_and_detects_a_tampered_incompatibility_statement(database_url, tmp_path, monkeypatch):
    monkeypatch.setattr(deep, "SAVE_EVENTS", 400)
    root, art, pack = _prepared(database_url, tmp_path, monkeypatch, MINS)
    rid = _launch(database_url, root, pack)
    w = worker(database_url, root, art, "observe:h", checkpoint_events=700)
    run_all(w)

    def done(vid):
        run_all(w)
        with connect(database_url) as c:
            return c.execute("SELECT * FROM observation_deep_validations WHERE validation_id = %s", (vid,)).fetchone()
    with connect(database_url) as c:
        vid = deep.create_deep_validation(c, rid)
    v = done(vid)
    assert v["status"] == "completed" and v["result"]["outcome"] == "match", v["result"]["mismatches"]
    assert v["result"]["validator_version"] == "11" and "Version 11 (v0.7" in v["result"]["scope"]
    arm = next(e for e in _a_scen(journal(database_url, rid)) if e["record"]["transition"] == "ARM")
    with connect(database_url) as c:  # stored statement altered (bytes only): never MATCH
        rec = {**arm["record"], "antecedent": "a later eligible complete 1m close >= 100900.1 confirms continuation"}
        c.execute("UPDATE adviser_journal SET record = %s WHERE run_id = %s AND seq = %s", (Jsonb(rec), rid, arm["seq"]))
        vid2 = deep.create_deep_validation(c, rid)
    v2 = done(vid2)
    assert v2["result"]["outcome"] == "mismatch"
    assert any(m["kind"] == "adviser_journal_stored_bytes" for m in v2["result"]["mismatches"])


def test_paired_v06_v07_evaluations_identical_calls_reports_and_read_only_comparison(database_url, tmp_path,
                                                                                     monkeypatch):
    root, art, pack = _prepared(database_url, tmp_path, monkeypatch, MINS)
    api = TestClient(create_app(database_url, art, web_dist=tmp_path / "no-ui", data_root=root))
    listed = api.get("/api/adviser/methods").json()
    assert listed["default"] == "v0.2" and [m["method"] for m in listed["methods"]][-2:] == ["v0.6", "v0.7"]
    seven = listed["methods"][-1]
    assert seven["status"] == "ENGINEERING_REVIEW_PENDING" and seven["label"].startswith("Candidate v0.7")
    assert seven["rules_manifest"][0]["file"] == "V07-TRIGGER-DESTINATION-RELEASE.md"
    ids = {}
    for m in ("v0.6", "v0.7"):
        r = api.post("/api/evaluations", json={"pack_id": pack["pack_id"], "run_type": "adviser_evaluation",
                                               "method": m, "acknowledge_limitations": True})
        assert r.status_code == 201, r.text
        ids[m] = (r.json()["evaluation_id"], r.json()["replay"]["replay_id"])
    run_all(worker(database_url, root, art, "observe:x", checkpoint_events=2000))
    j6, j7 = journal(database_url, ids["v0.6"][1]), journal(database_url, ids["v0.7"][1])
    ops = ("call", "call_revision", "entry_attempt", "material_change")
    def opr(j):
        return [(e["kind"], e["record"]["env"]["clock_time"], e["record"].get("transition") or e["record"].get("entry_status"))
                for e in j if e["kind"] in ops]
    assert opr(j6) == opr(j7) and [e for e in j7 if e["kind"] == "call"]  # identical operational path, one call
    rep = api.get(f"/api/evaluations/{ids['v0.7'][0]}/report.json").json()
    a7 = rep["adviser"]
    assert a7["report_version"] == "adviser.report.v7" and a7["method"]["method"] == "v0.7"
    assert rep["capabilities"]["professional_adviser"]["reason"].startswith("tdc v0.7 btc.context-action.v0.7")
    td = a7["trigger_destination"]
    assert td["incompatible_publications_by_transition"] == {"ARM": 1} and td["restored_by_a_compatible_revision"] == 1
    md7 = api.get(f"/api/evaluations/{ids['v0.7'][0]}/report.md").text
    assert "Candidate v0.7 (trigger/destination compatibility over MP-005" in md7
    assert "#### Trigger/destination compatibility (published records only)" in md7
    a6 = api.get(f"/api/evaluations/{ids['v0.6'][0]}/report.json").json()["adviser"]
    assert a6["report_version"] == "adviser.report.v6" and "trigger_destination" not in a6
    cmp = api.get("/api/evaluations/compare/report.json", params={"a": ids["v0.6"][0], "b": ids["v0.7"][0]}).json()
    assert cmp["comparability"]["verdict"] == "COMPARABLE", cmp["comparability"]
    assert [x["id"] for x in cmp["limitations"]] == ["V07_TRIGGER_DESTINATION_COMPATIBILITY_DELTA"]
    assert cmp["identities"]["b"]["implementation"] == "adviser.core.v7"
