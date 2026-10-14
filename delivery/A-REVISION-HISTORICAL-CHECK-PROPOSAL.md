# A revisions — proposed historical descriptive check

Director design, 14 October 2026. **Proposal only; execution not authorized or performed.** Prepared from the frozen v0.6 anchor code and the existing historical-check design/committed record structure. Previously reported outcomes are already known: this is not a preregistration on unseen data.

## Question and scope

For each A scenario, how does the sequence of published local conditions evolve before the first confirmation, and what follows the condition that actually confirms within the scenario's effective life?

This describes updating, not the incremental predictive value of revision. Publication before a subsequent move is a causal requirement, not proof that the system anticipated it. No comparison against a fictitious no-revision policy is proposed.

Use only the existing v0.6 September–December 2025 journal and admitted trade 1m bars outside the Owner stack. No engine replay or acquisition. These artifacts describe v0.6, not a historical execution of v0.7. Trigger/destination compatibility may be annotated using the exact approved criterion, but no v0.7 MarketView or whole-policy result is inferred.

## Unit and complete population

All A scenarios born in [2025-09-01, 2026-01-01), LONG/SHORT; initialization births separate. One scenario is one unit, including never-armed and never-confirmed cases. No selection on destination, call or revision count.

Within each scenario retain the complete ordered chain:
BIRTH → ARM → any REVISE / ANCHOR_LOST / REARM → first CONFIRM or unconfirmed terminal → confirmed terminal.

Anchor epochs are descriptive segments, not independent observations. Repeated publications are not counted as independent forecasts.

## Segment boundaries and immutable conditions

An ARM/REVISE/REARM starts a condition segment at actual publication time/cursor. Freeze its K, V, B, direction, premise, source, epoch and original setup expiry. A superseding publication ends the prior segment prospectively; ANCHOR_LOST ends local support and starts an observation-only gap. Neither rewrites the earlier condition.

Audit ordering using publication and admitted cursor, not only candle market time. A source bar used to construct an anchor is context, not a later confirming event. Only an eligible complete 1m interval admitted after the publication, with start at/after it, can confirm. Preserve ambiguous straddling/late intervals under the existing anchor-domain rules; do not infer intrabar order.

In q = direction × price, Tq = Kq + tick × trigger_ticks. Annotate Tq < Bq as compatible and Tq >= Bq as incompatible. A compatible threshold is only feasibility of continuation before B, not favorable evidence or entry availability.

Dispatch order remains the engine's: timers, interval contacts, 15m predicates/revision, confirmation. The journal sequence decides boundaries sharing a dispatch; never credit the source interval or a pre-publication contact as post-revision confirmation.

## Outcomes and the single scenario-level table

For each anchor segment classify its end as:
- confirmed on this epoch;
- superseded by revision without confirmation;
- local anchor lost (certified contact or ambiguous contact, distinguished);
- destination contact before confirmation;
- original setup expiry / structural or context terminal;
- data unavailable or insufficient record linkage.

After the first confirmation, freeze the confirmed epoch and use the engine's published confirmed deadline and actual terminal. Report destination after confirmation, local invalidation, expiry, STALLED/context/other terminal, ambiguity and data loss separately. A destination in an observation-only gap or before confirmation is not continuation following an activated condition.

At scenario level reconcile:
never armed / armed but never confirmed / confirmed on first anchor / confirmed on revised or rearmed anchor.
For the two confirmed groups cross-tabulate actual terminal categories. This is the only primary comparison, **descriptive and selected by confirmation**. Do not interpret differences as the benefit of revision: paths, geometry and confirmation selection differ.

Report the non-confirmed groups and their terminals alongside, and segment end counts with the explicit label “publications, not independent scenarios”. No aggregate accuracy score, economic result, significance test, subgroup search or parameter changes.

## Evidence and feasibility limit

The committed observations retain revision times and K/V, but not the complete publication cursor/source/domain chain. They are not sufficient alone. Execution requires the already-authorized full journal and admitted bars from the existing local copy, with identities reverified. If unavailable, stop; no Owner extraction or new replay is included.

Checks: all births accounted for; ordered, non-overlapping segment domains; one confirmation epoch maximum; fixed B/setup expiry; no retroactive confirmation; each claimed confirmation matches the journal and its contemporaneous levels; scenarios and terminals reconcile.

Three illustrative sequences selected by first chronological occurrence of each type, not outcome:
revision while armed; loss → WATCH gap → rearm; revised anchor that never confirms.
Show publication/source/first eligible later interval, then the segment ending.

## Decision requested

Authorize one offline tabulation from those existing artifacts, after committing exact input/script identities and the completed implementation conventions before execution. No market run, product change, new data, tuning or economic evaluator.

This can show how existing revision rules operate and which subsequent developments follow their activated formulations. It cannot establish whether revisions improve forecasts, beat geometry or outperform an alternative policy. v0.6/studies remain frozen; E and a2x remain closed.
