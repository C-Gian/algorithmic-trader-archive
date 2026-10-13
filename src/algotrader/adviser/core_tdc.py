"""EXPERIMENTAL variant ``btc.context-action.v0.6-tdc`` (implementation ``adviser.core.v6-tdc``; state
``algotrader.adviser-state.v6-tdc``): v0.6 plus the trigger/destination compatibility correction authorized after the
Director's semantic review (``delivery/A-TRIGGER-DESTINATION-SEMANTIC-REVIEW.md``, ``f2e22ac``; correction document
``delivery/A-TRIGGER-DESTINATION-CORRECTION.md``). Not a release: never the default, never offered by the application;
selected explicitly in test paths only. It does not contain the v0.6-a2x second attempt.

Criterion (one function, engine-side, exact Decimal): for an ARMED A scenario in the direction-transformed domain
q = d x price, the effective confirmation threshold is Tq = Kq + tick x trigger_ticks (the confirmation predicate of
``core3._confirmations``) and the destination is Bq. The current recovery condition is COMPATIBLE only when Tq < Bq.
When Tq >= Bq a close meeting it has high_q >= Bq, a destination contact that the dispatch processes before
confirmation: the condition cannot confirm a continuation toward B under the current levels. Then, and only while it
holds (it is re-evaluated at every publication; levels only change at REVISE/REARM/ANCHOR_LOST):

* the published antecedent (scenario records, view entries, inspection) states the incompatibility faithfully;
* the MarketView does not count the scenario as directional support: it is listed with the observed hypotheses
  (``watch``, its status still ARMED) instead of the principal/alternatives, and a reason line explains it; every other
  scenario is evaluated as in v0.6 (an incompatible scenario never forces UNCERTAIN by itself).

Unchanged (inherited v0.6 code paths): recognition, levels, scenario identities, revisions, deadlines, terminals,
contact precedence, confirmation, child routing, selection, slot, conflicts and calls. The MarketView is computed after
selection and is read by no operational step.
"""

from __future__ import annotations

from .core import dname
from .core3 import Scen
from .core6 import AdviserCoreV6

STATE_FORMAT = "algotrader.adviser-state.v6-tdc"
NOTE = "armed, not counted as directional support"


class AdviserCoreTDC(AdviserCoreV6):
    STATE_FMT = STATE_FORMAT

    def trigger_reaches_destination(self, s: Scen) -> bool:
        """True when the current ARMED A recovery condition is incompatible with its destination (Tq >= Bq)."""
        if s.family != "A" or s.status != "ARMED" or s.k_t is None or s.dest_t is None:
            return False
        return s.k_t + self.tick * self.p.trigger_ticks >= s.dest_t

    def _antecedent(self, s: Scen) -> str:
        if not self.trigger_reaches_destination(s):
            return super()._antecedent(s)
        d = s.d
        threshold = (s.k_t + self.tick * self.p.trigger_ticks) * d
        return (f"current recovery condition incompatible with its destination: the required complete 1m close "
                f"{'>=' if d > 0 else '<='} {threshold} is at or beyond the destination {s.dest_t * d}, so meeting it "
                f"would reach the destination first and cannot confirm a continuation toward it under the current "
                f"levels; observed hypothesis, open only to the existing prospective anchor revisions (none is "
                f"promised); not a directional expectation, not an entry")

    def _view_support(self, active: list[Scen]) -> tuple[list, list]:
        strong = [s for s in active if s.status in ("ARMED", "CONFIRMED") and not self.trigger_reaches_destination(s)]
        watch = [s for s in active if s.status == "WATCH" or self.trigger_reaches_destination(s)]
        return strong, watch

    def _watch_only_reason(self, watch: list[Scen]) -> str:
        """With an incompatible ARMED scenario among them, the hypotheses are described as observed hypotheses
        without current directional support, each with its actual status; with WATCH hypotheses only, the v0.6
        sentence is kept unchanged."""
        if not any(self.trigger_reaches_destination(s) for s in watch):
            return super()._watch_only_reason(watch)
        items = ", ".join(f"{s.family} {dname(s.d)} {s.status}"
                          + (" (recovery condition incompatible with its destination)"
                             if self.trigger_reaches_destination(s) else "") for s in watch)
        return f"observed hypotheses without current directional support: {items} (not a forecast, not a call)"

    def _view_notes(self, active: list[Scen]) -> list[str]:
        return [f"{s.family} {dname(s.d)} {NOTE}: {self._antecedent(s)}" for s in active
                if self.trigger_reaches_destination(s)]

    def inspect(self) -> dict:
        out = super().inspect()
        out["method_semantics"] = ("EXPERIMENTAL v0.6-tdc: v0.6 + trigger/destination compatibility (an ARMED A whose "
                                   "effective threshold is at or beyond its destination is published as incompatible "
                                   "and is not MarketView directional support)")
        out["trigger_destination_incompatible"] = sorted(s.sid for s in self.scen.values()
                                                         if self.trigger_reaches_destination(s))
        return out
