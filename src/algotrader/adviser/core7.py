"""Adviser ``btc.context-action.v0.7`` professional fold (implementation ``adviser.core.v7``; state
``algotrader.adviser-state.v7``): the product version of the trigger/destination compatibility correction approved at
``57fa14e`` (``delivery/V07-TRIGGER-DESTINATION-RELEASE.md``).

The behaviour is exactly the approved EXPERIMENTAL v0.6-tdc fold (``core_tdc.AdviserCoreTDC``): v0.6 plus, for an ARMED
A scenario whose effective threshold Tq = Kq + tick x trigger_ticks is at or beyond its destination Bq, a faithful
incompatibility statement in the published antecedent and no MarketView directional support while it lasts (listed
with the observed hypotheses, status ARMED, one reason line; other scenarios as in v0.6; WATCH_ONLY wording of the
addendum). Operational policy unchanged. Only the identity differs, plus one INSPECTION field (never a journal record):
each A scenario row with a current trigger carries the engine's verdict ``trigger_destination`` (compatibility,
threshold, destination, and whether a compatible current anchor replaced an incompatible previous one), so the
cockpit translates it instead of computing it from prices or levels.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from . import contracts as sc
from .core import _iso
from .core_tdc import AdviserCoreTDC

STATE_FORMAT = "algotrader.adviser-state.v7"


class AdviserCoreV7(AdviserCoreTDC):
    STATE_FMT = STATE_FORMAT
    KINDS = sc.KIND_CONTRACTS_V7

    def scenarios_view(self, t: datetime | None) -> list[dict]:
        rows = super().scenarios_view(t)
        step = self.tick * self.p.trigger_ticks
        for row in rows:
            s = self.scen.get(row["scenario_id"])
            if s is None or s.family != "A" or s.k_t is None or s.dest_t is None:
                continue
            d = s.d
            compatible = not self.trigger_reaches_destination(s)
            prev = s.prev_anchor or {}
            prev_k = prev.get("K")
            prev_incompatible = None if prev_k is None else d * Decimal(prev_k) + step >= s.dest_t
            restored = compatible and s.status == "ARMED" and prev_incompatible is True
            row["trigger_destination"] = {
                "compatible": compatible, "supports_direction": compatible,
                "threshold": str((s.k_t + step) * d), "destination": str(s.dest_t * d),
                "previous_anchor_incompatible": prev_incompatible, "restored_by_revision": restored,
                "revision_published_at": _iso(s.anchor_pub_at) if restored else None}
        return rows

    def inspect(self) -> dict:
        out = super().inspect()
        out["method_semantics"] = ("v0.7: v0.6 + trigger/destination compatibility (an ARMED A whose effective threshold "
                                   "is at or beyond its destination is published as incompatible and is not MarketView "
                                   "directional support)")
        return out
