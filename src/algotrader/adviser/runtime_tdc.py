"""EXPERIMENTAL v0.6-tdc runtime state codec (``algotrader.adviser-runtime.v6-tdc``): the v0.3 runtime frontier/clock
codec around the trigger/destination compatibility variant core (``algotrader.adviser-state.v6-tdc``) and the
unchanged v0.3 evaluator. No other runtime document decodes here and vice versa (no silent cross-method continuation)."""

from __future__ import annotations

from .core_tdc import STATE_FORMAT as CORE_FORMAT, AdviserCoreTDC
from .runtime3 import AdviserRuntimeV3

RUNTIME_FORMAT = "algotrader.adviser-runtime.v6-tdc"


class AdviserRuntimeTDC(AdviserRuntimeV3):
    RUNTIME_FMT, CORE_FMT, CORE_CLS = RUNTIME_FORMAT, CORE_FORMAT, AdviserCoreTDC
