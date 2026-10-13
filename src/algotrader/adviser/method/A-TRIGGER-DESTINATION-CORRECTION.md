# A trigger/destination compatibility — correction rules (EXPERIMENTAL v0.6-tdc)

13 October 2026. **Authorization:** relayed by the Owner after `f2e22ac`. It is a decision on the minimum correction proposed by the Director's [semantic review](A-TRIGGER-DESTINATION-SEMANTIC-REVIEW.md) (`aebf831`, recorded in `f2e22ac`): implement it in a version distinct from the frozen v0.6.

**Not authorized:** promotion, installation in the Owner stack, real data, historical replay, economic evaluation and CI query. v0.6 and the registered studies stay frozen and INACTIVE. The variant does not contain v0.6-a2x.

## Rule (delta over v0.6 / MP-005; everything else inherited unchanged)

**Domain.** Let d = +1 (LONG) or −1 (SHORT), q = d × price, tick = the instrument tick and `trigger_ticks` the registered confirmation ticks (MP-005 register: 1).

**Threshold.** For an **ARMED A** scenario with current trigger K and destination B, the effective confirmation threshold is **Tq = d·K + tick × trigger_ticks**. This is the inclusive predicate of the confirmation pass: close_q ≥ Tq.

**Compatibility.**
- **Compatible:** `Tq < Bq`. Behaviour is that of v0.6.
- **Incompatible:** `Tq ≥ Bq`.
  - A complete 1m close meeting the condition has high_q ≥ close_q ≥ Tq ≥ Bq. That is a destination contact, which the ordinary dispatch processes before the confirmation pass.
  - So the condition cannot confirm a continuation toward B under the current levels.

**While a scenario is incompatible:**
1. **Faithful publication.** The antecedent published with the scenario (scenario records, MarketView entries, inspection) states that the required close is at or beyond the destination, that meeting it would reach the destination first, and that it cannot confirm a continuation toward it under the current levels. The scenario remains an observed hypothesis open only to the existing prospective anchor revisions; no revision is promised. It is not a directional expectation and not an entry.
2. **MarketView.**
   - The scenario is **not directional support**: it is neither principal nor alternative.
   - It is listed with the observed hypotheses (`watch`), with its true status ARMED.
   - A reason line `A <direction> armed, not counted as directional support: <antecedent>` is added.
   - Every other scenario is evaluated exactly as in v0.6. An incompatible scenario never forces UNCERTAIN, or any other row, while a valid support remains.
   - With no other support and no WATCH hypothesis, the row is WATCH_ONLY / UNCERTAIN, as for v0.6 hypotheses.

**Re-evaluation.**
- Compatibility is computed by one engine function (`AdviserCoreTDC.trigger_reaches_destination`, exact Decimal), shared by the publication and the MarketView. The frontend deduces nothing.
- It is re-evaluated at every publication. K and B change only at the inherited REVISE / REARM / ANCHOR_LOST publications, so support is restored only by a new publication that makes it compatible.
- Earlier records are never rewritten.

## Preserved (inherited v0.6 code paths, not modified)

- Recognition, levels, scenario identities, revisions, deadlines, terminals and contact precedence.
- Confirmation, child routing, selection, slot, conflicts and calls.
- No early terminal, no change to B, no lowered trigger, no change to operational selection.
- The MarketView is computed after selection in the dispatch and is read by no operational step: selection, child, call, material change or alert.

## Identity

| Field | Value |
|---|---|
| Key | `v0.6-tdc` (EXPERIMENTAL, `methods.EXPERIMENTAL`; never listed or default) |
| Model / rules | `btc.context-action.v0.6-tdc` / `tdc.rules.exp1` |
| Implementation / state / runtime / engine | `adviser.core.v6-tdc` / `algotrader.adviser-state.v6-tdc` / `algotrader.adviser-runtime.v6-tdc` / `observe.stream.v7-tdc` |
| Rules manifest | this document (DELTA), the Director's semantic review, then the v0.6 texts (MP-005 … MP-001) |
| Register | `TDC-PARAMETERS.json` = the MP-005 register with identity and status changed, plus the categorical section `trigger_destination_compatibility`. **No new number** |

Shared code: one behaviour-preserving hook in `core3.compute_view` (`_view_support`, `_view_notes`). For v0.3 to v0.6 and v0.6-a2x it returns exactly the previous lists, as shown by the existing byte pins.

## Addendum — WATCH_ONLY wording (13 October 2026, on `b7c1733`)

When the observed hypotheses of a WATCH_ONLY reading include an incompatible ARMED scenario, the reason no longer claims that only WATCH scenarios are present. It reads: `observed hypotheses without current directional support: <family> <direction> <status>[ (recovery condition incompatible with its destination)], … (not a forecast, not a call)`. Each hypothesis keeps its actual status, WATCH or ARMED, and the specific incompatibility reason line is kept.

With WATCH hypotheses only, the v0.6 sentence is unchanged. The criterion, classification, levels, terminals and operational policy are unchanged. The shared hook `core3._watch_only_reason` returns the v0.6 text byte for byte for every other version.
