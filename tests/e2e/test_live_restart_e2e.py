"""Voluntary Stop then Start of the live adviser with a v0.6 call AVAILABLE, through the REAL worker path (E2E; the
WP-009 offline fakes fed with the synthetic MP-005 tape: mocked OKX REST/WebSocket/ticker, no network, no Owner data):
Start -> call AVAILABLE -> Stop requested -> Stop confirmed and saved by the worker -> Start -> restore.

Contract (orchestrator decision, 11 October 2026):
- Stop keeps the last assessment and its timestamp. A kept AVAILABLE is historical: the API serves UNVERIFIED with the
  stopped/not-current reason and no usable band; the cockpit shows no current availability, also after a reload.
- STOPPED is a SESSION event at its actual time: never an engine input, never a call revision, never backdated.
- At Start the existing gap rules apply: same run (gap < 96 h, same instrument and method); the restart gap ends the
  ongoing thesis UNASSESSABLE (AVAILABLE -> UNASSESSABLE in the journal); no new "every Stop invalidates" rule.
- One continuity run, two sessions; the old call is never duplicated, reopened or re-alerted; its recorded history is
  consultable and distinct from current availability and from the session interruption."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta

import adviser6_fixtures as fx
import pytest
from playwright.sync_api import expect

from test_ui_smoke import ROOT, browser, evidence_dir, stack, wait_for  # noqa: F401

pytestmark = [pytest.mark.e2e, pytest.mark.db]
sys.path.insert(0, str(ROOT / "tests"))
from pack_fixtures import connect  # noqa: E402
from test_adviser_live_db import FakeClock, _run_worker, _wait, ws_messages  # noqa: E402
from test_mp004_live import START  # noqa: E402
from test_mp005_live import tape  # noqa: E402

from algotrader.adviser import live as lv  # noqa: E402

EQ = fx.minute(99995, 100005, 99990, 100000)  # the proposal/episode LONG tape: a v0.6 call issued at 04:07:01


def _tape(c, sid: str) -> list[dict]:
    return [cmd for b in c.execute("SELECT command FROM adviser_input_tape WHERE session_id = %s ORDER BY seq",
                                   (sid,)).fetchall() for cmd in b["command"]["commands"]]


def _session(c, sid: str) -> dict:
    return c.execute("SELECT * FROM adviser_live_sessions WHERE session_id = %s", (sid,)).fetchone()


def _current_available(stack) -> bool:
    st = stack.get("/api/adviser/live")
    return bool(st["current"]) and ((st["view"] or {}).get("call") or {}).get("entry_status") == "AVAILABLE"


def test_stop_then_start_through_the_worker_keeps_history_and_never_serves_old_availability(stack, browser, evidence_dir):  # noqa: F811
    url = stack.env["ALGOTRADER_DATABASE_URL"]
    mins = tape("L", fx.REF, fx.neutral(1)[0], EQ, fx.VALID)
    clock = FakeClock(START + timedelta(seconds=30))
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000}, timezone_id="Europe/Rome")
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    panel = page.get_by_test_id("live-call")
    th2 = sid2 = None
    try:
        # ---- session 1: Start (v0.6) -> live call AVAILABLE ----------------------------------------------------------
        with connect(url) as c:
            sid1 = lv.start_session(c, "http://x", "v0.6")
        th1, ws1 = _run_worker(url, clock, ws_messages(START, fx.T(4, 7), mins), mins)
        _wait(url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'status' = 'WARMING_UP'", (sid1,))
        ws1.gate.set()
        call_row = _wait(url, "SELECT * FROM adviser_journal WHERE kind = 'call'", ())
        cid, run = call_row["record_id"], call_row["run_id"]
        wait_for(lambda: _current_available(stack), timeout=60)
        page.goto(f"{stack.base}/#market")
        expect(panel).to_have_attribute("data-state", "AVAILABLE", timeout=15_000)  # precondition: served as current
        with connect(url) as c:
            before = _session(c, sid1)["view"]
            n_before = c.execute("SELECT count(*) AS n FROM adviser_journal WHERE run_id = %s", (run,)).fetchone()["n"]
            alerts1 = [a["alert_key"] for a in c.execute("SELECT alert_key FROM adviser_alerts ORDER BY created_at")]
        assert before["call"]["call_id"] == cid and before["call"]["entry_status"] == "AVAILABLE"

        # ---- Stop requested -> confirmed and saved by the worker -----------------------------------------------------
        with connect(url) as c:
            lv.stop_session(c, sid1)
        th1.join(60)
        assert not th1.is_alive()
        with connect(url) as c:
            s1 = _session(c, sid1)
            tape1 = _tape(c, sid1)
            n_stop = c.execute("SELECT count(*) AS n FROM adviser_journal WHERE run_id = %s", (run,)).fetchone()["n"]
        v1 = s1["view"]
        assert s1["status"] == "stopped" and s1["stopped_at"] is not None and v1["status"] == "STOPPED"
        assert not v1["connected"]
        # the last assessment is kept as it was, with its own timestamp (historical AVAILABLE, no Stop revision)
        assert v1["clock"] == before["clock"] and v1["call"] == before["call"]
        assert n_stop == n_before  # the Stop wrote no journal record
        # STOPPED is a session event at the Stop's own time, never an engine input
        stop_note = [n for n in v1["notes"] if n["event"] == "stopped"]
        stop_at = datetime.fromisoformat(stop_note[0]["at"].replace("Z", "+00:00")) if stop_note else None
        assert len(stop_note) == 1 and stop_at >= datetime.fromisoformat(before["clock"].replace("Z", "+00:00"))
        assert not [x for x in tape1 if x["cmd"] == "connection" and x["state"] == "STOPPED"]
        # served while stopped: UNVERIFIED, stopped/not-current reason, no usable band
        st = stack.get("/api/adviser/live")
        assert st["session"]["session_id"] == sid1 and st["state"] == "STOPPED" and not st["current"]
        sc = st["view"]["call"]
        assert (sc["call_id"], sc["entry_status"], sc["entry_status_saved"]) == (cid, "UNVERIFIED", "AVAILABLE")
        assert "SESSION_NOT_CURRENT:STOPPED" in sc["entry_reasons"] and sc["admissible_bounds"] is None
        assert sc["presentation"] == "NOT_CURRENT"
        for reload in (False, True):
            if reload:
                page.reload()
            expect(panel).to_have_attribute("data-state", "UNVERIFIED", timeout=15_000)
            expect(page.get_by_test_id("live-call-not-current")).to_be_visible()
            expect(page.get_by_test_id("live-entry-consequence")).to_have_attribute("data-kind", "NOT_CURRENT")
            expect(page.get_by_test_id("live-admissible")).to_have_count(0)
            expect(page.locator(".sig-avail")).to_have_count(0)
            expect(page.locator(".band-admissible")).to_have_count(0)
            # the interruption is a session event in What changed, not a call revision
            expect(page.get_by_test_id("live-timeline")).to_contain_text("stopped")
        page.screenshot(path=str(evidence_dir / "restart-1-stopped.png"), full_page=True)

        # ---- Start 5 minutes later -> restore -----------------------------------------------------------------------
        clock.set(fx.T(4, 12) + timedelta(seconds=30))
        with connect(url) as c:
            sid2 = lv.start_session(c, "http://x", "v0.6")
        assert sid2 != sid1
        th2, ws2 = _run_worker(url, clock, ws_messages(fx.T(4, 12), fx.T(4, 15), mins), mins)
        _wait(url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'status' = 'WARMING_UP'", (sid2,))
        ws2.gate.set()
        _wait(url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'status' = 'LIVE'", (sid2,))
        _wait(url, "SELECT 1 FROM adviser_journal WHERE kind = 'call_revision' AND subject = %s AND "
                   "record->>'terminal_reason' = 'RESTART_GAP_OVERLAPS_THESIS'", (cid,))
        with connect(url) as c:
            rows = c.execute("SELECT seq, kind, record_id, subject, clock_time, record FROM adviser_journal "
                             "WHERE run_id = %s ORDER BY seq", (run,)).fetchall()
            runs = {r["run_id"] for r in c.execute("SELECT DISTINCT run_id FROM adviser_journal").fetchall()}
            alerts2 = [a["alert_key"] for a in c.execute("SELECT alert_key FROM adviser_alerts ORDER BY created_at")]
            tape2 = _tape(c, sid2)
            v2 = _session(c, sid2)["view"]
            all_tape = [cmd for b in c.execute("SELECT command FROM adviser_input_tape WHERE run_id = %s", (run,))
                        for cmd in b["command"]["commands"]]
        # same continuity run, a new session; the existing gap rule (not a Stop rule) ends the old thesis
        assert runs == {run} and v2["run_id"] == run
        assert any(n["event"] == "resumed" and n["run_id"] == run for n in v2["notes"])
        assert not [n for n in v2["notes"] if n["event"] == "pending_stop_superseded"]  # nothing pending from the Stop
        assert [r["seq"] for r in rows] == list(range(1, len(rows) + 1))
        assert len({r["record_id"] for r in rows}) == len(rows)
        assert [r["record_id"] for r in rows if r["kind"] == "call"] == [cid]  # issued once, never reissued
        revs = [r for r in rows if r["kind"] == "call_revision" and r["subject"] == cid]
        assert [r["record"]["revision"] for r in revs] == list(range(1, len(revs) + 1))
        assert all(r["seq"] > n_stop for r in revs)  # no revision was written by the Stop (none before it either)
        terminals = [r for r in revs if r["record"]["thesis_status"] != "ONGOING"]
        assert len(terminals) == 1 and terminals[0] is revs[-1]
        term = terminals[0]
        assert (term["record"]["thesis_status"], term["record"]["terminal_reason"]) == (
            "UNASSESSABLE", "RESTART_GAP_OVERLAPS_THESIS")
        assert term["record"]["entry_status"] != "AVAILABLE"
        restart = [x for x in tape2 if x["cmd"] == "restart"]
        assert len(restart) == 1 and restart[0]["reason"] == "RESTART_GAP_OVERLAPS_THESIS"
        # the gap terminal sits at the restored processing point (existing rule): never after the Stop, never moved
        assert datetime.fromisoformat(restart[0]["at"]) == term["clock_time"]
        assert term["clock_time"] <= stop_at
        assert not [x for x in all_tape if x["cmd"] == "connection" and x["state"] == "STOPPED"]
        assert not [r for r in rows if r["seq"] > n_stop and r["kind"] == "call"]  # no new call from reconstruction
        assert alerts2 == alerts1  # no replayed alert and no alert for the gap terminal

        st = stack.get("/api/adviser/live")
        assert st["session"]["session_id"] == sid2 and st["view"]["run_id"] == run and st["view"]["call"] is None
        rc = [x for x in st["view"]["recent_calls"] if x["call_id"] == cid]
        assert len(rc) == 1 and (rc[0]["terminal"], rc[0]["reason"]) == ("UNASSESSABLE", "RESTART_GAP_OVERLAPS_THESIS")
        detail = stack.get(f"/api/adviser/runs/{run}/calls/{cid}")
        assert detail["call"]["call_id"] == cid and detail["revisions"] == [r["record"] for r in revs]

        for _ in range(2):  # the restored cockpit, then after a reload
            page.reload()
            expect(panel).to_have_attribute("data-state", "WAITING", timeout=15_000)
            expect(page.get_by_test_id("live-call-identity")).to_contain_text("Conclusa — non valutabile")
            expect(page.get_by_test_id("live-call-concluded")).to_have_attribute("data-terminal", "UNASSESSABLE")
            expect(page.get_by_test_id("live-concluded-reason")).to_contain_text("RESTART_GAP_OVERLAPS_THESIS")
            for gone in ("live-entry", "live-admissible", "live-call-not-current"):
                expect(page.get_by_test_id(gone)).to_have_count(0)
            expect(page.locator(".sig-avail")).to_have_count(0)
            expect(page.locator(".band-admissible")).to_have_count(0)
            expect(page.get_by_test_id("live-timeline")).to_contain_text("resumed")  # the interruption: a session event
        page.screenshot(path=str(evidence_dir / "restart-2-after-start.png"), full_page=True)
        # the call's recorded history, from What changed: revisions only, distinct from availability and sessions
        page.get_by_test_id("timeline-call-history-open").first.click()
        hist = page.get_by_test_id("live-call-history")
        expect(hist.get_by_test_id("history-identity")).to_contain_text(cid)
        expect(hist.get_by_test_id("history-identity")).to_contain_text(run)
        expect(hist.get_by_test_id("history-status-terminal")).to_be_visible()
        expect(hist.get_by_test_id("history-revisions")).to_contain_text("RESTART_GAP_OVERLAPS_THESIS")
        expect(hist.get_by_test_id("history-revisions")).not_to_contain_text("LIVE_SESSION_STOPPED")
        page.screenshot(path=str(evidence_dir / "restart-3-history.png"), full_page=True)
        assert not errors, errors
    finally:
        ctx.close()
        if sid2 is not None:
            with connect(url) as c:
                lv.stop_session(c, sid2)
            if th2 is not None:
                th2.join(60)
