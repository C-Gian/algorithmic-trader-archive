"""WP-015 live path for v0.6 (mocked services and synthetic tapes only; never an Owner live session).

Live, MP-005 adds only the cost-independent CORRIDOR terminal (§3.1): a reference preparable under MP-004 (complete
close and current side price inside the corridor and admissible) whose confirming close could never lie in the
corridor ends the child in its preparation dispatch. An economic incompatibility is never a live terminal (§3.3): the
child keeps waiting and the MP-004 temporary cost restriction applies; at the first recovery any remaining impediment
consumes it by the existing rules. Quotes: ``feed6`` sends bid = ask = close unless a minute has an override."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import adviser6_fixtures as fx
import pytest
from test_adviser_live import COMPAT, Clock, _persisted, fetcher
from test_mp004_live import START

from algotrader.adviser import live as lv
from algotrader.adviser.core import Quote
from algotrader.adviser.core6 import CORRIDOR, REASON
from algotrader.feed.contracts import Family

MIN = timedelta(minutes=1)
WIDE = (Decimal(99880), Decimal(100120))  # mid 100000, half-spread 12 bps -> K 26 bps: empty region in the corridor


def feed6(sess, clock, mins, start, end, quotes=None, short=False):
    quotes = quotes or {}
    t = start
    while t < end:
        m = mins[int((t - (fx.DAY2 - timedelta(days=1))) / MIN)]
        close = t + MIN
        clock.t = close + timedelta(milliseconds=500)
        bid, ask = quotes.get(t, (m.c, m.c))
        if short and t in quotes:  # reflect the LONG quote (x -> 200000 - x swaps bid and ask)
            bid, ask = 200000 - ask, 200000 - bid
        sess.on_quote(Quote(bid, ask, clock.t, clock.t, "BTC-USDT-SWAP", "q" * 64), clock.t)
        clock.t = close + timedelta(seconds=1)
        for fam in (Family.TRADE_BAR_1M, Family.MARK_BAR_1M, Family.INDEX_BAR_1M):
            ohlc = (m.o, m.h, m.lo, m.c) if fam == Family.TRADE_BAR_1M else (m.c, m.c, m.c, m.c)
            sess.on_live_bar(fam, t, ohlc, ("100", "1", str(m.c)), clock.t)
        clock.t = close + timedelta(milliseconds=1500)
        sess.tick(clock.t)
        t = close


def session(mins, until, quotes=None, short=False, method="v0.6"):
    clock = Clock(START + timedelta(seconds=30))
    sess = lv.LiveSession(compat=COMPAT, build="test", clock=clock, method=method)
    sess.start(None, fetcher(mins))
    sess.on_connection("CONNECTED", clock.t)
    feed6(sess, clock, mins, START, until, quotes, short)
    return sess, clock


def a_ents(journal):
    return [e["record"] for e in journal if e["kind"] == "entry_attempt" and e["record"]["scenario_id"][:2] in ("AL", "AS")
            and e["record"]["transition"] != "BLOCKERS"]


def tape(side, ref, *post):
    ms = fx.live_tape6(ref, *post)
    return ms if side == "L" else fx.mirror(ms)


@pytest.mark.parametrize("side", ["L", "S"])
def test_live_corridor_terminal_after_a_preparable_reference(side):
    """MP-005 §3.1 live: REF_COR (H0 at the corridor top) is a usable MP-004 return (close and side price 99995 in the
    corridor, admissible at K 14 bps) and prepares at its live dispatch; F misses the corridor -> CORRIDOR terminal in
    that dispatch, cost-independent; no call, no alert, the scenario not invalidated."""
    sess, _ = session(tape(side, fx.REF_COR, *fx.neutral(6)), fx.T(4, 9), short=side == "S")
    core = sess.driver.rt.core
    assert core.cfg.method.model == "btc.context-action.v0.6" and core.cfg.method.implementation == "adviser.core.v6"
    assert lv._session_identity(sess)["method"] == "v0.6"
    journal, _, _ = sess.driver.take()
    ents = a_ents(journal)
    assert [(r["transition"], r["env"]["origin"]) for r in ents] == [
        ("WAIT_OPEN", "LIVE"), ("RESPONSE_REFERENCE", "LIVE"), ("TERMINAL", "LIVE")]
    ref, end = ents[1], ents[2]
    assert ref["env"]["clock_time"] == end["env"]["clock_time"] == "2025-09-01T04:04:01Z"
    assert ref["geometry"]["K_cost"] == "14" and ref["geometry"]["price"] == ("99995" if side == "L" else "100005")
    assert end["reason"] == f"{REASON}:{CORRIDOR}"
    resp = end["response"]
    assert (resp["execution_profile"], resp["economic_basis"], resp["A0"], resp["J0"]) == (
        "LIVE", "NOT_A_TERMINAL_BASIS_LIVE", None, None)
    assert resp["incompatibility_annotations"] is None and resp["F_cap_C0"] is None
    assert not [e for e in journal if e["kind"] == "call"]
    assert not [e for e in journal if e["kind"] == "material_change" and e["record"]["alertable"]]
    [row] = [s for s in sess.view()["scenarios"] if s["family"] == "A"]
    assert row["status"] == "CONFIRMED" and row["entry_ended"]["base"] == CORRIDOR
    assert row["entry_ended"]["scenario_invalidated"] is False and "waiting" not in row


@pytest.mark.parametrize("side", ["L", "S"])
def test_live_economic_incompatibility_is_never_a_terminal(side):
    """MP-005 §3.3: REF_ECON (F meets the corridor but not the region at 14 bps) keeps waiting live; the recovery
    100014.6 is then evaluated once on the ask and is not issuable by the existing reward/risk rule (R = N = 1). The same
    reference is a HISTORICAL_ECONOMICS terminal in the historical profile (test_mp005_paths)."""
    sess, _ = session(tape(side, fx.REF_ECON, fx.neutral(1)[0], fx.ECON_RECOVERY), fx.T(4, 9), short=side == "S")
    journal, _, _ = sess.driver.take()
    ents = a_ents(journal)
    assert [r["transition"] for r in ents] == ["WAIT_OPEN", "RESPONSE_REFERENCE", "TERMINAL"]
    assert ents[2]["env"]["clock_time"] == "2025-09-01T04:06:01Z"  # the recovery dispatch, not the preparation
    assert ents[2]["reason"] == "RESPONSE_NOT_ISSUABLE:REWARD_RISK_BELOW_MINIMUM"
    assert ents[2]["response"]["outcome"] == "NOT_ISSUABLE" and "incompatibility_base" not in ents[2]["response"]


@pytest.mark.parametrize("side", ["L", "S"])
def test_live_temporary_cost_restriction_then_recovery_and_issue(side):
    """MP-005 §9 L1-L3 analogue: L1 the reference prepares with a fresh 14 bps quote; L2 during WAIT_RESPONSE a wide
    quote (K 26 bps) empties the current region while the bar neither confirms nor contradicts (low = L0): no terminal,
    still waiting; L3 the quote is restored and the valid recovery is issued on the side price."""
    eq = fx.minute(99995, 100005, 99990, 100000)  # contrary equality (low = L0), no favourable close
    mins = tape(side, fx.REF, fx.neutral(1)[0], eq, fx.VALID)
    sess, clock = session(mins, fx.T(4, 6), quotes={fx.T(4, 5): WIDE}, short=side == "S")
    w = next(iter(sess.driver.rt.core.waits.values()))
    assert w.phase == "WAIT_RESPONSE" and w.checked == 2  # straddling bar + the L2 bar, the child still open
    k = sess.driver.rt.core._side_price(1 if side == "L" else -1, fx.T(4, 6) + timedelta(seconds=1))[2]
    assert k == Decimal(26)
    journal, _, _ = sess.driver.take()
    assert [r["transition"] for r in a_ents(journal)] == ["WAIT_OPEN", "RESPONSE_REFERENCE"]
    feed6(sess, clock, mins, fx.T(4, 6), fx.T(4, 8))  # L3: bid = ask = close again (14 bps)
    journal, _, _ = sess.driver.take()
    ents = a_ents(journal)
    assert [r["transition"] for r in ents] == ["ISSUE"] and ents[0]["env"]["clock_time"] == "2025-09-01T04:07:01Z"
    [call] = [e["record"] for e in journal if e["kind"] == "call"]
    assert call["actionability"]["side_price"] == ("100012" if side == "L" else "99988")


def _stop_restart(legacy_stopped: bool) -> dict:
    """A v0.6 call AVAILABLE, the Owner's Stop at 04:07:03, Start at 04:12:30. ``legacy_stopped`` reproduces a state
    saved BEFORE the orchestrator decision of 11 October 2026, whose worker taped the Stop as a STOPPED connection
    command left pending in the saved runtime."""
    mins = tape("L", fx.REF, fx.neutral(1)[0], fx.minute(99995, 100005, 99990, 100000), fx.VALID)
    s1, clock = session(mins, fx.T(4, 7), quotes={fx.T(4, 5): WIDE})
    assert s1.driver.rt.core.call.entry == "AVAILABLE"
    j0, _, t0 = s1.driver.take()  # everything up to the Stop
    view0 = s1.view()
    clock.t = fx.T(4, 7) + timedelta(seconds=3)
    if legacy_stopped:
        s1.on_connection("STOPPED", clock.t)
    s1.stopped(clock.t)
    j1, _, t1 = s1.driver.take()  # what the Stop itself wrote and taped
    p = {**_persisted(s1), "method": "v0.6"}  # as LiveStore.load_state
    clock.t = fx.T(4, 12) + timedelta(seconds=30)
    s2 = lv.LiveSession(compat=COMPAT, build="test", clock=clock, method="v0.6")
    s2.start(p, fetcher(mins))
    j2, _, t2 = s2.driver.take()
    return {"s1": s1, "s2": s2, "view0": view0, "j0": j0, "t0": t0, "j1": j1, "t1": t1, "j2": j2, "t2": t2}


def _calls(journal: list[dict]) -> list[tuple]:
    return [(e["kind"], e["clock_time"], {k: v for k, v in e["record"].items() if k != "env"}) for e in journal
            if e["kind"] in ("call", "call_revision", "material_change")]


def test_stop_is_a_session_event_and_a_legacy_pending_stopped_never_governs_the_restore():
    """Orchestrator decision (11 October 2026): STOPPED is a session event, never an engine input or a call revision.
    The Stop keeps the last assessment (historical AVAILABLE, same clock); at Start the existing gap rule ends the
    thesis UNASSESSABLE at the restored processing point. A STOPPED left pending by a pre-decision worker is superseded
    at its own instant (same dispatch) and changes nothing: the same call records as a restore without it, no alert,
    and the run's input tape (both sessions) still reproduces the journal."""
    r = _stop_restart(legacy_stopped=False)
    assert r["j1"] == [] and r["t1"] == []  # the Stop wrote and taped nothing in the engine
    v = r["s1"].view()
    assert v["status"] == "STOPPED" and not v["connected"]
    assert (v["clock"], v["call"]) == (r["view0"]["clock"], r["view0"]["call"])  # the kept assessment, unchanged
    assert v["call"]["entry_status"] == "AVAILABLE"  # historical; the API serves it as UNVERIFIED / not current
    assert r["s1"].notes[-1] == {"at": "2025-09-01T04:07:03+00:00", "event": "stopped"}  # its actual time
    revs = [e["record"] for e in r["j2"] if e["kind"] == "call_revision"]
    assert [(x["thesis_status"], x["terminal_reason"]) for x in revs] == [("UNASSESSABLE", "RESTART_GAP_OVERLAPS_THESIS")]
    assert r["s2"].driver.rt.core.connection["state"] == "DISCONNECTED" and lv.alerts_from(r["j2"], "run") == []

    old = _stop_restart(legacy_stopped=True)
    assert [c["state"] for c in old["t1"] if c["cmd"] == "connection"] == ["STOPPED"]  # taped by the old worker
    assert old["j1"] == []  # pending at the save: no revision at the Stop
    assert any(n["event"] == "pending_stop_superseded" and n["stop_at"] == "2025-09-01T04:07:03+00:00"
               for n in old["s2"].notes)
    assert old["s2"].driver.rt.core.connection["state"] == "DISCONNECTED"
    assert not [p for p in old["s2"].driver.rt.pending if p[2] == "connection"]
    assert _calls(old["j2"]) == _calls(r["j2"]) and lv.alerts_from(old["j2"], "run") == []
    d = lv.replay_tape(old["t0"] + old["t1"] + old["t2"], lv.live_config(COMPAT, "test", "v0.6"),
                       old["s1"].epoch.cov_from)
    assert [e["digest"] for e in d.take()[0]] == [e["digest"] for e in old["j0"] + old["j1"] + old["j2"]]


