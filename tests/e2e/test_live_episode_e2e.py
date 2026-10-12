"""Integrated synthetic acceptance check of the live adviser v0.6 (E2E, 12 October 2026): ONE episode from the ordinary
Start to the conclusion of one call, through the REAL path - cockpit Start button -> API -> the live worker (bounded
catch-up, WARMING_UP, LIVE activation) -> engine -> persistence (session row, journal, alerts) -> API -> cockpit.

TECHNICAL PROOF WITHOUT ECONOMIC MEANING. The input is the synthetic MP-005 LONG tape of ``tests/test_mp005_live.py``
(L1-L3: REF, neutral, EQ, VALID) plus the three later minutes of the call-updates episode, served by the existing
offline WP-009 fakes (mocked OKX REST/WebSocket/ticker; no network, no Owner data). The tape is designed to satisfy the
frozen v0.6 rules; nothing is put into the state directly and no gate, readiness or timestamp is altered. The only test
control is WHEN the scripted pushes are released (``FakeWS.until``), so each phase can be read while the fake clock is
held.

Phases (UTC, synthetic day 2025-09-01):
- Start 03:16:30: 96 h catch-up RECONSTRUCTED, WARMING_UP (no current advice), LIVE activation 03:17:01.
- Conditional expectation: scenario A LONG armed at 03:45:01 -> MarketView UP *conditional*; confirmed at 04:02:01;
  return reference prepared at 04:04:01 (H0 100008, L0 99990). Expectation is not entry availability.
- DISCRIMINATING CONDITION (v0.6 inherits the MP-004 RETURN response): after the prepared reference a call is possible
  only on "a later complete 1m close >= 100008.1 with low >= 99990" (local recovery). At 04:06:01 the bar
  [04:05,04:06) (EQ: close 100000, low 99990) does not satisfy it: WAIT_RESPONSE, no call, cockpit WAITING. At 04:07:01
  the bar [04:06,04:07) (VALID: close 100012, low 99992) satisfies it: call issued, entry AVAILABLE.
- Update of the same call: entry UNVERIFIED (QUOTE_STALE timer, r1) then CLOSED (price outside the structural area,
  r2), thesis ONGOING.
- Conclusion of the same call: TARGET_REACHED at 04:10:01 (certified contact by the bar [04:09,04:10), high 100720 >=
  target 100700.0)."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta

import adviser6_fixtures as fx
import pytest
from playwright.sync_api import expect

from test_ui_smoke import ROOT, browser, evidence_dir, record, stack  # noqa: F401

pytestmark = [pytest.mark.e2e, pytest.mark.db]
sys.path.insert(0, str(ROOT / "tests"))
from pack_fixtures import connect  # noqa: E402
from test_adviser_live_db import FakeClock, _run_worker, _wait, ws_messages  # noqa: E402
from test_mp004_live import START  # noqa: E402
from test_mp005_live import tape  # noqa: E402

from algotrader.adviser import live as lv  # noqa: E402

EQ = fx.minute(99995, 100005, 99990, 100000)  # [04:05,04:06): contrary equality, no favourable close
POST = [fx.minute(100010, 100120, 100005, 100100),  # [04:07,04:08) closes above the structural area top 100049.9
        fx.minute(100100, 100320, 100090, 100300),  # [04:08,04:09)
        fx.minute(100300, 100720, 100290, 100710)]  # [04:09,04:10) high beyond the target 100700.0
HOLD = timedelta(seconds=1, milliseconds=300)  # after a minute closes: its completed pushes (+1 s) and duplicate (+1.25 s)


def _iso(t: datetime) -> str:
    return t.isoformat()


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _journal(c, run: str) -> list[dict]:
    return c.execute("SELECT seq, kind, record_id, subject, clock_time, origin, record FROM adviser_journal "
                     "WHERE run_id = %s ORDER BY seq", (run,)).fetchall()


def _causal(rec: dict) -> bool:
    """Every dependency of a record was known at or before the record's own dispatch (admitted prefix only)."""
    env = rec["env"]
    return all(_ts(d["known_at"]) <= _ts(env["clock_time"]) for d in env["dependencies"] if d.get("known_at"))


