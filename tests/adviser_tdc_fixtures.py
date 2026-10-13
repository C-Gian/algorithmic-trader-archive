"""Hand-designed synthetic paths for the EXPERIMENTAL v0.6-tdc trigger/destination compatibility variant (engineering
inputs, NOT market data). Every tape starts from the cold day-1 history of the MP-002/MP-003 base A LONG path:
warmup, readiness, context and scale are produced by the ordinary kernel; no scenario, anchor or call is placed in
any state.

Base geometry (``adviser4_fixtures``): impulse A 97000, B 100900, birth S15 2000, z 200; birth 03:30, original expiry
05:30. The reaction bar [03:30,03:45) is o 100700, high H, low 100000, close 100049.9 (order HL), so the first ARM at
03:45 has R 100000, V 99800 and K = H (the anchor bar's high). With tick 0.1 and one trigger tick the effective
threshold is T = H + 0.1 (LONG); the condition is compatible only when T < B = 100900:

* H 100899.8 -> T 100899.9 = B - tick: compatible (one tick before B);
* H 100899.9 -> T 100900.0 = B: incompatible (exactly at B);
* H 100900   -> T 100900.1 = B + tick: incompatible (one tick beyond).

H never exceeds B + z (101100), so the WATCH spend rule does not apply. SHORT tapes are the positive-price reflection
about 100000 (x -> 200000 - x): B 99100, T = 200000 - H - 0.1.
"""

from __future__ import annotations

from adviser3_fixtures import DAY1, DAY2, D, T, bar15, flat, index_of, minute, mirror, walk  # noqa: F401
from adviser4_fixtures import birth_base
from adviser5_fixtures import REF, VALID

H_BEFORE, H_AT, H_BEYOND = D("100899.8"), D("100899.9"), D(100900)
B = D(100900)


def tail(ms: list, n: int = 420) -> list:
    return ms + flat(n, ms[-1].c)


def arm_with(h) -> list:
    """Up to the first ARM published at 03:45 with K = h."""
    return birth_base() + bar15(D(100700), D(str(h)), D(100000), D("100049.9"))


def hold(h) -> list:
    """First ARM at 03:45 with K = h, then 100049.9 -> 100300 and flat (lows above R 100000, no new reaction, no close
    reaching T): the scenario stays ARMED to its original expiry 05:30 (EXPIRED in every policy)."""
    return tail(arm_with(h) + walk(D("100049.9"), 100300, 5) + flat(100, 100300, amp=D(0)))


def reach_threshold(h) -> list:
    """First ARM at 03:45 with K = h, then a walk to 100500 and the minute [04:00,04:01) closing exactly at T = h + 0.1
    with high = close. Compatible (T < B): the close confirms (CONFIRM at 04:01). Incompatible (T >= B): the minute's
    high reaches B, a destination contact processed before confirmation: DESTINATION_REACHED at 04:01, never a CONFIRM."""
    t_ = D(str(h)) + D("0.1")
    return tail(arm_with(h) + walk(D("100049.9"), 100500, 15) + [minute(100500, t_, 100500, t_)] + walk(t_, 100300, 10))


def revision_restores() -> list:
    """First ARM at 03:45 with K 100900 (T 100900.1 > B: incompatible), then the a3 base: bar [03:45,04:00) o 100049.9
    h 100049.9 l 99900 c 99950 is a lower clean reaction -> REVISE at 04:00 (K 100049.9, T 100050 < B: compatible),
    minute [04:00,04:01) closes 100050 -> CONFIRM at 04:01; then REF and VALID -> call at 04:03 (the v0.6 path)."""
    ms = arm_with(H_BEYOND) + bar15(D("100049.9"), D("100049.9"), D(99900), D(99950))
    ms.append(minute(99950, 100050, 99950, 100050))
    return tail(ms + [REF, VALID] + walk(100012, 100300, 20))


def valid_and_incompatible() -> list:
    """Two same-direction A scenarios. S1 (far B 103500, ``adviser_a2x_fixtures.far_b_base``) confirms at 04:01 and
    stays CONFIRMED (no V/B contact) to its hard deadline 08:01; its discovery owner is released at 05:30. A quiet hour
    then a second LONG impulse (six bars of +60 from 101100) gives S2's birth at 07:30 (B2 101460, S15 104.95). The
    reaction bar [07:30,07:45) o 101460 h 101460 l 101300 c 101350 arms S2 at 07:45 with K2 = 101460 = B2: T2 101460.1
    > B2, incompatible, while S1 is a valid confirmed support. After 08:01 (S1 TIME_EXPIRED) only S2 remains."""
    from adviser_a2x_fixtures import far_b_base

    ms = far_b_base() + walk(100050, 101100, 59) + flat(60, 101100, amp=D(5))
    p = D(101100)
    for _ in range(6):
        ms += bar15(p, p + 60, p, p + 60, order="LH")
        p += 60
    ms += bar15(D(101460), D(101460), D(101300), D(101350))
    return tail(ms + walk(101350, 101400, 15) + flat(60, 101400, amp=D(0)))


def short(ms: list) -> list:
    return mirror(ms)


def watch_and_incompatible() -> list:
    """A B LONG WATCH hypothesis together with an incompatible ARMED A LONG (``adviser_fixtures.Path``; P0 100000).

    Day 1 oscillates (15m TR 15, BALANCED); day 2 rises +1/min from 00:00 to 04:00 (1h context UP from 04:00) to
    L = 100240; twelve 15m bars cycle L -> L+10 -> L+20 -> L+30 -> ... (TR 10), then five bars around the middle
    (TR <= 6): COMPRESSION, box [100240, 100270] born at 08:15 (S15 10, z 1). The breakout bar [08:15,08:30) closes
    L+45 = 100285 > U+z: B LONG born WATCH (destination 100300) and, in the same dispatch, an A LONG birth (Q_A true;
    B_A = 100285). The bar [08:30,08:45) opens at 100285 (= B_A, its high), dips to 100274 (> U+z: no B retest;
    < B_A - 0.25 S15) and closes 100278 (lower close): A ARM at 08:45 with K = 100285 = B_A -> T = 100285.1 > B_A,
    incompatible, while B is still WATCH (retest window 4 bars: B EXPIRED at 09:30). Then flat +-0.5."""
    from adviser_fixtures import Path

    p = Path()
    p.oscillate(24, amp=60)
    p.step(240, 1)
    low = p.last
    seq = [1, 2, 3, 2, 1, 0]
    for i in range(12):
        p.to(low + D(30) * seq[i % 6] / 3, 15)
    mid = low + D(15)
    p.to(mid, 15)
    for i in range(4):
        p.to(mid + (D(6) if i % 2 == 0 else 0), 15)
    p.to(low + 45, 15).to(low + 34, 10).to(low + 38, 5)
    for i in range(300):
        p.step(1, D("0.5") if i % 2 == 0 else D("-0.5"))
    return p.minutes()
