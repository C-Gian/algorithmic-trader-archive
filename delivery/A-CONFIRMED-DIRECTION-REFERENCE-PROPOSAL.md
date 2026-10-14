# A confirmed direction — proposed descriptive reference comparison

Director proposal, 14 October 2026. **Not authorized for execution; no computation performed.** Existing results on September–December 2025 are known. This proposal is not independent validation and does not reopen E, a2x or the revision branch.

## Decision sought

Does the direction A selects at its first confirmation show more favourable subsequent barrier order than an uninformed choice of direction, with the same observation time, distances and observation horizon?

This evaluates only directional information at confirmation. It does not evaluate unactivated expectations, selection/entry policy, MarketView as a whole, economics or the value of revisions.

## Candidate population

All first A confirmations belonging to scenarios born in [2025-09-01, 2026-01-01), one observation per scenario, including confirmation on revised anchors. Initialization births separate. No selection for call, later destination or revision count. The previous descriptive count is 89; it is known, not a minimum sample requirement.

At the confirmation publication freeze the confirming trade close P, selected direction d, narrative destination B, local invalidation V, tick and the existing registered A hard horizon of four hours. Require positive favourable distance a = d(B-P) and adverse distance b = d(P-V). If not positive or essential evidence unavailable, report not evaluable with reason, never adjust levels.

## One simple reference

An uninformed 50/50 direction choice at exactly the same publication. Evaluate both possible directions deterministically; no random seed, chosen draws or fitted parameters.

The selected direction uses barriers P+d*a and P-d*b.
The opposite direction uses P-d*a and P+d*b.
Thus favourable and adverse distances, starting close, time, instrument and duration are identical; only orientation changes.

This is a price-only reference, not a second scenario recognizer or a simulated trader. It does not say that both orientations would qualify under A.

## Common outcome distinct from native scenario terminals

For each orientation, from complete trade 1m intervals wholly after the confirmation publication:
- favourable barrier contacted first within four hours: Y = 1;
- adverse barrier first, or full horizon observed with no favourable contact: Y = 0;
- both barriers in one interval: ambiguous;
- unavailable, missing or temporally unresolvable observation: incomplete.

A contact known at the horizon boundary is not assumed earlier; fix precise availability/expiry precedence in registration from the existing clock semantics.

For the primary paired comparison, both orientations must have resolved outcomes. Report every excluded pair and its reason, including whether the exclusion differs by orientation. Do not turn ambiguity/incompleteness into failure. Report expiry-without-contact separately even though Y=0 for the declared primary endpoint.

Use a common four-hour price window, not future scenario withdrawals, STALLED or entry/call terminals. Otherwise the candidate and uninformed reference would have different observation rules. Native scenario terminal times are retained only as descriptive markers. Contacts after a native terminal must NOT be called successful original promises: this is a new standardized directional probe, not rescoring the scenario's own promise.

## Sole primary summary

For each resolved pair i:
reference_i = (Y_selected_i + Y_opposite_i)/2;
difference_i = Y_selected_i - reference_i.

Report selected favourable-first count, opposite favourable-first count, reference total, and average paired difference in percentage points. Show the complete paired 2×2 count table and evaluable denominator before the average. No subgroup searches, significance tests or dependence-based intervals.

A positive difference means selected orientation has more favourable-first outcomes under this fixed probe than an uninformed direction choice. It does not establish profits, calibrated probabilities, causal benefit of professional reasoning, generalization or superiority of the operational policy.

Successive/overlapping scenarios are dependent. Report overlap and temporal concentration without treating pair counts as independent market experiments.

## Inputs and limits

Existing frozen v0.6 journal and admitted trade bars already outside the Owner stack, identities verified before use. No new engine run, extraction, acquisition or protected period. No v0.7 result inferred.

The proposed reference controls exact distances at each observation, not context distribution between hypothetical directions. That asymmetry is precisely the direction-selection question, not proof of information beyond every possible contextual reference.

The endpoint, reference and observation horizon are new study conventions and need explicit approval. This proposal intentionally differs from the earlier native-lifecycle descriptions; mixing their success counts is prohibited.

## If approved

Register exact classifier, availability rules, hashes and paired exclusions before calculation. A few hand-derived LONG/SHORT synthetic cases only, no product suite. One tabulation plus reproducibility check on unchanged inputs. No tuning, implementation change or automatic subsequent study.

If the standardized price probe is not the question the orchestrator wants to answer, reject it rather than quietly converting native scenario terminal outcomes into a reference comparison.
