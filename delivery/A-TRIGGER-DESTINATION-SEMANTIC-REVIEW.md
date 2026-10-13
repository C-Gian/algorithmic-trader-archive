# A trigger at or beyond its destination — semantic review

Director static review, 13 October 2026. Reference: `41f9edffa6bad262466a957fc4d22c5beb5b4230`. Code, specifications and previously committed observations only; no engine execution, subsequent-price search, acquisition, Owner access or CI query.

## Decision

**Contradiction between the published conditional promise and the contact/confirmation rules for the current anchor.** It is not evidence of a wrong contact precedence, nor a finding that the entire impulse or later revisions cannot be useful.

The actual ARMED antecedent says that a later eligible complete 1m close at the trigger “confirms continuation toward” B. In the examined geometry, that close necessarily implies a contact with B. The engine processes that contact before confirmation and ends the scenario. The antecedent therefore cannot produce the stated continuation under these same levels.

## Direction, tick, borders and order

Let `d = +1` for LONG and `-1` for SHORT, and transform prices into `q = d × price`. The actual inclusive confirmation threshold is `Tq = d × K + tick × trigger_ticks`, not K alone. Here tick = 0.1 and trigger_ticks = 1.

When `Tq >= d × B`, a complete 1m close satisfying the trigger necessarily has transformed high at or beyond B. Destination contact is inclusive. In the ordinary dispatch, scenario timers precede interval contacts; contacts precede the subsequent confirmation pass. A B contact terminates A as DESTINATION_REACHED, or as UNASSESSABLE when combined with a local contact or uncertain interval boundary. It does not become a confirmation. Expiry can terminate it still earlier.

Source: `core3.py` (`_antecedent`, confirmation, dispatch and MarketView strong-scenario selection); `core4.py` (`_scen_interval`, first-ARM monitoring origin); MP-002 MarketView rules and MP-003 prospective anchor/destination rules.

A's initial source bar ends at/before the first-ARM monitoring origin and is not retrospectively tested for destination success. This explains how such an anchor can be published without a prior terminal. It does not make the later stated antecedent feasible.

## Three existing publication examples

Times UTC. Selected for LONG, SHORT and the K = B border, not subsequent outcome.

| Scenario / first ARM | Published required close | B | Meaning |
|---|---:|---:|---|
| AL-2025-09-01T18:45:00+00:00-52af2866da89 / 19:15 | >= 109263.9 | 109244.6 | Required LONG close already beyond B |
| AS-2025-10-05T19:45:00+00:00-10257c4c571a / 20:15 | <= 122430.9 | 122439.4 | Required SHORT close already beyond B |
| AL-2025-10-01T01:45:00+00:00-a69d2cdba4e7 / 02:15 | >= 114500.1 | 114500 | K equals B; the added tick makes the required close beyond B |

The recorded sentences explicitly say “confirms continuation toward” the destination in each row. These are recorded engine publications, not an interpretation invented by the historical classifier. Each is PRINCIPAL in MarketView, with expected direction UP or DOWN and CONDITIONAL_SCENARIO.

Source: `delivery/evidence/V06-EXPECTATION-HISTORICAL-CHECK/out/observations.json`. The original post-hoc count remains qualified as such: 20 of 161 A first publications, 12 LONG and 8 SHORT. The verdict rests on the geometry and code, not their later outcomes.

## Why revisions do not resolve the wording

REVISE/REARM can prospectively replace K and V and make a later antecedent feasible. That is a revised formulation; it cannot retroactively validate the earlier “confirms continuation toward B” sentence. The broad impulse may remain under observation, but its survival alone does not support that impossible current antecedent.

No explicit specification was found that deliberately qualifies this geometry's published sentence as provisional or impossible. The specifications allow the anchor lifecycle; they do not supply that missing qualification. Accordingly this is not classified merely as a documented limitation or a coherent provisional promise.

## Minimum correction proposed — not implemented

Keep impulse recognition, anchor history, revisions, B, tick, contact precedence and timers unchanged. At publication, when the actual normalized threshold is at or beyond B:

- state that **the current recovery condition would already require reaching the destination, so it cannot confirm a continuation toward that destination under the current levels**;
- preserve the scenario as an observed hypothesis eligible only for the existing prospective revision rules, without promising that a revision will occur;
- do not count this infeasible ARMED antecedent as support for a current directional conditional expectation in MarketView. Evaluate other eligible scenarios normally; do not force the entire view to UNCERTAIN if another coherent published expectation supports it.

This is a proposed semantic publication/selection correction, not an added entry filter, a tuned threshold or a change to the frozen method. It requires a decision before implementation, including explicit identification separate from frozen v0.6. No new state, record schema or UI implementation is prescribed by this review.

The historical classification and original delivery are preserved. v0.6 remains frozen; E and a2x remain closed; future studies remain INACTIVE.
