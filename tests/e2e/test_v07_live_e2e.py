"""Adviser v0.7 integrated synthetic acceptance (E2E): the trigger/destination compatibility through the REAL path -
cockpit Start -> API -> live worker (offline OKX fakes, bounded catch-up, WARMING_UP, LIVE) -> engine -> persistence
(session, journal) -> API -> cockpit (Italian translation of the published reasons and of the engine verdict only).

TECHNICAL PROOF WITHOUT ECONOMIC MEANING. Inputs are the synthetic tapes of ``tests/adviser_tdc_fixtures.py`` served by
the existing offline fakes; nothing is put into any state, no gate/readiness/timestamp is altered; the only test control
is WHEN scripted pushes are released (``FakeWS.until``). The tick borders before/beyond B are proven by the engine suites
(``test_tdc_trigger_destination``, ``test_v07_release``) and not repeated here.

1. LONG ``revision_restores``: first ARM 03:45 with K 100900 > B (incompatible) -> no directional support; REVISE 04:00
   compatible -> support only from that publication; the live child/call path identical to frozen v0.6; reload; Stop/Start
   v0.7 restores the same run without duplicating its history; Start v0.6 opens a new epoch (METHOD_CHANGED) and never
   rewrites the v0.7 records.
2. SHORT ``hold(H_AT)``: effective threshold exactly at B.
3. LONG ``valid_and_incompatible``: another valid (confirmed) scenario present keeps the directional reading.
4. EXCEPTION - translation test only, not an integrated engine proof: from the real SHORT view, PREPARED MarketView
   variants (CONDITIONAL_SCENARIO with principal, OPPOSING_SCENARIOS, REQUIRED_CONTEXT_UNAVAILABLE, WATCH_ONLY) check that
   the note beside an incompatible scenario repeats the published reading and never deduces one from an absent principal."""

from __future__ import annotations

import copy
import json
import sys
from datetime import datetime, timedelta

import adviser_tdc_fixtures as fx
import pytest
from playwright.sync_api import expect

from test_ui_smoke import ROOT, browser, evidence_dir, record, stack  # noqa: F401

pytestmark = [pytest.mark.e2e, pytest.mark.db]
sys.path.insert(0, str(ROOT / "tests"))
from pack_fixtures import connect  # noqa: E402
from test_adviser_live_db import FakeClock, _run_worker, _wait, ws_messages  # noqa: E402
from test_mp004_live import START  # noqa: E402

from algotrader.adviser import live as lv  # noqa: E402

HOLD = timedelta(seconds=1, milliseconds=300)
INCOMPATIBLE = "current recovery condition incompatible with its destination"


def _iso(t: datetime) -> str:
    return t.isoformat()


def _journal(c, run: str) -> list[dict]:
    return c.execute("SELECT seq, kind, record_id, subject, clock_time, origin, record FROM adviser_journal "
                     "WHERE run_id = %s ORDER BY seq", (run,)).fetchall()


class Episode:
    """One live session on a synthetic tape; ``at(t)`` releases the scripted pushes up to the minute ending at t and
    waits until the session's own view reached that dispatch."""

    def __init__(self, stack, mins, start, clock=None):
        self.stack, self.url, self.mins, self.start = stack, stack.env["ALGOTRADER_DATABASE_URL"], mins, start
        self.clock = clock or FakeClock(start + timedelta(seconds=30))
        self.sid = self.th = self.ws = None

    def run(self, sid, end):
        self.sid = sid
        self.th, self.ws = _run_worker(self.url, self.clock, ws_messages(self.start, end, self.mins), self.mins)
        _wait(self.url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'status' = 'WARMING_UP'",
              (sid,))
        self.ws.until = self.start
        self.ws.gate.set()

    def at(self, t: datetime) -> dict:
        self.ws.until = t + HOLD
        _wait(self.url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'clock' = %s",
              (self.sid, _iso(t + timedelta(seconds=1))))
        return self.stack.get("/api/adviser/live")

    def stop(self):
        if self.sid is not None:
            with connect(self.url) as c:
                lv.stop_session(c, self.sid)
            if self.th is not None:
                self.th.join(60)


