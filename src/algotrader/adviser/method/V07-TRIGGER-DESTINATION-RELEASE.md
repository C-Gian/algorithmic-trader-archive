# Adviser v0.7 — the trigger/destination compatibility correction as a product version

13 October 2026. **Authorization:** the orchestrator's decision, relayed by the Owner. It integrates **only** the tdc correction approved at `57fa14ea5b94934a1a6ac16dba126f991c169902` as a new product version, distinct from the frozen v0.6.

**Not part of this version:** a2x and any other methodological change.

**Unchanged:**
- v0.6 stays selectable, with its identity and behaviour.
- The default method stays v0.2.
- The EXPERIMENTAL v0.6-tdc variant and its evidence are kept.
- No run or checkpoint migrates implicitly: a state restores only under a compatible identity.
  - A v0.7 run or state never decodes as v0.6, v0.6-tdc or v0.6-a2x, and vice versa.
  - A live session started with another method begins a new epoch (METHOD_CHANGED).

## Rules

v0.7 is v0.6 plus exactly the rules of [`A-TRIGGER-DESTINATION-CORRECTION.md`](A-TRIGGER-DESTINATION-CORRECTION.md), as approved at `57fa14e`, including its WATCH_ONLY addendum. The Director's [semantic review](A-TRIGGER-DESTINATION-SEMANTIC-REVIEW.md) is their source. No other rule, number or threshold is added.

In short:
- **Criterion.** For an ARMED A scenario, with q = d × price, Tq = d·K + tick × trigger ticks; the condition is compatible only when Tq < Bq.
- **While incompatible:**
  - the published antecedent states the incompatibility;
  - the MarketView does not count the scenario as directional support: it is listed with the observed hypotheses, status ARMED, with a reason line;
  - other scenarios are evaluated as in v0.6;
  - only a later compatible revision publication restores support.
- **Operational policy unchanged:** recognition, levels, ids, revisions, deadlines, terminals, confirmation, child, selection, slot, conflicts and calls.

**Inspection only.** The live and inspection scenario rows carry the engine's own verdict, `trigger_destination`, with compatible, threshold and destination. The cockpit translates it; it never computes it from prices or levels.

## Identity

| Field | Value |
|---|---|
| Key / label | `v0.7` — "Candidate v0.7 — an A condition that would already reach its destination is not counted as directional support" |
| Model / rules | `btc.context-action.v0.7` / `tdc.rules.v0.7` |
| Implementation / state / runtime / engine | `adviser.core.v7` / `algotrader.adviser-state.v7` / `algotrader.adviser-runtime.v7` / `observe.stream.v8` |
| Report / reconciliation / Deep | `adviser.report.v7` / `10` / `11`: the v0.6 report, reconciliation and Deep checks applied to the pinned v0.7 release |
| Rules manifest | this document (DELTA), the correction rules, the Director's semantic review, then the v0.6 texts (MP-005 … MP-001) |
| Register | `V07-PARAMETERS.json` = the approved tdc register (= MP-005 numbers) with identity and status changed. **No new number** |
| Contracts | semantic.v2 **revision 6**: v0.7 emits the revision-5 contracts unchanged. The MarketView `watch` may list an incompatible ARMED A scenario (status ARMED), with the published wording. observe.v1 **revision 10**: `adviser_method` accepts `v0.7` |
| Status | engineering review pending; economic usefulness unvalidated. Not the default |