def test_one_v06_episode_from_start_to_conclusion_through_worker_api_and_cockpit(stack, browser, evidence_dir):  # noqa: F811
    url = stack.env["ALGOTRADER_DATABASE_URL"]
    mins = tape("L", fx.REF, fx.neutral(1)[0], EQ, fx.VALID, *POST)
    assert (mins[fx.index_of(fx.T(4, 5))], mins[fx.index_of(fx.T(4, 6))]) == (EQ, fx.VALID)
    clock = FakeClock(START + timedelta(seconds=30))
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000}, timezone_id="Europe/Rome")
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    panel = page.get_by_test_id("live-call")
    th = sid = None
    shots: list[str] = []

    def shot(name: str) -> None:
        page.screenshot(path=str(evidence_dir / name), full_page=True)
        shots.append(name)

    def no_availability_shown() -> None:
        expect(page.get_by_test_id("live-admissible")).to_have_count(0)
        expect(page.locator(".sig-avail")).to_have_count(0)
        expect(page.locator(".band-admissible")).to_have_count(0)

    def step(t: datetime, sql: str, args: tuple) -> dict:
        ws.until = t
        return _wait(url, sql, args)

    try:
        # ---- ordinary Start from the cockpit (method v0.6) -> catch-up, WARMING_UP ---------------------------------
        page.goto(f"{stack.base}/#market")
        page.get_by_test_id("live-method-select").select_option("v0.6")
        page.get_by_test_id("live-start").click()
        q = _wait(url, "SELECT session_id, config FROM adviser_live_sessions WHERE status = 'queued'", ())
        sid = q["session_id"]
        assert q["config"]["method"] == "v0.6"
        th, ws = _run_worker(url, clock, ws_messages(START, fx.T(4, 12), mins), mins)
        _wait(url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'status' = 'WARMING_UP'", (sid,))
        st = stack.get("/api/adviser/live")
        assert st["session"]["session_id"] == sid and st["session"]["method"] == "v0.6"
        assert st["state"] == "WARMING_UP" and not st["current"] and st["view"]["call"] is None
        run = st["view"]["run_id"]
        with connect(url) as c:
            j0 = _journal(c, run)
        assert j0 and {r["origin"] for r in j0} == {"RECONSTRUCTED"}  # catch-up never issues anything live
        assert not [r for r in j0 if r["kind"] in ("call", "entry_attempt")]
        assert not [r for r in j0 if r["kind"] == "market_view" and r["record"]["conditional"]]
        expect(panel).to_have_attribute("data-state", "WAITING", timeout=15_000)
        expect(page.get_by_test_id("live-call-not-current")).to_be_visible()  # not current advice while warming up
        no_availability_shown()
        shot("episode-0-warming-up.png")

        # ---- LIVE; the conditional expectation forms; DISCRIMINATING WAIT at 04:06:01 ------------------------------
        ws.until = START  # nothing beyond the session's own startup until each phase is released
        ws.gate.set()
        t_wait = fx.T(4, 6) + timedelta(seconds=1)  # the EQ bar [04:05,04:06) is decided here
        step(fx.T(4, 6) + HOLD, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND "
             "view->>'clock' = %s", (sid, _iso(t_wait)))
        st = stack.get("/api/adviser/live")
        v = st["view"]
        assert st["state"] == "LIVE" and st["current"] and v["run_id"] == run and v["origin"] == "LIVE"
        mv = v["market_view"]
        assert (mv["expected_direction"], mv["conditional"], mv["table_row"]) == ("UP", True, "CONDITIONAL_SCENARIO")
        aid = mv["principal"]["scenario_id"]
        assert aid.startswith("AL-") and v["call"] is None  # an expectation, not an available entry
        [sa] = [s for s in v["scenarios"] if s["scenario_id"] == aid]
        assert sa["status"] == "CONFIRMED" and sa["call_id"] is None and sa["waiting"]["phase"] == "WAIT_RESPONSE"
        resp = sa["waiting"]["response"]
        assert (resp["H0"], resp["L0"], resp["recovery_close"], resp["bars_checked"]) == ("100008", "99990", "100008.1", 2)
        assert resp["reference_bar"].endswith("#obs@2025-09-01T04:03:00Z")
        last = v["chart"]["minutes"][-1]  # the bar just decided: the necessary condition is NOT met
        assert (last["t"], last["c"], last["l"]) == (_iso(fx.T(4, 5)), "100000", "99990")
        with connect(url) as c:
            j1 = _journal(c, run)
            live_since = _ts(c.execute("SELECT view->>'live_since' AS t FROM adviser_live_sessions WHERE session_id = %s",
                                       (sid,)).fetchone()["t"])
        assert not [r for r in j1 if r["kind"] == "call"]
        assert [r["record"]["transition"] for r in j1 if r["kind"] == "entry_attempt"] == ["WAIT_OPEN",
                                                                                          "RESPONSE_REFERENCE"]
        # the expectation is derived live from admitted observations: UP conditional appears with the scenario ARM
        scen = {r["record"]["transition"]: r for r in j1 if r["kind"] == "scenario" and r["subject"] == aid}
        mvs = [r for r in j1 if r["kind"] == "market_view" and r["record"]["conditional"]]
        assert scen["BIRTH"]["clock_time"] < scen["ARM"]["clock_time"] < scen["CONFIRM"]["clock_time"]
        assert mvs[0]["origin"] == "LIVE" and mvs[0]["clock_time"] == scen["ARM"]["clock_time"] > live_since
        assert mvs[0]["record"]["expected_direction"] == "UP" and mvs[0]["record"]["principal"]["scenario_id"] == aid
        assert all(_causal(r["record"]) for r in j1 if r["kind"] in ("market_view", "scenario", "entry_attempt"))
        page.reload()
        expect(panel).to_have_attribute("data-state", "WAITING", timeout=15_000)
        expect(page.get_by_test_id("live-no-trade")).to_contain_text("In attesa — nessun ingresso proposto")
        expect(page.get_by_test_id("live-expected")).to_have_text("Rialzo")
        expect(page.get_by_test_id("live-direction")).to_contain_text("(condizionale)")
        expect(page.get_by_test_id("live-condition")).to_contain_text("serve una ripresa locale del prezzo")
        expect(page.get_by_test_id("live-updated")).to_contain_text("06:06:01")  # 04:06:01 UTC in Europe/Rome
        expect(page.get_by_test_id("live-call-not-current")).to_have_count(0)
        no_availability_shown()
        shot("episode-1-expectation-waiting.png")

        # ---- condition met at 04:07:01: the call is issued, entry AVAILABLE ---------------------------------------
        t_issue = fx.T(4, 7) + timedelta(seconds=1)
        call_row = step(fx.T(4, 7) + HOLD, "SELECT * FROM adviser_journal WHERE kind = 'call'", ())
        _wait(url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'clock' = %s", (sid, _iso(t_issue)))
        _wait(url, "SELECT 1 FROM adviser_alerts WHERE change_type = 'NEW_CALL'", ())
        cid, call = call_row["record_id"], call_row["record"]
        assert call_row["run_id"] == run and call_row["origin"] == "LIVE"
        assert call["scenario_id"] == aid and call_row["subject"] == f"{aid}#entry"  # the scenario's entry child
        assert call_row["clock_time"] == t_issue and _ts(call["issued_at"]) == t_issue == _ts(call["env"]["published_at"])
        assert call["issue_reference"] == "100012" and _causal(call)  # the VALID close, known at its receipt
        trade1m = next(d for d in call["env"]["dependencies"] if d["name"] == "trade.1m")
        assert trade1m["latest_ref"].endswith("#obs@2025-09-01T04:06:00Z") and _ts(trade1m["known_at"]) <= t_issue
        st = stack.get("/api/adviser/live")
        c0 = st["view"]["call"]
        assert st["current"] and st["view"]["market_view"]["conditional"] is True  # the expectation stays an expectation
        assert (c0["call_id"], c0["revision"], c0["entry_status"], c0["thesis_status"]) == (cid, 0, "AVAILABLE", "ONGOING")
        assert (c0["direction"], c0["admissible_bounds"], c0["target"], c0["stop"]) == (
            "LONG", ["99900", "100014.4"], "100700.0", "99700.0")
        assert c0["structural_area"] == call["structural_area"] and c0["target"] == call["target"]
        assert [(a["change_type"], a["subject_id"]) for a in st["alerts"]] == [("NEW_CALL", cid)]
        page.reload()
        expect(panel).to_have_attribute("data-state", "AVAILABLE", timeout=15_000)
        expect(page.get_by_test_id("live-entry")).to_contain_text("Ingresso disponibile secondo il sistema")
        expect(page.get_by_test_id("live-admissible")).to_have_text("99.900 – 100.014,4")
        expect(page.get_by_test_id("live-target")).to_have_text("100.700")
        expect(page.get_by_test_id("live-stop-guidance")).to_have_text("99.700")
        expect(page.get_by_test_id("live-call-direction")).to_contain_text("LONG")
        expect(page.locator(".band-admissible")).to_have_count(1)
        expect(page.get_by_test_id("live-updated")).to_contain_text("06:07:01")
        expect(page.get_by_test_id("live-call-history-open")).to_contain_text("r0")
        shot("episode-2-entry-available.png")

        # ---- update of the SAME call at 04:08:01: entry CLOSED, thesis ongoing -------------------------------------
        t_upd = fx.T(4, 8) + timedelta(seconds=1)
        step(fx.T(4, 8) + HOLD, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND "
             "view->>'clock' = %s", (sid, _iso(t_upd)))
        st = stack.get("/api/adviser/live")
        c2 = st["view"]["call"]
        assert st["current"] and (c2["call_id"], c2["revision"], c2["entry_status"], c2["thesis_status"]) == (
            cid, 2, "CLOSED", "ONGOING")
        assert c2["entry_reasons"] == ["PRICE_OUTSIDE_STRUCTURAL_AREA", "REWARD_RISK_BELOW_MINIMUM"]
        with connect(url) as c:
            revs = [r for r in _journal(c, run) if r["kind"] == "call_revision"]
        assert [(r["subject"], r["record"]["revision"], r["record"]["entry_status"], r["record"]["entry_reasons"])
                for r in revs] == [(cid, 1, "UNVERIFIED", ["QUOTE_STALE"]),
                                   (cid, 2, "CLOSED", ["PRICE_OUTSIDE_STRUCTURAL_AREA", "REWARD_RISK_BELOW_MINIMUM"])]
        assert t_issue < revs[0]["clock_time"] < revs[1]["clock_time"] <= t_upd
        page.reload()
        expect(panel).to_have_attribute("data-state", "CLOSED", timeout=15_000)
        expect(page.get_by_test_id("live-entry")).to_contain_text("Ingresso non disponibile adesso")
        expect(page.get_by_test_id("live-entry-reasons")).to_contain_text("prezzo fuori dall'area d'ingresso")
        expect(page.get_by_test_id("live-thesis")).to_have_text("ancora valida")
        expect(page.get_by_test_id("live-call-history-open")).to_contain_text("r2")
        expect(page.get_by_test_id("live-updated")).to_contain_text("06:08:01")
        no_availability_shown()
        shot("episode-3-update-entry-closed.png")

        # ---- conclusion of the SAME call at 04:10:01: TARGET_REACHED ----------------------------------------------
        t_end = fx.T(4, 10) + timedelta(seconds=1)
        term = step(fx.T(4, 10) + HOLD, "SELECT * FROM adviser_journal WHERE kind = 'call_revision' "
                    "AND record->>'thesis_status' <> 'ONGOING'", ())
        _wait(url, "SELECT 1 FROM adviser_live_sessions WHERE session_id = %s AND view->>'clock' = %s", (sid, _iso(t_end)))
        _wait(url, "SELECT 1 FROM adviser_alerts WHERE change_type = 'TERMINAL'", ())
        with connect(url) as c:
            rows = _journal(c, run)
            runs = {r["run_id"] for r in c.execute("SELECT DISTINCT run_id FROM adviser_journal").fetchall()}
            alerts = c.execute("SELECT change_type, subject_id FROM adviser_alerts ORDER BY created_at").fetchall()
        revs = [r for r in rows if r["kind"] == "call_revision"]
        assert runs == {run} and [r["seq"] for r in rows] == list(range(1, len(rows) + 1))
        assert [r["record_id"] for r in rows if r["kind"] == "call"] == [cid]  # one call, never reissued
        assert {r["subject"] for r in revs} == {cid} and [r["record"]["revision"] for r in revs] == list(range(1, 8))
        assert all(a["clock_time"] <= b["clock_time"] for a, b in zip(revs, revs[1:], strict=False))
        assert all(_ts(r["record"]["env"]["published_at"]) == r["clock_time"] and _causal(r["record"]) for r in revs)
        assert [r for r in revs if r["record"]["thesis_status"] != "ONGOING"] == [revs[-1]]
        assert term["record_id"] == revs[-1]["record_id"] and term["clock_time"] == t_end
        assert (term["record"]["thesis_status"], term["record"]["terminal_reason"]) == (
            "TARGET_REACHED", "CERTIFIED_TARGET_CONTACT:okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-09-01T04:09:00Z")
        assert not [r for r in revs if r["record"]["entry_status"] == "AVAILABLE"]  # never re-proposed after r0
        assert [(a["change_type"], a["subject_id"]) for a in alerts] == [
            ("NEW_CALL", cid), ("ENTRY_UNVERIFIED", cid), ("TERMINAL", cid)]
        st = stack.get("/api/adviser/live")
        assert st["current"] and st["session"]["session_id"] == sid and st["view"]["call"] is None
        [rc] = [x for x in st["view"]["recent_calls"] if x["call_id"] == cid]
        assert (rc["terminal"], _ts(rc["terminal_at"])) == ("TARGET_REACHED", t_end)
        detail = stack.get(f"/api/adviser/runs/{run}/calls/{cid}")
        assert detail["call"]["call_id"] == cid and detail["revisions"] == [r["record"] for r in revs]
        page.reload()
        expect(panel).to_have_attribute("data-state", "WAITING", timeout=15_000)
        expect(page.get_by_test_id("live-call-identity")).to_contain_text("Conclusa — target raggiunto")
        expect(page.get_by_test_id("live-call-concluded")).to_have_attribute("data-terminal", "TARGET_REACHED")
        expect(page.get_by_test_id("live-concluded-target")).to_have_text("100.700 — raggiunto")
        expect(page.get_by_test_id("live-concluded-separation")).to_contain_text("non prolunga questa call")
        expect(page.get_by_test_id("live-updated")).to_contain_text("06:10:01")
        no_availability_shown()
        shot("episode-4-conclusion.png")
        page.get_by_test_id("timeline-call-history-open").first.click()
        hist = page.get_by_test_id("live-call-history")
        expect(hist.get_by_test_id("history-identity")).to_contain_text(cid)
        expect(hist.get_by_test_id("history-identity")).to_contain_text(run)
        expect(hist.get_by_test_id("history-status-terminal")).to_be_visible()
        expect(hist.get_by_test_id("history-revisions")).to_contain_text("CERTIFIED_TARGET_CONTACT")
        shot("episode-5-call-history.png")
        assert not errors, errors
        record(evidence_dir, "e2e-live-episode-v06", {
            "note": "synthetic engineering tape, technical proof without economic meaning",
            "session_id": sid, "run_id": run, "live_since": _iso(live_since), "scenario_id": aid, "call_id": cid,
            "expectation": {"first_conditional_up_at": _iso(mvs[0]["clock_time"]),
                            "scenario": {k: _iso(scen[k]["clock_time"]) for k in ("BIRTH", "ARM", "CONFIRM")}},
            "discriminating_condition": {
                "rule": resp["recovery_rule"], "reference_bar": resp["reference_bar"],
                "before": {"decided_at": _iso(t_wait), "bar": last, "served_call": None, "cockpit": "WAITING"},
                "after": {"decided_at": _iso(t_issue), "issue_reference": call["issue_reference"],
                          "trade_1m_dependency": trade1m["latest_ref"], "cockpit": "AVAILABLE"}},
            "call": {"issued_at": call["issued_at"], "structural_area": call["structural_area"],
                     "admissible_at_issue": c0["admissible_bounds"], "target": call["target"],
                     "stop": call["invalidation"]},
            "revisions": [{"revision": r["record"]["revision"], "at": _iso(r["clock_time"]),
                           "entry_status": r["record"]["entry_status"], "entry_reasons": r["record"]["entry_reasons"],
                           "thesis_status": r["record"]["thesis_status"],
                           "terminal_reason": r["record"]["terminal_reason"]} for r in revs],
            "alerts": [a["change_type"] for a in alerts],
            "screenshots": shots})
    finally:
        ctx.close()
        if sid is not None:
            with connect(url) as c:
                lv.stop_session(c, sid)
            if th is not None:
                th.join(60)
