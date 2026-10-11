"""Voluntary Stop then Start of the live adviser with a v0.6 call AVAILABLE (E2E; synthetic MP-005 tape, mocked
services, no network, no Owner data). Engine sessions are real ``LiveSession`` objects persisted through the real
``LiveStore`` under real claimed session rows; the API server and the cockpit read that database unmodified.

The worker's own Stop/Start loop (method-agnostic) is covered by ``test_adviser_live_db`` with v0.2; here the Stop
epilogue mirrors ``LiveAdviserWorker._session`` (connection STOPPED, status STOPPED, fenced save, row stopped).

Contract checked (MP-001 §9 restart rule, WP-009 continuity): Start creates a NEW session that resumes the SAME
continuity run (gap < 96 h, same instrument and method); the restart gap overlapping the ongoing thesis ends the old call
UNASSESSABLE (RESTART_GAP_OVERLAPS_THESIS), recorded once, in the same run, by the second session; no duplicate journal
rows, no reopening, no repeated or new alert, no new call from reconstruction; the saved AVAILABLE never becomes current
again; the cockpit shows the concluded call and its recorded history, and no usable entry.

Observed and reported, not asserted as a contract: the worker's Stop epilogue tapes STOPPED but saves without a dispatch,
so session 1's stored view still holds entry AVAILABLE (the API presents it as UNVERIFIED / NOT_CURRENT), and at the next
Start the restart terminal (stamped at the last processed instant) precedes the pending STOPPED: no Stop-time UNVERIFIED
revision is journaled."""

from __future__ import annotations

import sys
from datetime import timedelta

import adviser6_fixtures as fx
import pytest
from playwright.sync_api import expect

from test_ui_smoke import ROOT, browser, evidence_dir, stack  # noqa: F401

pytestmark = [pytest.mark.e2e, pytest.mark.db]
sys.path.insert(0, str(ROOT / "tests"))
from test_adviser_live import COMPAT, fetcher  # noqa: E402
from test_mp005_live import WIDE, feed6, session, tape  # noqa: E402

from algotrader import db  # noqa: E402
from algotrader.adviser import live as lv  # noqa: E402

EQ = fx.minute(99995, 100005, 99990, 100000)  # the proposal/episode LONG tape: the call is AVAILABLE at 04:07:01.5
QUOTES = {fx.T(4, 5): WIDE}


def _claim(c, sid: str) -> lv.LiveStore:
    got = lv.LiveAdviserWorker("unused", worker_id="adviser:restart-test", lease_seconds=600).claim(c)
    assert got is not None and got[0]["session_id"] == sid
    return lv.LiveStore(c, sid, "adviser:restart-test", got[1])


def _stop_like_worker(c, store: lv.LiveStore, sess: lv.LiveSession) -> None:
    """The Owner's Stop as the worker ends a session (live.py ``LiveAdviserWorker._session`` epilogue)."""
    lv.stop_session(c, store.sid)
    sess.on_connection("STOPPED", sess.clock())
    sess.status = "STOPPED"
    store.save(sess)
    c.execute("UPDATE adviser_live_sessions SET status = 'stopped', stopped_at = now(), phase = 'STOPPED', "
              "lease_owner = NULL, lease_expires_at = NULL WHERE session_id = %s AND lease_generation = %s",
              (store.sid, store.gen))


