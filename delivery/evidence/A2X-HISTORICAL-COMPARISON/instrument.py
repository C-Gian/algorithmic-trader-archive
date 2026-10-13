"""Passive, read-only trace of an adviser core for the v0.6 / v0.6-a2x descriptive comparison (no product change).

``install(core, write)`` wraps four bound methods of ONE core instance (instance attributes; the classes and every
other instance are untouched). Each wrapper calls the original with the same arguments and returns its result
unchanged; it only reads state and calls ``write(dict)``:

* ``_emit``: at the FIRST scenario record of each scenario id, the frozen facts held by the core object at that
  moment - family, direction, the complete ordered source-bar list (records carry only the last three), birth time,
  S15, zone, impulse A/B in the real price domain, attempt/impulse (variant), owner, and the box geometry when the owner
  is the current box. These give the registered matching key.
* ``_a_births`` (flag only) and ``_qa``: every Q_A evaluated inside the birth step, with the direction's latch and
  discovery owner as read at that call (before the latch update): the state that decides an ordinary A birth.
* ``_a2x_count`` (variant only): every deferral of an ordinary same-direction birth while the slot is reserved, with
  the direction of the Q_A just evaluated, the reserving token and its impulse, and the 15m source close.

Reading state cannot alter the fold; the v0.6 run is checked against the earlier uninstrumented v0.6 journal.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable


def _iso(t: datetime | None) -> str | None:
    return None if t is None else t.isoformat()


def _real(x, d) -> str | None:
    return None if x is None else str(x * d)


def scenario_facts(core, s) -> dict[str, Any]:
    if s is None:
        return {"facts": None}
    box = getattr(core, "box", None)
    bx = None
    if box is not None and s.family in "BC" and s.owner == box.bid:
        bx = {"low": str(box.low), "up": str(box.up), "mid": str(box.mid)}
    return {"facts": {
        "family": s.family, "d": s.d, "sources": list(s.sources), "born_at": _iso(s.born_at),
        "s15": None if s.s15 is None else str(s.s15), "z": None if s.z is None else str(s.z),
        "impulse_A": _real(s.a_t, s.d), "impulse_B": _real(s.b_t, s.d), "owner": s.owner,
        "attempt": getattr(s, "attempt", 1), "impulse": getattr(s, "impulse", None),
        "setup_deadline": _iso(s.setup_deadline), "box": bx}}


def install(core, write: Callable[[dict], None]) -> None:
    seen: set[str] = set()
    st: dict[str, Any] = {"births": False, "last": None}

    orig_emit = core._emit

    def _emit(kind, t, body, *a, **kw):
        if kind == "scenario":
            sid = body["scenario_id"]
            if sid not in seen:
                seen.add(sid)
                write({"ev": "scenario_first", "t": _iso(t), "sid": sid, "transition": body["transition"],
                       **scenario_facts(core, core.scen.get(sid))})
        return orig_emit(kind, t, body, *a, **kw)

    orig_births = core._a_births

    def _a_births(b, t):
        st["births"] = True
        try:
            return orig_births(b, t)
        finally:
            st["births"] = False

    orig_qa = core._qa

    def _qa(d, t):
        r = orig_qa(d, t)
        if st["births"]:
            k = str(d)
            own = core.a_owner.get(k)
            st["last"] = (d, None if own is None else dict(own))
            write({"ev": "qa", "t": _iso(t), "d": d, "qa": r, "latch": core.latch[k],
                   "owner": None if own is None else own.get("sid"),
                   "reserved_for": None if own is None else own.get("reserved_for"),
                   "src_close": core.m15[-1].rid if core.m15 else None})
        return r

    core._emit, core._a_births, core._qa = _emit, _a_births, _qa

    if hasattr(core, "_a2x_count"):
        orig_count = core._a2x_count

        def _a2x_count(key, sub=None):
            if key == "ordinary_births_deferred":
                d, own = st["last"] if st["last"] is not None else (None, None)
                write({"ev": "deferral", "t": _iso(core.clock), "d": d,
                       "reserved_by": None if own is None else own.get("sid"),
                       "reserved_for": None if own is None else own.get("reserved_for"),
                       "src_close": core.m15[-1].rid if core.m15 else None})
            return orig_count(key, sub)

        core._a2x_count = _a2x_count