def _page(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000}, timezone_id="Europe/Rome")
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page, errors


def test_v07_long_incompatible_then_restored_by_revision_reload_restore_and_v06_isolation(stack, browser, evidence_dir):  # noqa: F811
    ep = Episode(stack, fx.revision_restores(), START)
    ctx, page, errors = _page(browser)
    shots: list[str] = []
    ep6 = None

    def shot(name):
        page.screenshot(path=str(evidence_dir / name), full_page=True)
        shots.append(name)
    try:
        # ---- ordinary Start from the cockpit, method v0.7 ---------------------------------------------------------
        page.goto(f"{stack.base}/#market")
        page.get_by_test_id("live-method-select").select_option("v0.7")
        page.get_by_test_id("live-start").click()
        q = _wait(ep.url, "SELECT session_id, config FROM adviser_live_sessions WHERE status = 'queued'", ())
        assert q["config"]["method"] == "v0.7"
        ep.run(q["session_id"], fx.T(4, 8))
        # ---- 03:45: incompatible first ARM -> no directional support ----------------------------------------------
        st = ep.at(fx.T(3, 45))
        v = st["view"]
        run = v["run_id"]
        assert st["session"]["method"] == "v0.7" and v["method"] == "v0.7"
        mv = v["market_view"]
        assert (mv["table_row"], mv["expected_direction"], mv["principal"]) == ("WATCH_ONLY", "UNCERTAIN", None)
        assert mv["reasons"][0].startswith("observed hypotheses without current directional support: A LONG ARMED")
        [a] = [s for s in v["scenarios"] if s["family"] == "A"]
        assert a["status"] == "ARMED" and a["antecedent"].startswith(INCOMPATIBLE)
        assert a["trigger_destination"] == {**a["trigger_destination"], "compatible": False, "threshold": "100900.1",
                                            "destination": "100900", "restored_by_revision": False}
        for reload in (False, True):
            if reload:
                page.reload()
            expect(page.get_by_test_id("live-expected")).to_have_text("Incerta", timeout=15_000)
            inc = page.get_by_test_id("live-incompatible")
            expect(inc).to_contain_text("Scenario riconosciuto, ma la condizione attuale")
            expect(inc).to_contain_text("è già alla destinazione 100.900 o oltre")
            expect(inc).to_contain_text("Non sostiene la direzione")
            expect(inc).to_contain_text("Nella lettura pubblicata non c'è un'aspettativa direzionale sostenuta.")
            expect(inc).not_to_contain_text("Nessun altro scenario")
            expect(page.get_by_test_id("live-reason")).to_contain_text("senza sostegno direzionale attuale")
            expect(page.get_by_test_id("live-reason")).to_contain_text("non conta come sostegno direzionale")
            expect(page.get_by_test_id("live-restored")).to_have_count(0)
        shot("v07-1-long-incompatible-no-support.png")
        # ---- 04:00: compatible REVISE -> support restored only from this publication -------------------------------
        st = ep.at(fx.T(4, 0))
        v = st["view"]
        mv = v["market_view"]
        assert (mv["table_row"], mv["expected_direction"]) == ("CONDITIONAL_SCENARIO", "UP")
        [a] = [s for s in v["scenarios"] if s["family"] == "A"]
        td = a["trigger_destination"]
        assert (td["compatible"], td["previous_anchor_incompatible"], td["restored_by_revision"]) == (True, True, True)
        expect(page.get_by_test_id("live-expected")).to_have_text("Rialzo", timeout=15_000)
        expect(page.get_by_test_id("live-restored")).to_contain_text("La condizione è stata rivista")
        expect(page.get_by_test_id("live-restored")).to_contain_text("solo da questa nuova pubblicazione")
        expect(page.get_by_test_id("live-incompatible")).to_have_count(0)
        shot("v07-2-long-restored-by-revision.png")
        # ---- the operational path is the v0.6 one (live): CONFIRM 04:06:01 (the 04:00 minute straddles the live
        # REVISE publication at 04:00:01 and cannot confirm), the same child state and no call -----------------------
        st = ep.at(fx.T(4, 7))
        from test_mp005_live import session as live_session  # in-process frozen v0.6 live session, same tape
        ref6, _ = live_session(ep.mins, fx.T(4, 7), method="v0.6")
        v6ref = ref6.view()
        def child(view):
            return [(s["status"], s.get("entry_state"), (s.get("waiting") or {}).get("phase"),
                     sorted((s.get("waiting") or {}).get("blockers") or [])) for s in view["scenarios"] if s["family"] == "A"]
        assert child(st["view"]) == child(v6ref) and st["view"]["call"] is None and v6ref.get("call") is None
        _wait(ep.url, "SELECT 1 FROM adviser_journal WHERE run_id = %s AND kind = 'scenario' AND "
                      "record->>'transition' = 'CONFIRM'", (run,))
        with connect(ep.url) as c:
            j7 = _journal(c, run)
        scen = [(r["clock_time"].isoformat()[11:19], r["record"]["transition"], r["record"]["antecedent"].startswith(INCOMPATIBLE))
                for r in j7 if r["kind"] == "scenario" and r["record"]["family"] == "A" and r["origin"] == "LIVE"]
        assert scen[:3] == [("03:30:01", "BIRTH", False), ("03:45:01", "ARM", True), ("04:00:01", "REVISE", False)]
        assert scen[3] == ("04:06:01", "CONFIRM", False)
        calls7 = [r for r in j7 if r["kind"] == "call"]
        assert calls7 == []  # live: the frozen v0.6 child keeps waiting (WAIT_RETURN), identical in both versions
        # ---- Stop, then Start v0.7: the same run is restored, history never duplicated ----------------------------
        ep.stop()
        with connect(ep.url) as c:
            n_stop = len(_journal(c, run))
        ep.clock.set(fx.T(4, 8) + timedelta(seconds=30))
        with connect(ep.url) as c:
            sid2 = lv.start_session(c, "http://x", "v0.7")
        ep2 = Episode(stack, ep.mins, fx.T(4, 8), ep.clock)
        ep2.run(sid2, fx.T(4, 11))
        st = ep2.at(fx.T(4, 10))
        assert st["view"]["run_id"] == run  # same lineage, same method
        with connect(ep.url) as c:
            j7b = _journal(c, run)
        ids = [r["record_id"] for r in j7b]
        assert len(ids) == len(set(ids)) and [r["record_id"] for r in j7b[:n_stop]] == [r["record_id"] for r in j7[:n_stop]]
        page.reload()
        expect(page.get_by_test_id("live-market-reading")).to_be_visible(timeout=15_000)
        shot("v07-3-long-after-restore.png")
        ep2.stop()
        # ---- Start v0.6: a new epoch (METHOD_CHANGED), the v0.7 records untouched (isolation) -----------------------
        ep2.clock.set(fx.T(4, 11) + timedelta(seconds=30))
        with connect(ep.url) as c:
            sid6 = lv.start_session(c, "http://x", "v0.6")
        ep6 = Episode(stack, ep.mins, fx.T(4, 11), ep2.clock)
        ep6.run(sid6, fx.T(4, 14))
        st = ep6.at(fx.T(4, 13))
        assert st["session"]["method"] == "v0.6" and st["view"]["run_id"] != run
        with connect(ep.url) as c:
            notes = c.execute("SELECT diagnostic_log FROM adviser_live_sessions WHERE session_id = %s", (sid6,)).fetchone()
            j7c = _journal(c, run)
        assert [r["record_id"] for r in j7c] == ids  # the v0.7 lineage is never continued or rewritten by v0.6
        assert "METHOD_CHANGED:v0.7->v0.6" in str(notes["diagnostic_log"])
        v6 = st["view"]
        r6 = [s for s in v6["scenarios"] if s["family"] == "A"]
        assert all("trigger_destination" not in s for s in r6)  # frozen v0.6 publishes no v0.7 verdict
        assert not errors, errors
        record(evidence_dir, "e2e-v07-long-revision", {
            "note": "synthetic engineering tape, technical proof without economic meaning",
            "run_v07": run, "scenario_records_live": scen, "calls_v07": len(calls7),
            "restore": {"same_run": True, "records_before_stop": n_stop, "records_after_restart": len(ids),
                        "duplicates": 0},
            "v06_isolation": {"run": v6["run_id"], "reset": "METHOD_CHANGED:v0.7->v0.6"}, "screenshots": shots})
    finally:
        ctx.close()
        ep.stop()
        if ep6 is not None:
            ep6.stop()