def test_stop_then_start_keeps_the_run_ends_the_old_call_and_never_restores_availability(stack, browser, evidence_dir):  # noqa: F811
    mins = tape("L", fx.REF, fx.neutral(1)[0], EQ, fx.VALID)
    with db.connection(stack.env["ALGOTRADER_DATABASE_URL"], autocommit=True) as c:
        # session 1: Start (v0.6) -> live call AVAILABLE -> voluntary Stop
        sid1 = lv.start_session(c, "http://x", "v0.6")
        store1 = _claim(c, sid1)
        s1, clock = session(mins, fx.T(4, 7), quotes=QUOTES)
        call = s1.driver.rt.core.call
        assert call is not None and call.entry == "AVAILABLE" and call.thesis == "ONGOING"
        cid, run = call.cid, s1.epoch.run_id
        store1.save(s1)
        clock.t = fx.T(4, 7) + timedelta(seconds=3)
        _stop_like_worker(c, store1, s1)
        alerts1 = c.execute("SELECT alert_key, change_type FROM adviser_alerts ORDER BY created_at").fetchall()
        assert [a["change_type"] for a in alerts1] == ["NEW_CALL"]
        saved = c.execute("SELECT view FROM adviser_live_sessions WHERE session_id = %s", (sid1,)).fetchone()["view"]
        assert saved["call"]["call_id"] == cid and saved["call"]["thesis_status"] == "ONGOING"
        # the Stop is taped by session 1 (its dispatch is still pending in the saved state: see the module note)
        tape1 = [cmd for b in c.execute("SELECT command FROM adviser_input_tape WHERE session_id = %s ORDER BY seq",
                                        (sid1,)).fetchall() for cmd in b["command"]["commands"]]
        assert tape1[-1]["cmd"] == "connection" and tape1[-1]["state"] == "STOPPED"
        n1 = c.execute("SELECT count(*) AS n FROM adviser_journal WHERE run_id = %s", (run,)).fetchone()["n"]

    # while stopped: the API presents the last saved assessment as not current, never as an available entry
    st = stack.get("/api/adviser/live")
    assert st["session"]["session_id"] == sid1 and st["state"] == "STOPPED" and not st["current"]
    assert st["view"]["call"]["call_id"] == cid and st["view"]["call"]["entry_status"] == "UNVERIFIED"
    assert st["view"]["call"]["admissible_bounds"] is None and st["view"]["call"]["presentation"] == "NOT_CURRENT"

    with db.connection(stack.env["ALGOTRADER_DATABASE_URL"], autocommit=True) as c:
        # session 2: Start 5 minutes later -> new session, same run; the restart gap ends the old thesis
        clock.t = fx.T(4, 12) + timedelta(seconds=30)
        sid2 = lv.start_session(c, "http://x", "v0.6")
        assert sid2 != sid1
        store2 = _claim(c, sid2)
        s2 = lv.LiveSession(compat=COMPAT, build="test", clock=clock, method="v0.6")
        s2.start(store2.load_state(), fetcher(mins))
        assert s2.epoch.run_id == run and s2.status == "WARMING_UP"
        assert any(n["event"] == "resumed" and n["run_id"] == run for n in s2.notes)
        assert s2.driver.rt.core.call is None
        store2.save(s2)
        s2.on_connection("CONNECTED", clock.t)
        feed6(s2, clock, mins, fx.T(4, 12), fx.T(4, 15))  # fresh live minutes after the restart
        assert s2.status == "LIVE"
        store2.save(s2)

        rows = c.execute("SELECT seq, kind, record_id, subject, clock_time, record FROM adviser_journal "
                         "WHERE run_id = %s ORDER BY seq", (run,)).fetchall()
        runs = {r["run_id"] for r in c.execute("SELECT DISTINCT run_id FROM adviser_journal").fetchall()}
        alerts2 = c.execute("SELECT alert_key, change_type FROM adviser_alerts ORDER BY created_at").fetchall()
        tape2 = [cmd for b in c.execute("SELECT command FROM adviser_input_tape WHERE session_id = %s ORDER BY seq",
                                        (sid2,)).fetchall() for cmd in b["command"]["commands"]]
        sessions = c.execute("SELECT session_id, status, view->>'run_id' AS run FROM adviser_live_sessions "
                             "ORDER BY created_at").fetchall()

    # one continuity run, two sessions; the journal grew without duplicates or gaps
    assert runs == {run}
    assert [(s["session_id"], s["status"], s["run"]) for s in sessions] == [(sid1, "stopped", run), (sid2, "running", run)]
    assert [r["seq"] for r in rows] == list(range(1, len(rows) + 1)) and len(rows) > n1
    assert len({r["record_id"] for r in rows}) == len(rows)
    # the old call: issued once, never reissued or reopened; its only terminal is the restart-gap one
    assert [r["record_id"] for r in rows if r["kind"] == "call"] == [cid]
    revs = [r for r in rows if r["kind"] == "call_revision" and r["subject"] == cid]
    assert [r["record"]["revision"] for r in revs] == list(range(1, len(revs) + 1))
    terminals = [r for r in revs if r["record"]["thesis_status"] != "ONGOING"]
    assert len(terminals) == 1 and terminals[0] is revs[-1]
    term = terminals[0]["record"]
    assert (term["thesis_status"], term["terminal_reason"]) == ("UNASSESSABLE", "RESTART_GAP_OVERLAPS_THESIS")
    assert term["entry_status"] != "AVAILABLE" and terminals[0]["seq"] > n1  # written by the second session
    assert terminals[0]["clock_time"] < fx.T(4, 12)  # at the restart point (last processed instant), before catch-up
    assert any(cmd["cmd"] == "restart" and cmd["reason"] == "RESTART_GAP_OVERLAPS_THESIS" for cmd in tape2)
    assert not [r for r in rows[n1:] if r["kind"] == "call"]  # reconstruction and the first live minutes issue no call
    # no alert replayed, and no alert for the restart terminal
    assert alerts2 == alerts1

    # live API: the new session on the same run, no current call, the old call listed as concluded once
    st = stack.get("/api/adviser/live")
    assert st["session"]["session_id"] == sid2 and st["view"]["run_id"] == run
    assert st["view"]["call"] is None
    rc = [x for x in st["view"]["recent_calls"] if x["call_id"] == cid]
    assert len(rc) == 1 and (rc[0]["terminal"], rc[0]["reason"]) == ("UNASSESSABLE", "RESTART_GAP_OVERLAPS_THESIS")
    detail = stack.get(f"/api/adviser/runs/{run}/calls/{cid}")
    assert detail["call"]["call_id"] == cid and detail["revisions"] == [r["record"] for r in revs]

    # cockpit: concluded call and its recorded history; no usable entry anywhere, also after a reload
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000}, timezone_id="Europe/Rome")
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"{stack.base}/#market")
    for attempt in range(2):
        panel = page.get_by_test_id("live-call")
        expect(panel).to_have_attribute("data-state", "WAITING", timeout=15_000)
        expect(page.get_by_test_id("live-call-identity")).to_contain_text("Conclusa — non valutabile")
        expect(page.get_by_test_id("live-call-concluded")).to_have_attribute("data-terminal", "UNASSESSABLE")
        expect(page.get_by_test_id("live-concluded-reason")).to_contain_text("RESTART_GAP_OVERLAPS_THESIS")
        expect(page.get_by_test_id("live-concluded-guidance")).not_to_have_attribute("data-kind", "LOADING", timeout=15_000)
        for gone in ("live-entry", "live-admissible"):
            expect(page.get_by_test_id(gone)).to_have_count(0)
        expect(page.locator(".sig-avail")).to_have_count(0)
        expect(page.locator(".band-admissible")).to_have_count(0)
        expect(page.get_by_test_id("live-no-trade")).to_have_text("In attesa — nessun ingresso proposto")
        if attempt == 0:
            page.screenshot(path=str(evidence_dir / "restart-cockpit.png"), full_page=True)
            page.reload()
    # the previous call's recorded history, from What changed
    page.get_by_test_id("timeline-call-history-open").first.click()
    hist = page.get_by_test_id("live-call-history")
    expect(hist).to_be_visible()
    expect(hist.get_by_test_id("history-identity")).to_contain_text(cid)
    expect(hist.get_by_test_id("history-identity")).to_contain_text(run)
    expect(hist.get_by_test_id("history-status-terminal")).to_be_visible()
    expect(hist.get_by_test_id("history-revisions")).to_contain_text("RESTART_GAP_OVERLAPS_THESIS")
    page.screenshot(path=str(evidence_dir / "restart-history.png"), full_page=True)
    assert not errors, errors
    ctx.close()
