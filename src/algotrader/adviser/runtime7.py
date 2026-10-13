"""v0.7 runtime state codec (``algotrader.adviser-runtime.v7``): the v0.3 runtime frontier/clock codec around the v0.7
core (``algotrader.adviser-state.v7``) and the unchanged v0.3 evaluator. No other runtime document decodes here and vice
versa (no silent cross-method continuation, no migration)."""

from __future__ import annotations

from .core7 import STATE_FORMAT as CORE_FORMAT, AdviserCoreV7
from .runtime3 import AdviserRuntimeV3

RUNTIME_FORMAT = "algotrader.adviser-runtime.v7"


class AdviserRuntimeV7(AdviserRuntimeV3):
    RUNTIME_FMT, CORE_FMT, CORE_CLS = RUNTIME_FORMAT, CORE_FORMAT, AdviserCoreV7