def test_v07_short_threshold_exactly_at_the_destination(stack, browser, evidence_dir):  # noqa: F811
    ep = Episode(stack, fx.short(fx.hold(fx.H_AT)), START)
    ctx, page, errors = _page(browser)
    try:
        with connect(ep.url) as c:
            ep.run(lv.start_session(c, "http://x", "v0.7"), fx.T(3, 50))
        st = ep.at(fx.T(3, 45))
        v = st["view"]
        [a] = [s for s in v["scenarios"] if s["family"] == "A"]
        assert a["direction"] == "SHORT" and a["status"] == "ARMED"
        td = a["trigger_destination"]
        assert (td["compatible"], td["threshold"], td["destination"]) == (False, "99100.0", "99100")  # T = B exactly
        assert v["market_view"]["table_row"] == "WATCH_ONLY" and v["market_view"]["principal"] is None
        page.goto(f"{stack.base}/#market")
        inc = page.get_by_test_id("live-incompatible")
        expect(inc).to_contain_text("Scenario SHORT A: Scenario riconosciuto", timeout=15_000)
        expect(inc).to_contain_text("è già alla destinazione 99.100 o oltre")
        expect(page.get_by_test_id("live-reason")).to_contain_text("chiusura a 1 minuto ≤ 99.100")
        page.screenshot(path=str(evidence_dir / "v07-4-short-threshold-at-b.png"), full_page=True)
        assert not errors, errors
    finally:
        ctx.close()
        ep.stop()