def test_live_restart_after_the_initial_terminal_never_reopens_or_reprepares():
    mins = fx.live_tape6(fx.REF_COR, *fx.neutral(30))
    s1, clock = session(mins, fx.T(4, 7))
    assert not s1.driver.rt.core.waits
    s2 = lv.LiveSession(compat=COMPAT, build="test", clock=clock, method="v0.6")
    s2.start({**_persisted(s1), "method": "v0.6"}, fetcher(mins))  # as LiveStore.load_state: the lineage's method
    assert s2.epoch.run_id == s1.epoch.run_id  # a real resume of the same v0.6 run, not a method-change reset
    assert not s2.driver.rt.core.waits
    assert not [e for e in s2.driver.take()[0] if e["kind"] == "entry_attempt"
                and e["record"]["transition"] in ("RESPONSE_REFERENCE", "WAIT_OPEN")]


def test_v06_live_input_tape_reproduces_the_same_semantic_outputs():
    sess, _ = session(fx.live_tape6(fx.REF_COR, *fx.neutral(6)), fx.T(4, 9))
    journal, _, tape_ = sess.driver.take()
    d = lv.replay_tape(tape_, lv.live_config(COMPAT, "test", "v0.6"), sess.epoch.cov_from)
    j2, _, _ = d.take()
    assert [e["digest"] for e in j2] == [e["digest"] for e in journal]


def test_restart_from_a_v05_lineage_resets_continuity_instead_of_converting_it():
    mins = fx.h1_economics()
    clock = Clock(START + timedelta(seconds=30))
    s1 = lv.LiveSession(compat=COMPAT, build="test", clock=clock, method="v0.5")
    s1.start(None, fetcher(mins))
    s2 = lv.LiveSession(compat=COMPAT, build="test", clock=clock, method="v0.6")
    s2.start({**_persisted(s1), "method": "v0.5"}, fetcher(mins))
    assert s2.epoch.run_id != s1.epoch.run_id
    assert any(n.get("reason") == "METHOD_CHANGED:v0.5->v0.6" for n in s2.notes)


@pytest.mark.db
def test_start_session_records_v06(database_url):
    from pack_fixtures import connect

    from algotrader.adviser.api import live_status

    with connect(database_url) as c:
        c.execute("DELETE FROM adviser_live_sessions")
        sid = lv.start_session(c, "http://x", "v0.6")
        row = c.execute("SELECT config FROM adviser_live_sessions WHERE session_id = %s", (sid,)).fetchone()
        assert row["config"]["method"] == "v0.6" and live_status(c)["session"]["method"] == "v0.6"
        lv.stop_session(c, sid)
