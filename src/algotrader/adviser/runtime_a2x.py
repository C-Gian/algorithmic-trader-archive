"""EXPERIMENTAL v0.6-a2x runtime state codec (``algotrader.adviser-runtime.v6-a2x``): the v0.3 runtime frontier/clock
codec around the second-attempt variant core (``algotrader.adviser-state.v6-a2x``) and the unchanged v0.3 evaluator.
No v0.2-v0.6 runtime document decodes here and vice versa (no silent cross-method continuation)."""

from __future__ import annotations

from .core_a2x import STATE_FORMAT as CORE_FORMAT, AdviserCoreA2X
from .runtime3 import AdviserRuntimeV3

RUNTIME_FORMAT = "algotrader.adviser-runtime.v6-a2x"


class AdviserRuntimeA2X(AdviserRuntimeV3):
    RUNTIME_FMT, CORE_FMT, CORE_CLS = RUNTIME_FORMAT, CORE_FORMAT, AdviserCoreA2X