def test_v07_another_valid_scenario_keeps_the_directional_reading(stack, browser, evidence_dir):  # noqa: F811
    start = fx.T(7, 31)
    ep = Episode(stack, fx.valid_and_incompatible(), start)
    ctx, page, errors = _page(browser)
    try:
        with connect(ep.url) as c:
            ep.run(lv.start_session(c, "http://x", "v0.7"), fx.T(7, 50))
        st = ep.at(fx.T(7, 45))
        v = st["view"]
        mv = v["market_view"]
        assert (mv["table_row"], mv["expected_direction"]) == ("CONDITIONAL_SCENARIO", "UP")
        assert mv["principal"]["status"] == "CONFIRMED"  # the valid scenario (confirmed at 04:01, reconstructed)
        inc = [s for s in v["scenarios"] if (s.get("trigger_destination") or {}).get("compatible") is False]
        assert len(inc) == 1 and inc[0]["status"] == "ARMED"
        assert [w["status"] for w in mv["watch"]] == ["ARMED"] and mv["alternatives"] == []
        page.goto(f"{stack.base}/#market")
        expect(page.get_by_test_id("live-expected")).to_have_text("Rialzo", timeout=15_000)
        expect(page.get_by_test_id("live-incompatible")).to_contain_text("Un altro scenario (LONG A) sostiene la lettura corrente.")
        page.screenshot(path=str(evidence_dir / "v07-5-long-valid-scenario-present.png"), full_page=True)
        assert not errors, errors
    finally:
        ctx.close()
        ep.stop()


