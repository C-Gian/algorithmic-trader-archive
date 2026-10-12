"""Hand-designed synthetic paths for the EXPERIMENTAL v0.6-a2x second-attempt variant (engineering inputs, NOT market
data). Every tape starts from the cold day-1 history of the MP-002 base A LONG path (``adviser3_fixtures.a3_base``):
warmup, readiness, context and scale are produced by the ordinary kernel from these minutes; no scenario, anchor or
call is placed in any state.

Base geometry: impulse A 97000, B 100900, birth S15 2000, z 200 (A+z 97200, B-0.25*S15 100400); birth 03:30, original
expiry H0 05:30; ARM 03:45; REVISE 04:00 (R1 99900, K 100049.9, V 99700); first confirmation 04:01 (close 100050).

``two_calls`` (the main tape): the first attempt's RETURN reference [04:01,04:02) and recovery [04:02,04:03) issue call 1
at 04:03; [04:03,04:04) touches V 99700 -> call 1 and the first attempt INVALIDATED at tf = 04:04, review origin
O = 04:15. The bar [04:00,04:15) contains the failure and is never a new fact. The fresh bar [04:15,04:30) (o 99800
h 100050 l 99650 c 99750: contrary close, R2 99650 < R1 99900) arms the successor at 04:30 (K2 100050, V2 99450). The
minute [04:30,04:31) closes 100050.1 = K2 + tick: second confirmation C2 at 04:31 (59 min before H0). Its child waits
(RETURN): [04:31,04:32) closes outside the corridor (temporary blocker), [04:32,04:33) prepares the local reference
(H0' 99860, L0' 99800), [04:33,04:34) recovers (close 99865): call 2 at 04:34, hard deadline H0 05:30. A walk to
100910 reaches call 2's target then B.

SHORT tapes are the positive-price reflection about 100000 (economics computed independently, never asserted by
reflection).
"""

from __future__ import annotations

from adviser3_fixtures import DAY1, DAY2, D, T, a3_base, bar15, flat, minute, mirror, walk  # noqa: F401
from adviser5_fixtures import REF, VALID

from algotrader.adviser.harness import Minute

V_CONTACT = minute(100012, 100012, 99700, 99950)  # [04:03,04:04): touches V 99700, closes 99950
NEW_BAR = (99800, 100050, 99650, 99750)  # o h l c of the fresh post-failure reaction bar [04:15,04:30)
CONFIRM2 = minute(99750, 100060, 99750, D("100050.1"))  # K2 + tick, low > V2 99450
OUTSIDE2 = minute(D("100050.1"), 100058, 100045, 100055)  # close above the successor's corridor: temporary blocker
REF2 = minute(99850, 99860, 99800, 99820)  # successor's first usable return -> local reference H0' 99860 / L0' 99800
RECOVER2 = minute(99820, 99870, 99810, 99865)  # close >= 99860.1 with low >= 99800: recovery -> call 2


def tail(ms: list, n: int = 420) -> list:
    return ms + flat(n, ms[-1].c)


def first_call_then_failure() -> list:
    """a3 base + call 1 (REF, VALID) + the V contact at [04:03,04:04) + drift to 99800 by 04:15 (to 04:15)."""
    return a3_base() + [REF, VALID, V_CONTACT] + walk(99950, 99800, 11)


def two_calls(after: list | None = None) -> list:
    ms = first_call_then_failure() + bar15(*NEW_BAR) + [CONFIRM2, OUTSIDE2, REF2, RECOVER2]
    return tail(ms + (after if after is not None else walk(99865, 100910, 30)))


def no_call_failure() -> list:
    """S1 confirmed at 04:01 and still waiting (no call 1); V contact [04:01,04:02) -> tf 04:02; then as two_calls."""
    ms = a3_base() + [minute(100050, 100050, 99700, 99950)] + walk(99950, 99800, 13) + bar15(*NEW_BAR)
    return tail(ms + [CONFIRM2, OUTSIDE2, REF2, RECOVER2] + walk(99865, 100910, 30))


