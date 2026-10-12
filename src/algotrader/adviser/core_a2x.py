"""EXPERIMENTAL variant ``btc.context-action.v0.6-a2x`` (implementation ``adviser.core.v6-a2x``; state
``algotrader.adviser-state.v6-a2x``): v0.6 plus ONE successor attempt on the same A impulse after the confirmed first
attempt was invalidated by its frozen V (``delivery/A-SECOND-ATTEMPT-DESIGN.md``, design b20919e, ratification
3705fd0). Not a release: never the default, never offered by the application; selected explicitly in test paths only.

Everything not named here is the v0.6 fold unchanged (``core6.AdviserCoreV6``). The variant adds:

* **Review opening** (design §3), in the dispatch tf that publishes the first attempt's terminal: only a TERMINAL
  INVALIDATED with reason V_CONTACT of a CONFIRMED attempt-1 A scenario; tf < H0 (original expiry); the impulse still
  held the discovery owner; no B contact among the bars admitted in that dispatch; no known complete 15m close at or
  beyond A+z (the PRE-confirmation premise) since the confirmation, including that dispatch; 1m/15m readiness and the
  ordinary A context gate at tf; not in the evaluation tail. The first attempt's scenario, child and call records are
  exactly v0.6 (its terminal still says the owner was released by IT); a published observation then records the
  reservation. When an admissibility condition fails, v0.6 holds (owner released) and the reason is published.
* **Reservation** (§§3, 7): the same-direction A discovery owner stays occupied by the impulse until H0, the review's
  terminal or the successor's terminal, so an ordinary same-direction A birth cannot take the slot meanwhile (a
  deliberate policy change versus v0.6, published once per reservation when it first defers a Q_A true). On release
  the ordinary latch applies unchanged (NEED_FALSE -> false observed at/after release -> true). The reservation is
  counted in the A scenario capacity.
* **Fresh formation** (§4): origin O = first 15m boundary at/after tf; only complete 15m trade bars starting at/after
  O. R2 = cumulative transformed new low (anchor = latest bar attaining it, ties included); a contrary close is
  required on the new bars only (first new bar c < o, later ones c < previous new close); R2 < frozen R1,
  R2 < B - reaction_min_scale * birth S15, R2 > A + z; the ordinary A context gate now. No old bar, flag, recovery or
  confirmation is reused. While waiting: B contacts, coverage, staleness, the A+z close and the context gate close the
  review (§6 order: expiry/data, B, premise/gates, formation).
* **Successor** (§§2, 5): at the first qualifying bar, before H0, a distinct scenario (own id, parent = the impulse)
  is published ARMED with K2 = the anchor bar's high and V2 = R2 - z, frozen impulse A/B/S15/z/sources/expiry and
  destination B; its destination monitoring starts at that ARM. The budget is consumed there: no third attempt. Its
  local anchor rules before confirmation, the confirmation predicate, the child routing, selection, slot, conflicts,
  RETURN and call protections are the inherited ones; only the clocks differ: scenario and call hard deadline = H0
  (origin ORIGINAL_IMPULSE_EXPIRY), scenario progress at C2 + (H0 - C2)/2, call progress at issue + (H0 - issue)/2.
* **Insufficient residual** (ratified precision 1): an eligible recovery with less than the A minimum residual before
  H0 is published as an excluded observation (bar, interval, availability, close, residual, reason) and the successor
  ends EXPIRED: no confirmed or operative opportunity, no extension.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from . import contracts as sc
from .core import MINUTE, _d, _dt, _h, _iso, _s, dname, tbar
from .core3 import A_CAPACITY_PER_DIRECTION, AdviserError, Scen, half_point
from .core6 import AdviserCoreV6, Scen6
from .measures import Bar

STATE_FORMAT = "algotrader.adviser-state.v6-a2x"
OBS_NAME = "a_second_attempt"
ARM_REASON = "SECOND_ATTEMPT_FRESH_POST_FAILURE_REACTION"
EXCLUDED_REASON = "SECOND_ATTEMPT_RECOVERY_WITH_INSUFFICIENT_RESIDUAL"
HARD_ORIGIN = "ORIGINAL_IMPULSE_EXPIRY"


@dataclass
class ScenA2(Scen6):
    """The v0.6 scenario plus its attempt lineage (attempt 1 = an ordinary birth; attempt 2 = the successor)."""

    attempt: int = 1
    impulse: str | None = None  # the original impulse (= the first attempt's scenario id) for a successor
    review_opened_at: datetime | None = None  # tf
    review_origin: datetime | None = None  # O
    failed_r1_t: Decimal | None = None  # frozen R of the failed first attempt
    pre_premise_failed: bool = False  # attempt 1: a confirmed-time complete 15m close at/beyond A+z was seen

    _DT = Scen6._DT + ("review_opened_at", "review_origin")
    _DEC = Scen6._DEC + ("failed_r1_t",)


@dataclass
class Review:
    """The reserved review of one failed impulse (not a scenario, not ARMED/CONFIRMED, not an entry). Transformed
    prices (suffix _t)."""

    impulse: str
    d: int
    sources: list
    born_at: datetime
    h0: datetime
    s15: Decimal
    z: Decimal
    a_t: Decimal
    b_t: Decimal
    r1_t: Decimal
    b_broken: bool
    tf: datetime
    cursor: int
    origin: datetime
    bars: int = 0
    contrary: bool = False
    prev_close_t: Decimal | None = None
    r2_t: Decimal | None = None
    anchor: str | None = None
    anchor_h_t: Decimal | None = None

    _DT = ("born_at", "h0", "tf", "origin")
    _DEC = ("s15", "z", "a_t", "b_t", "r1_t", "prev_close_t", "r2_t", "anchor_h_t")

    @property
    def token(self) -> str:
        return f"{self.impulse}#review"

    def encode(self) -> dict:
        return {k: (str(v) if isinstance(v, Decimal) else _iso(v) if isinstance(v, datetime) else v)
                for k, v in self.__dict__.items()}

    @classmethod
    def decode(cls, d: dict) -> Review:
        x = dict(d)
        for k in cls._DT:
            x[k] = _dt(x[k])
        for k in cls._DEC:
            x[k] = _d(x[k])
        x["sources"] = list(x["sources"])
        return cls(**x)


def first_boundary_at_or_after(t: datetime) -> datetime:
    """O: the first 15m market boundary >= t (t itself when it is exactly a boundary)."""
    base = t.replace(minute=(t.minute // 15) * 15, second=0, microsecond=0)
    return base if base == t else base + timedelta(minutes=15)


class AdviserCoreA2X(AdviserCoreV6):
    SCEN_CLS = ScenA2
    STATE_FMT = STATE_FORMAT

    def __init__(self, config) -> None:
        super().__init__(config)
        self.reviews: dict[str, Review] = {}  # direction key -> open review
        self.counters["a2x"] = _new_counters()
        self._disp_closes15: list[Bar] = []
        self._emit_ctx: ScenA2 | None = None

    # ----------------------------------------------------------------------------------------------------------
    # dispatch context
    # ----------------------------------------------------------------------------------------------------------

    def dispatch(self, t: datetime) -> list[dict]:
        self._disp_closes15 = []
        return super().dispatch(t)

    def _ingest_sealed(self, sealed: list[dict], t: datetime) -> list[Bar]:
        closes = super()._ingest_sealed(sealed, t)
        self._disp_closes15 = list(closes)
        return closes

    def _a2x_count(self, key: str, sub: str | None = None) -> None:
        c = self.counters["a2x"]
        if sub is None:
            c[key] += 1
        else:
            c[key][sub] = c[key].get(sub, 0) + 1

    # ----------------------------------------------------------------------------------------------------------
    # successor clocks (design §5)
    # ----------------------------------------------------------------------------------------------------------

    def _conf_clocks(self, s: Scen, t: datetime) -> tuple[datetime, datetime]:
        if getattr(s, "attempt", 1) == 2:
            return s.setup_deadline, half_point(t, s.setup_deadline)
        return super()._conf_clocks(s, t)

    def _a_hard(self, s: Scen) -> tuple[datetime, str]:
        if getattr(s, "attempt", 1) == 2:
            return s.setup_deadline, HARD_ORIGIN
        return super()._a_hard(s)

    def _confirm(self, s: Scen, m: Bar, t: datetime) -> None:
        if getattr(s, "attempt", 1) == 2:
            residual = s.setup_deadline - t
            need = timedelta(minutes=self.p.residual_min["A"])
            if residual < need:  # ratified precision 1: keep the observation, no opportunity, no extension
                self._a2x_count("excluded_recoveries")
                self._obs("RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL", t, {
                    "impulse_id": s.impulse, "successor_id": s.sid, "bar": m.rid, "bar_start": _iso(m.start),
                    "bar_end": _iso(m.end), "bar_known_at": _iso(m.known_at), "available_at_dispatch": _iso(t),
                    "cursor": str(self.cursor), "close": str(m.c),
                    "recovery_threshold": str(s.k_t * s.d + self.tick * self.p.trigger_ticks * s.d),
                    "original_expiry": _iso(s.setup_deadline), "residual_seconds": str(int(residual.total_seconds())),
                    "required_residual_minutes": str(self.p.residual_min["A"]), "reason": "INSUFFICIENT_RESIDUAL",
                    "operational": "false"},
                    "A recovery of the successor was observed, but less than the minimum residual remained before the "
                    "original expiry: it is recorded, not confirmed, and the successor ends without an opportunity.",
                    (s.sid, s.impulse))
                self._scen_end(s, "EXPIRED", f"{EXCLUDED_REASON}:{m.rid}", t)
                return
            self._a2x_count("successor_confirmations")
        super()._confirm(s, m, t)

    # ----------------------------------------------------------------------------------------------------------
    # review opening at the first attempt's terminal (design §3)
    # ----------------------------------------------------------------------------------------------------------

    def _scen_end(self, s: Scen, state: str, reason: str, t: datetime, coverage_from: datetime | None = None) -> None:
        if s.sid not in self.scen:
            return
        failure = (s.family == "A" and getattr(s, "attempt", 1) == 1 and s.status == "CONFIRMED"
                   and state == "INVALIDATED" and reason.startswith("V_CONTACT:"))
        excluded = self._review_exclusion(s, t) if failure else None
        released_key = f"SCENARIO_{state}"
        before = self.counters["v3"]["owner_releases"].get(released_key, 0)
        super()._scen_end(s, state, reason, t, coverage_from=coverage_from)
        if not failure:
            return
        if excluded is not None:
            self._a2x_count("reviews_not_opened", excluded.split(":")[0])
            self._obs("REVIEW_NOT_OPENED", t, {"impulse_id": s.sid, "failure": reason.split(":", 1)[1],
                                               "reason": excluded, "original_expiry": _iso(s.setup_deadline)},
                      "The confirmed first attempt failed at its V, but a second attempt is not admissible: "
                      "v0.6 behaviour (owner released).", (s.sid,))
            return
        # the reservation replaces, prospectively, the release v0.6 made for this V contact (S1 records unchanged)
        after = self.counters["v3"]["owner_releases"].get(released_key, 0)
        if after > before:
            self.counters["v3"]["owner_releases"][released_key] = after - 1
            if after - 1 == 0:
                del self.counters["v3"]["owner_releases"][released_key]
        rv = Review(impulse=s.sid, d=s.d, sources=list(s.sources), born_at=s.born_at, h0=s.setup_deadline, s15=s.s15,
                    z=s.z, a_t=s.a_t, b_t=s.b_t, r1_t=s.r_t, b_broken=s.b_broken, tf=t, cursor=self.cursor,
                    origin=first_boundary_at_or_after(t))
        self.reviews[str(s.d)] = rv
        self.a_owner[str(s.d)] = {"sid": rv.token, "expires": _iso(rv.h0), "reserved_for": s.sid}
        self._a2x_count("reviews_opened")
        self._obs("REVIEW_OPEN", t, {**self._review_values(rv), "failure": reason.split(":", 1)[1]},
                  "The confirmed first attempt failed at its V before the original expiry: the discovery slot stays "
                  "reserved for one second attempt that needs a fresh complete reaction after the failure (not a "
                  "scenario, not an entry, not a call).", (s.sid,))
        self._touch()

    def _review_exclusion(self, s: Scen, t: datetime) -> str | None:
        """The first unmet admissibility condition of a review (None = admissible)."""
        if self.window == "TAIL":
            return "EVALUATION_TAIL"
        if t >= s.setup_deadline:
            return "AT_OR_AFTER_ORIGINAL_EXPIRY"
        if not self._owner_active(s):
            return "DISCOVERY_OWNER_ALREADY_RELEASED"
        if any(tbar(m, s.d)[1] >= s.b_t for m in self._disp_bars):
            return "DESTINATION_CONTACT_IN_FAILURE_DISPATCH"
        if getattr(s, "pre_premise_failed", False) or any(tbar(b, s.d)[3] <= s.a_t + s.z for b in self._disp_closes15):
            return "PREMISE_CLOSE_AT_OR_BEYOND_A_PLUS_Z_KNOWN"
        if not self.ready_1m(t) or not self.ready_15m(t):
            return "REQUIRED_DATA_NOT_READY"
        if not self._a_context_ok(s, t):
            return f"CONTEXT_OR_ADVERSE_EXPANSION:{self.context(t)}/{self.phase_now(t)}:{self.phase['dir']}"
        return None

    def _premise_close(self, b: Bar, t: datetime) -> None:
        for s in self.scen.values():
            if (s.family == "A" and s.status == "CONFIRMED" and getattr(s, "attempt", 1) == 1 and b.end > s.conf_at
                    and tbar(b, s.d)[3] <= s.a_t + s.z):
                s.pre_premise_failed = True
        super()._premise_close(b, t)

    # ----------------------------------------------------------------------------------------------------------
    # review lifecycle (design §6 order: expiry/data -> B -> premise/gates -> formation)
    # ----------------------------------------------------------------------------------------------------------

    def _review_values(self, rv: Review) -> dict[str, Any]:
        d = rv.d
        return {"impulse_id": rv.impulse, "direction": dname(d), "impulse_A": str(rv.a_t * d),
                "impulse_B": str(rv.b_t * d), "birth_s15": str(rv.s15), "zone_halfwidth": str(rv.z),
                "failed_attempt_R": str(rv.r1_t * d), "original_expiry": _iso(rv.h0), "opened_at": _iso(rv.tf),
                "opened_cursor": str(rv.cursor), "formation_origin": _iso(rv.origin), "new_bars": str(rv.bars),
                "new_reaction_low": _s(rv.r2_t * d if rv.r2_t is not None else None), "new_anchor": rv.anchor,
                "contrary_close_seen": str(rv.contrary).lower()}

    def _close_review(self, rv: Review, state: str, reason: str, t: datetime) -> None:
        key = str(rv.d)
        if self.reviews.get(key) is not rv:
            return
        del self.reviews[key]
        own = self.a_owner.get(key)
        if own is not None and own.get("sid") == rv.token:
            self.a_owner[key] = None  # release: the ordinary latch applies from here (no reset, no retro false)
        self._a2x_count("reviews_closed", f"{state}:{reason.split(':')[0]}")
        self._obs("REVIEW_CLOSED", t, {**self._review_values(rv), "state": state, "reason": reason},
                  "The reserved second attempt ended without a successor; the discovery slot is released.",
                  (rv.impulse,))
        self._touch()

    def _windows(self, t: datetime) -> None:
        was = self.window
        super()._windows(t)
        if was == "EVALUATION" and self.window == "TAIL":
            for rv in [self.reviews[k] for k in sorted(self.reviews)]:
                self._close_review(rv, "TERMINAL", "EVALUATION_WINDOW_ENDED", t)

    def _scen_timers(self, t: datetime) -> None:
        m1_stale = self.last_1m is not None and not self.ready_1m(t)
        m15_stale = bool(self.m15) and not self.ready_15m(t)
        for rv in [self.reviews[k] for k in sorted(self.reviews)]:
            if t >= rv.h0:  # equality: the timer precedes any ARM/CONFIRM of this dispatch
                self._close_review(rv, "EXPIRED", "ORIGINAL_SETUP_DEADLINE", t)
            elif m1_stale:
                self._close_review(rv, "UNASSESSABLE", "REQUIRED_TRADE_1M_STALE", t)
            elif m15_stale:
                self._close_review(rv, "UNASSESSABLE", "REQUIRED_INPUT_STALE:TRADE_15M", t)
        super()._scen_timers(t)

    def _required_gap(self, h: str, rec: dict, t: datetime) -> None:
        if h == "15m":
            for rv in [self.reviews[k] for k in sorted(self.reviews)]:
                self._close_review(rv, "UNASSESSABLE", f"REQUIRED_GAP_{h}:{rec['record_id']}:{rec['status']}", t)
        super()._required_gap(h, rec, t)

    def _scen_intervals(self, items: list, t: datetime) -> None:
        open_before = {k: rv for k, rv in self.reviews.items() if rv.tf < t}
        super()._scen_intervals(items, t)  # may open a review at this t (its own dispatch was checked at opening)
        for k in sorted(open_before):
            rv = self.reviews.get(k)
            if rv is not open_before[k]:
                continue
            for m in items:
                if isinstance(m, tuple):
                    if m[1] + MINUTE > rv.tf:
                        self._close_review(rv, "UNASSESSABLE", f"REQUIRED_MONITORING_GAP:{m[2]}", t)
                        break
                    continue
                if m.end <= rv.tf:
                    continue
                hit_b = tbar(m, rv.d)[1] >= rv.b_t
                if m.start < rv.tf and hit_b:
                    self._close_review(rv, "UNASSESSABLE", f"DESTINATION_CONTACT_TIME_AMBIGUOUS:{m.rid}", t)
                    break
                if hit_b:
                    self._close_review(rv, "DESTINATION_REACHED", f"DESTINATION_CONTACT:{m.rid}", t)
                    break

    def _a_close(self, b: Bar, t: datetime) -> None:
        super()._a_close(b, t)
        rv = None
        for k in sorted(self.reviews):
            rv = self.reviews[k]
            if rv.tf >= t or b.end <= rv.tf:
                continue  # opened in this dispatch (checked at opening) / a bar complete before the failure
            o_t, h_t, l_t, c_t = tbar(b, rv.d)
            if c_t <= rv.a_t + rv.z:
                self._close_review(rv, "WITHDRAWN", "CLOSE_AT_OR_BEYOND_A_PLUS_ZONE", t)
                continue
            if not self._a_context_ok(rv, t):
                self._close_review(rv, "WITHDRAWN", f"CONTEXT_OR_ADVERSE_EXPANSION:{self.context(t)}/"
                                                    f"{self.phase_now(t)}:{self.phase['dir']}", t)
                continue
            if b.start < rv.origin:
                continue  # the bar containing (or preceding) the failure never forms the new reaction
            rv.bars += 1
            rv.contrary = rv.contrary or (c_t < o_t if rv.prev_close_t is None else c_t < rv.prev_close_t)
            rv.prev_close_t = c_t
            if rv.r2_t is None or l_t <= rv.r2_t:
                rv.r2_t, rv.anchor, rv.anchor_h_t = l_t, b.rid, h_t
            self._touch()
            if (rv.contrary and rv.r2_t < rv.r1_t and rv.r2_t < rv.b_t - self.p.a_reaction_min * rv.s15
                    and rv.r2_t > rv.a_t + rv.z and t < rv.h0):
                self._arm_successor(rv, b, t)

    def _context_withdrawals(self, t: datetime, closes15: list[Bar]) -> None:
        super()._context_withdrawals(t, closes15)
        for rv in [self.reviews[k] for k in sorted(self.reviews)]:
            if rv.tf < t and not self._a_context_ok(rv, t):
                self._close_review(rv, "WITHDRAWN", f"CONTEXT_OR_ADVERSE_EXPANSION:{self.context(t)}/"
                                                    f"{self.phase_now(t)}:{self.phase['dir']}", t)

    def _arm_successor(self, rv: Review, b: Bar, t: datetime) -> None:
        d = rv.d
        sid = f"A{dname(d)[0]}-{_iso(b.start)}-{_h(self.cfg.method.rules_sha256, self.cfg.instrument, 'A2', d, rv.impulse, rv.anchor)}"
        if sid in self.scen:
            raise AdviserError(f"successor {sid} already exists")
        s = self.SCEN_CLS(sid=sid, family="A", d=d, owner=sid, born_at=t, born_seq=self.seq, sources=list(rv.sources),
                          setup_deadline=rv.h0, s15=rv.s15, z=rv.z, a_t=rv.a_t, b_t=rv.b_t, bars_seen=rv.bars,
                          lower_close=True, prev_close_t=rv.prev_close_t, b_broken=rv.b_broken,
                          renewal="SECOND_ATTEMPT", dest_t=rv.b_t, dest_type="IMPULSE_B", attempt=2,
                          impulse=rv.impulse, review_opened_at=rv.tf, review_origin=rv.origin, failed_r1_t=rv.r1_t)
        del self.reviews[str(d)]
        self.scen[sid] = s
        self.a_owner[str(d)] = {"sid": sid, "expires": _iso(rv.h0)}
        self._a2x_count("successors_armed")
        self._obs("SUCCESSOR_ARMED", t, {**self._review_values(rv), "successor_id": sid},
                  "A fresh complete reaction after the failure qualified: the single successor attempt of this impulse "
                  "is armed (budget consumed; no third attempt).", (rv.impulse, sid))
        self._publish_anchor(s, "ARM", rv.r2_t, rv.anchor_h_t, rv.anchor, t)

    # ----------------------------------------------------------------------------------------------------------
    # reservation versus ordinary births (design §7)
    # ----------------------------------------------------------------------------------------------------------

    def _a_births(self, b: Bar, t: datetime) -> None:
        if self.window != "TAIL":
            for key in ("1", "-1"):
                own = self.a_owner.get(key)
                if own is None or not self._reserved(own):
                    continue
                if self._qa(int(key), t) is True:
                    self._a2x_count("ordinary_births_deferred")
                    if not own.get("deferral_published"):
                        own["deferral_published"] = True
                        self._obs("ORDINARY_BIRTH_DEFERRED", t, {
                            "direction": dname(int(key)), "reserved_by": own["sid"],
                            "impulse_id": own.get("reserved_for") or own["sid"], "until": own["expires"],
                            "ordinary_source_close": b.rid},
                            "An ordinary same-direction A impulse qualified while the slot is reserved for the "
                            "second attempt: no ordinary birth now (policy change versus v0.6).",
                            (own.get("reserved_for") or own["sid"],))
        super()._a_births(b, t)

    def _reserved(self, own: dict) -> bool:
        if own.get("reserved_for"):
            return True
        s = self.scen.get(own["sid"])
        return s is not None and getattr(s, "attempt", 1) == 2

    def _capacity_check(self) -> None:
        for key in self.reviews:
            n = sum(1 for s in self.scen.values() if s.family == "A" and s.d == int(key)) + 1
            if n > A_CAPACITY_PER_DIRECTION:
                raise AdviserError(f"SCENARIO_CAPACITY_INVARIANT: {n} active A {dname(int(key))} scenarios and "
                                   f"reservations > {A_CAPACITY_PER_DIRECTION}")
        super()._capacity_check()

    # ----------------------------------------------------------------------------------------------------------
    # records / view
    # ----------------------------------------------------------------------------------------------------------

    def _obs(self, category: str, t: datetime, values: dict[str, Any], meaning: str, lineage: tuple) -> None:
        self._emit("observation", t, {
            "lens": "structure", "name": OBS_NAME, "category": category,
            "values": {k: (None if v is None else str(v)) for k, v in sorted(values.items())},
            "decision_role": "A_SECOND_ATTEMPT_RESERVATION", "meaning": meaning}, lineage=lineage)

    def _emit_scen(self, s: Scen, transition: str, reason: str | None, t: datetime, terminal: str | None = None,
                   released: bool = False) -> None:
        self._emit_ctx = s if getattr(s, "attempt", 1) == 2 else None
        try:
            super()._emit_scen(s, transition, reason, t, terminal=terminal, released=released)
        finally:
            self._emit_ctx = None

    def _emit(self, kind: str, t: datetime, body: dict, rid: str | None = None, revision: int = 0,
              lineage: tuple = (), event: tuple | None = None) -> dict:
        s = self._emit_ctx
        if kind == "scenario" and s is not None and body.get("scenario_id") == s.sid:
            d = s.d
            body = {**body, "setup": {**body["setup"], "attempt": "2", "impulse_id": s.impulse,
                                      "parent_scenario_id": s.impulse, "review_opened_at": _iso(s.review_opened_at),
                                      "formation_origin": _iso(s.review_origin),
                                      "failed_attempt_R": _s(s.failed_r1_t * d if s.failed_r1_t is not None else None)}}
            if body["transition"] == "ARM" and body["reason"] is None:
                body["reason"] = ARM_REASON
            lineage = tuple(lineage) + ((s.impulse,) if s.impulse not in lineage else ())
        return super()._emit(kind, t, body, rid=rid, revision=revision, lineage=lineage, event=event)

    def compute_view(self, t: datetime) -> dict:
        v = super().compute_view(t)
        p = v.get("principal")
        if p is not None:
            s = self.scen.get(p["scenario_id"])
            if s is not None and getattr(s, "attempt", 1) == 2 and s.status != "CONFIRMED" and v["horizon_minutes"]:
                rem = max(int((s.setup_deadline - t) / MINUTE), 0)  # descriptive horizon bounded by the residual
                v["horizon_minutes"] = (min(v["horizon_minutes"][0], rem), min(v["horizon_minutes"][1], rem))
        if self.reviews:
            v["reasons"] = tuple(v["reasons"]) + tuple(
                f"A {dname(rv.d)} second attempt reserved for impulse {rv.impulse} until {_iso(rv.h0)}: waiting for a "
                f"fresh complete reaction from {_iso(rv.origin)} (no scenario, no entry, not a call)"
                for _, rv in sorted(self.reviews.items()))
        return v

    def inspect(self) -> dict:
        out = super().inspect()
        out["method_semantics"] = ("EXPERIMENTAL v0.6-a2x: v0.6 + one successor A attempt on the same impulse after a "
                                   "confirmed V contact (reserved discovery slot, fresh post-failure reaction, clocks "
                                   "bounded by the original expiry)")
        out["second_attempt_reviews"] = {dname(int(k)): rv.encode() for k, rv in sorted(self.reviews.items())}
        out["successors"] = sorted(s.sid for s in self.scen.values() if getattr(s, "attempt", 1) == 2)
        return out

    def encode(self) -> dict:
        doc = super().encode()
        doc["a2x"] = {"reviews": [rv.encode() for _, rv in sorted(self.reviews.items())]}
        return doc

    @classmethod
    def decode(cls, doc: dict, cfg) -> AdviserCoreA2X:
        base = dict(doc)
        a2x = base.pop("a2x")
        c = super().decode(base, cfg)
        c.reviews = {str(x["d"]): Review.decode(x) for x in a2x["reviews"]}
        return c


def _new_counters() -> dict:
    return {"reviews_opened": 0, "reviews_not_opened": {}, "reviews_closed": {}, "successors_armed": 0,
            "successor_confirmations": 0, "excluded_recoveries": 0, "ordinary_births_deferred": 0}


_ = sc