def test_v07_incompatible_note_translates_only_the_published_reading(stack, browser, evidence_dir):  # noqa: F811
    """TRANSLATION TEST, NOT AN INTEGRATED ENGINE PROOF. The base payload is the real v0.7 live view of the SHORT
    ``hold(H_AT)`` tape at 03:45 (incompatible SHORT A, WATCH_ONLY); the worker is then stopped and the cockpit is
    served PREPARED variants that change only ``market_view.table_row``/``expected_direction``/``principal``. They prove
    that the note beside an incompatible scenario repeats the published MarketView and never deduces "no other support"
    from an absent principal; they do not claim the engine publishes these combinations on this tape."""
    ep = Episode(stack, fx.short(fx.hold(fx.H_AT)), START)
    try:
        with connect(ep.url) as c:
            ep.run(lv.start_session(c, "http://x", "v0.7"), fx.T(3, 50))
        base = ep.at(fx.T(3, 45))
    finally:
        ep.stop()
    mv0 = base["view"]["market_view"]
    assert (mv0["table_row"], mv0["principal"]) == ("WATCH_ONLY", None)
    other = {"scenario_id": "prepared-other", "family": "B", "direction": "LONG", "status": "ARMED",
             "trigger_level": "100500", "destination": "101200", "invalidation_level": "99800"}

    def prepared(**mv) -> dict:
        p = copy.deepcopy(base)
        p["view"]["market_view"].update(mv)
        return p

    cases = [  # (served body, expected direction label, sentence that must appear)
        (base, "Incerta", "Nella lettura pubblicata non c'è un'aspettativa direzionale sostenuta."),
        (prepared(table_row="CONDITIONAL_SCENARIO", expected_direction="UP", conditional=True, principal=other),
         "Rialzo", "Un altro scenario (LONG B) sostiene la lettura corrente."),
        (prepared(table_row="OPPOSING_SCENARIOS", expected_direction="UNCERTAIN", principal=None),
         "Incerta", "Esistono sostegni direzionali opposti: la lettura non indica una direzione unica."),
        (prepared(table_row="REQUIRED_CONTEXT_UNAVAILABLE", expected_direction="UNAVAILABLE", principal=None),
         "Non disponibile", "Il sistema non può pubblicare una lettura direzionale corrente."),
    ]
    sentences = [c[2] for c in cases]
    cur = {"body": base}
    ctx, page, errors = _page(browser)
    try:
        page.route("**/api/adviser/live", lambda r: r.fulfill(status=200, body=json.dumps(cur["body"]),
                                                              headers={"content-type": "application/json"}))
        page.goto(f"{stack.base}/#market")
        for body, label, sentence in cases:
            cur["body"] = body
            page.reload()
            expect(page.get_by_test_id("live-expected")).to_have_text(label, timeout=15_000)
            inc = page.get_by_test_id("live-incompatible")
            expect(inc).to_contain_text("Scenario SHORT A: Scenario riconosciuto")
            expect(inc).to_contain_text(sentence)
            for s in sentences:
                if s != sentence:
                    expect(inc).not_to_contain_text(s)
            expect(inc).not_to_contain_text("Nessun altro scenario")
        # a CONDITIONAL_SCENARIO row without a published principal states nothing beyond the scenario itself
        cur["body"] = prepared(table_row="CONDITIONAL_SCENARIO", expected_direction="UP", conditional=True, principal=None)
        page.reload()
        expect(page.get_by_test_id("live-expected")).to_have_text("Rialzo", timeout=15_000)
        inc = page.get_by_test_id("live-incompatible")
        expect(inc).to_contain_text("Scenario SHORT A: Scenario riconosciuto")
        for s in sentences:
            expect(inc).not_to_contain_text(s)
        expect(inc).not_to_contain_text("Nessun altro scenario")
        assert not errors, errors
    finally:
        ctx.close()