def short(ms: list) -> list:
    return mirror(ms)


_ = (DAY1, DAY2, T, Minute)


# -- variants (each states its hand-expected behaviour in the test that uses it) ---------------------------------------

def quiet_bars(p, n: int, step=10) -> list:
    """n 15m bars without a contrary close (first c > o, later c > previous c), lows 20 below the open."""
    out = []
    for _ in range(n):
        out += bar15(p, p + 40, p - 20, p + step, order="LH")
        p += step
    return out


def failure_then_flat(at=99950) -> list:
    """Call 1 then the V contact at [04:03,04:04), then flat at ``at`` to 04:15 (tf 04:04, O 04:15)."""
    return a3_base() + [REF, VALID, V_CONTACT] + flat(11, at, amp=D(0))


def late(quiet: int, recovery: tuple[int, int] | None, hold=None) -> list:
    """After the failure: ``quiet`` bars from 04:15 without new facts, then the qualifying contrary bar (h 100050,
    l 99650, c 99750) -> ARM at 04:15 + 15*(quiet+1); then flat at 99750 until the recovery minute starting at
    T(*recovery) (close 100050.1 = K2 + tick); ``recovery=None``: no recovery."""
    ms = failure_then_flat() + quiet_bars(D(99950), quiet)
    p = ms[-1].c
    ms += bar15(p, 100050, 99650, 99750)
    if recovery is not None:
        n = int((T(*recovery) - (DAY1 + len(ms) * (T(0, 1) - T(0, 0)))) / (T(0, 1) - T(0, 0)))
        ms += flat(n, 99750, amp=D(0)) + [CONFIRM2]
    return tail(ms + (hold if hold is not None else []))


def no_fresh_facts() -> list:
    """After the failure: the bar [04:00,04:15) containing the contact is excluded; [04:15,04:30) has a contrary close
    but its low 99950 is above R1 99900; later bars rise without a contrary close above the old K (100049.9): no
    successor; the review ends at H0 05:30."""
    ms = failure_then_flat(100000) + bar15(100000, 100100, 99950, 99960)
    return tail(ms + quiet_bars(D(99960), 4, step=30))


def premise_before_arm() -> list:
    """[04:15,04:30) closes 97150 <= A+z 97200 before any successor: the review is WITHDRAWN; a later fresh reaction
    and recovery change nothing."""
    ms = first_call_then_failure() + bar15(99800, 99850, 97100, 97150)
    return tail(ms + bar15(97150, 99800, 97150, 99700) + bar15(99700, 100050, 99650, 99750) + [CONFIRM2])


def premise_in_failure_dispatch() -> list:
    """No call 1: S1 confirmed at 04:01 and waits; [04:14,04:15) touches V and closes 97150, so the 15m bar
    [04:00,04:15) closes at/below A+z in the failure dispatch 04:15: no review (v0.6 release)."""
    ms = a3_base() + flat(13, 100100, amp=D(0)) + [minute(100100, 100100, 97100, 97150)]
    return tail(ms + bar15(97150, 99800, 97150, 99700))


def frontier_failure() -> list:
    """Call 1 at 04:03; the V contact is the minute [04:14,04:15), so tf = 04:15 is exactly a 15m boundary and the
    bar [04:15,04:30) starting there is fully after the failure (O = tf); the contact bar [04:00,04:15) is excluded."""
    ms = a3_base() + [REF, VALID] + flat(11, 100010, amp=D(0)) + [minute(100010, 100010, 99690, 99800)]
    ms += bar15(*NEW_BAR) + [CONFIRM2, OUTSIDE2, REF2, RECOVER2]
    return tail(ms + walk(99865, 100910, 30))


def destination_in_review() -> list:
    """After the failure, a rise to 100910 without a fresh reaction: B contact closes the review (DESTINATION)."""
    return tail(first_call_then_failure() + walk(99800, 100910, 40))


def gap_in_review() -> list:
    """A missing trade minute at [04:20,04:21) while the review waits: coverage loss (UNASSESSABLE); the later
    qualifying bar never arms."""
    ms = first_call_then_failure() + bar15(*NEW_BAR)
    ms[-10] = Minute(ms[-10].o, ms[-10].h, ms[-10].lo, ms[-10].c, gap=True)
    return tail(ms + [CONFIRM2])


def third_attempt_refused() -> list:
    """two_calls, then the successor's V2 99450 is touched at [04:37,04:38) (call 2 and the successor INVALIDATED);
    a later fresh contrary bar [04:45,05:00) and a recovery above it never open another review (no third attempt)."""
    after = walk(99865, 99440, 4) + walk(99440, 99500, 7) + bar15(99500, 99700, 99300, 99400) + walk(99400, 100200, 10)
    return two_calls(after=after)


VIOLATE2 = minute(99820, 99850, 99790, 99840)  # low < L0' 99800 after the successor's reference: contradiction


def successor_child_contradicted() -> list:
    """two_calls up to the successor's reference, then a contradiction [04:33,04:34): the child ends (terminal), the
    successor stays CONFIRMED, the later valid recovery never reopens it, no call 2 and no third attempt."""
    ms = first_call_then_failure() + bar15(*NEW_BAR) + [CONFIRM2, OUTSIDE2, REF2, VIOLATE2, RECOVER2]
    return tail(ms + walk(99865, 100300, 10))


def far_b_base(b=103500) -> list:
    """``a3_base`` with the last impulse bar's high at ``b`` (a long upper wick, same close 100700): B and the own-B
    target are far, so a later ordinary same-direction impulse can qualify below B."""
    ms = a3_base()
    i0 = len(ms) - 1 - 15 - 15 - 15  # first minute of the impulse bar [03:15,03:30)
    from adviser3_fixtures import bar15 as _b
    x = ms[i0].o
    ms[i0:i0 + 15] = _b(x, b, x, D(100700), order="LH")
    return ms


def reservation_defers_birth(rise=(100400, 100900, 101400, 101900, 102400), after=None) -> list:
    """Far-B impulse: S1 confirmed at 04:01 then V contact [04:01,04:02) (tf 04:02). From 04:15 the price rises bar by
    bar without a contrary close (no successor), so the review stays open to H0 05:30 while an ordinary same-direction
    impulse qualifies: v0.6 births it, the variant defers it. ``after`` continues from 05:30."""
    ms = far_b_base() + [minute(100050, 100050, 99700, 99950)] + flat(13, 99950, amp=D(0))
    p = D(99950)
    for c in rise:
        ms += bar15(p, D(c) + 20, p - 10, D(c), order="LH")
        p = D(c)
    return tail(ms + (after if after is not None else []))


def old_recovery_before_arm() -> list:
    """As two_calls, but inside the failure bar [04:00,04:15) the price closes 100100 at [04:09,04:10) (above the old
    K 100049.9 and above the future K2 + tick 100050.1) before returning to 99800: neither the old confirmation nor
    that earlier recovery is ever a new fact; K2 comes from the fresh bar and only a later minute confirms."""
    ms = a3_base() + [REF, VALID, V_CONTACT] + walk(99950, 100100, 6) + walk(100100, 99800, 5)
    ms += bar15(*NEW_BAR) + [CONFIRM2, OUTSIDE2, REF2, RECOVER2]
    return tail(ms + walk(99865, 100910, 30))


def confirmed_time_expired() -> list:
    """Far-B impulse: S1 confirmed at 04:01 (IMMEDIATE call), progress passes (max close 101100 >= 100050 + 0.5 S15),
    B 103500 never reached, no V contact: TIME_EXPIRED at the hard deadline 08:01 - never a review."""
    return tail(far_b_base() + walk(100050, 101100, 60), n=300)


def confirmed_b_and_v_same_minute() -> list:
    """S1 confirmed at 04:01; the minute [04:01,04:02) reaches both B 100900 and V 99700: UNASSESSABLE, never a review."""
    return tail(a3_base() + [minute(100050, 100950, 99650, 99900)])
