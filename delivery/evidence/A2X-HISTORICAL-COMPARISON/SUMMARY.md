# Descriptive historical comparison v0.6 / v0.6-a2x, September–December 2025

**Executor delivery, 13 October 2026.** Design registered before execution at `306a0b9` ([DESIGN.md](DESIGN.md)); the runs used build `306a0b9a6007c153b438e2ab6d87568270233330`, whose product tree is identical to `5b7f00e`.
- **Review.** The Director's review is PENDING.
- **Nature.** A description on **already exposed development data**. It is not a test and not an evaluation: no economic result, call outcome, P&L or tuning.
- **A published call is not an executed entry.**
- **Unchanged.** v0.6, HDP-001 and the future studies stay frozen and INACTIVE. The variant stays EXPERIMENTAL: not installed or selectable. No product change.

## 1. Inputs and processing

- **Inputs.** The 12 October local copy (pack `pack-1ae7d36c…`, cache `fc-80221b24…`), re-verified: **21/21** ([inputs_verification.json](inputs_verification.json)). No new copy, acquisition or Owner-stack access.
- **Baseline.**
  - The 12 October v0.6 journal is complete. It was judged insufficient by the registered rule: other build, and no complete source lists or birth-step state.
  - So **one v0.6 and one v0.6-a2x processing** were run at the same build, with the passive trace ([run_offline.py](run_offline.py), [instrument.py](instrument.py)).
  - Each policy took 361 s and 364 s; each applied 679,335 events, with finish at 2026-01-01T06:05Z, and no evaluator.
- **Same flow, verified.** Equal input commitment, temporal commitment, pack, cache, feed and build in both runs.
- **The instrumentation is passive on the pack.** The new v0.6 journal equals the 12 October journal entry for entry (**34,507**), with the build, digest and chain removed ([crosscheck_baseline.py](crosscheck_baseline.py), amendment 1).

| | v0.6 | v0.6-a2x |
|---|---|---|
| Journal entries | 34,507 | 34,617 |
| scenario / entry_attempt / observation / market_view | 2,003 / 1,002 / 8,014 / 8,193 | 2,022 / 1,014 / 8,080 / 8,206 |
| call / call_revision / landmark / material_change | 1 / 52 / 15,231 / 11 | 1 / 52 / 15,231 / 11 |

## 2. Reconciled flow per policy (A first attempts born in [2025-09-01, 2026-01-01); successors apart)

Every row reconciles. The identities are checked in `results.json` → `flow.*.reconciliation`.

| Step | v0.6 | v0.6-a2x |
|---|---|---|
| **A impulses born** | **359** | **359** |
| never armed | 198 (188 EXPIRED spent beyond B before reaction; 9 WITHDRAWN context/adverse expansion; 1 WITHDRAWN close at/beyond A+z) | same 198 |
| armed, not confirmed | 72 (33 WITHDRAWN context; 24 DESTINATION_REACHED; 12 WITHDRAWN A+z; 3 EXPIRED original deadline) | same 72 |
| **confirmed (first attempt)** | **89** | **89** |
| … terminal | 54 DESTINATION_REACHED, **28 INVALIDATED V_CONTACT**, 4 TIME_EXPIRED, 3 STALLED | same |
| V failures after confirmation | 28: admissibility not applicable | 28 |
| … admissible: review opened | — | **18** |
| … excluded: review not opened | — | 10 (9 AT_OR_AFTER_ORIGINAL_EXPIRY; 1 CONTEXT_OR_ADVERSE_EXPANSION) |
| reviews closed without successor | — | 14 (6 EXPIRED original deadline; 5 WITHDRAWN context/adverse expansion; 2 DESTINATION_REACHED; 1 WITHDRAWN A+z) |
| **successors armed** | — | **4** |
| … not confirmed | — | 3: 2 EXPIRED *recovery with insufficient residual* (recorded exclusions: 18 and 6 min left); 1 EXPIRED at H0 |
| … **confirmed (successor)** | — | **1** → STALLED (progress below half scale) |
| First-attempt child of the 89 confirmations | 1 ISSUED; 88 not issued: 22 NO_ECONOMIC_RETURN_REGION, 18 PRE_ENTRY_TARGET_CONTACT, 15 scenario DESTINATION_REACHED, 9 INITIAL_RESPONSE_INCOMPATIBLE:HISTORICAL_ECONOMICS, 8 ORIGINAL_SETUP_DEADLINE, 7 AT_OPPOSING_AREA, 4 CONTEXT_FORBIDDEN_PREISSUE, 3 INITIAL_RESPONSE_INCOMPATIBLE:CORRIDOR, 2 scenario INVALIDATED V | identical |
| Successor child of the 1 confirmation | — | not issued: INITIAL_RESPONSE_INCOMPATIBLE:HISTORICAL_ECONOMICS |
| **Calls published** | **1** (first attempt) | **1**, the same call; **0 from successors** |

**Warmup** (born in [2025-07-28, 2025-09-01), outside the population, reported separately):
- In both policies: 106 A impulses, 24 confirmed, 14 V failures, child records identical, 0 calls.
- In the variant: 4 reviews opened, 10 not opened (6 after original expiry, 4 context), 3 closed without successor, 1 successor armed (EXPIRED at H0).

**B and C** (evaluation): B 44 births, 4 confirmed, 0 calls; C 37 births, 12 confirmed, 0 calls. Every count is identical in both policies; warmup B 13 and C 12 likewise.

## 3. Divergence register

**Matching** (registered key: direction + complete ordered sources + A/B + S15 + zone; B/C with the box geometry):
- **571 one-to-one pairs**: A 359 + 106 warmup, B 44 + 13, C 37 + 12.
- **0 non-unique keys, 0 scenarios without a key, 0 unmatched births in either policy.**
- **Every matched chain is identical** (scenario, child, calls and revisions), including the 28 + 14 first attempts that failed at V.

| Divergence type | Count (evaluation + warmup) | Record and verifiable cause |
|---|---|---|
| Common events | 571 pairs, all chains identical | Normalized record equality (`results.json` → `matching`) |
| **Successor added** | **5** (4 + 1) | `SUCCESSOR_ARMED` + the successor ARM record, with lineage `setup.impulse_id` = `parent_scenario_id` = `lineage[1]` = the impulse, checked |
| Review closed without successor | 17 (14 + 3) | `REVIEW_OPEN` → `REVIEW_CLOSED` (state:reason) |
| Review not opened | 20 (10 + 10) | `REVIEW_NOT_OPENED` (reason) |
| **Ordinary birth deferred (link shown)** | **0** | No `ORDINARY_BIRTH_DEFERRED` record. The variant's counter `ordinary_births_deferred` is 0, and no deferral trace event exists |
| Ordinary birth absent or unmatched | **0** in each policy | — |
| Call in one policy only | **0** (1 common call) | — |
| B/C differences | **0** | All B/C chains identical |

The successors in the evaluation window:

| Impulse (birth) | Review | Successor ARM | Course | Outcome in records |
|---|---|---|---|---|
| SHORT 2025-09-09 16:30 | 17:05 | 17:45 | anchor lost 17:46, REARM 18:00, recovery at 18:11 with 18 min left | EXPIRED, insufficient residual (excluded observation) |
| LONG 2025-11-24 21:15 | 21:45 | 22:00 | CONFIRM 22:03; child waits RETURN, reference 22:26 | child INITIAL_RESPONSE_INCOMPATIBLE:HISTORICAL_ECONOMICS; successor STALLED 22:39 |
| SHORT 2025-12-01 05:15 | 06:01 | 06:45 | anchor lost 06:49, REARM 07:00, recovery at 07:08 with 6 min left | EXPIRED, insufficient residual (excluded observation) |
| SHORT 2025-12-19 18:00 | 19:20 | 19:45 | anchor lost 19:51 | EXPIRED at H0 20:00 |

**Other published records** (evaluation window):
- Landmarks, material changes and ordinary observations are identical.
- **Market views differ at 40 dispatches**: 40 view records only in the variant and 29 only in v0.6, the first at 2025-09-03T16:44Z.
- A post-hoc check (amendment 2) finds all 40 inside a variant reservation interval:
  - 29 differ only in the `reasons`, the added reservation line;
  - 11 have a different number of views in the dispatch;
  - **3 change the published reading**: at 2025-11-24 22:30 the variant reads **UP**, and at 2025-12-01 06:45 and 07:00 it reads **DOWN**, with the successor as principal, where v0.6 reads UNCERTAIN.

**Latent state difference, without consequence** (post-hoc, amendment 2):
- The birth-step latch or slot state differs at 19 LONG and 19 SHORT 15m closes, out of 11,712 per direction:
  - during reservations, a2x is reserved where v0.6 is free;
  - after a release, a2x keeps NEED_FALSE where v0.6 is READY, until the next false.
- **At none of them was Q_A true**, so this difference could not change any ordinary birth in this period.

**Selection.** With the slot, conflicts and joint selection active, no selection consequence is observed. The only call is common. The successor's single confirmation went through the ordinary RETURN routing and was not issuable.

## 4. Illustrative sequences (registered criterion: first chronological occurrence per type)

The first occurrences of the three types present are in the initialization. They are reported as registered, without substitution: [results.json](out/results.json) → `examples`, with the records of both policies.

- **Successor added.** SHORT impulse born 2025-08-01 23:00.
  - In both policies: CONFIRM 00:05, then the child INITIAL_RESPONSE_INCOMPATIBLE:HISTORICAL_ECONOMICS at 00:16, then INVALIDATED V at 00:28.
  - The variant only: REVIEW_OPEN 00:28, then SUCCESSOR_ARMED and successor ARM at 00:45 (K 113389.5, V 113703.8, B 112676.6), anchor lost 00:51, EXPIRED at H0 01:00. No call.
- **Review closed without successor.** SHORT impulse born 2025-08-07 03:00. Identical up to INVALIDATED V at 04:10. Then the variant only: REVIEW_OPEN 04:10, REVIEW_CLOSED DESTINATION_REACHED at 04:38.
- **Review not opened.** LONG impulse born 2025-08-11 05:15. Identical up to INVALIDATED V at 07:40, after the original expiry 07:15. Then the variant only: REVIEW_NOT_OPENED AT_OR_AFTER_ORIGINAL_EXPIRY.

Deferred birth, unmatched birth, chain difference and one-sided call have **no occurrence**, so there is no example of them.

## 5. Conclusion (descriptive, with attribution limits)

**What the variant adds in this period:**
- 18 of the 28 V failures after confirmation open a reservation; 4 reach a distinct successor, and **1 successor confirms**.
- **No successor call is published.** The confirmation's RETURN child ended INITIAL_RESPONSE_INCOMPATIBLE:HISTORICAL_ECONOMICS, two recoveries were recorded and excluded for insufficient residual, and two successors expired at H0.
- What does change is the published reading: a reservation line in the views during the reservations (18 in the evaluation window, 22 with the warmup), and in 3 dispatches a directional reading UP/DOWN instead of UNCERTAIN, led by the successor.

**What ordinary behaviour it sacrifices here:**
- **None observed.** The 571 ordinary A/B/C scenarios, their children and the call are identical, and no ordinary same-direction birth was deferred (counter 0).
- The reservation and the latch held after release change the internal state at 38 15m closes, but Q_A was never true there.
- This is a property of this period, not of the policy: the synthetic proofs show that the deferral and the latch can remove an ordinary birth (`test_reservation_defers_an_ordinary_birth_then_releases_with_the_ordinary_latch`).

**Attribution limits:**
- The successors are linked by lineage. The view differences are linked by time interval (post-hoc).
- The absence of deferral rests on the variant's counter, the trace and the records together.
- One period of four months, exposed development data, few events (4 successors, 1 confirmation). It supports no statement on usefulness.
- The absence of extra calls is not a merit, and more calls would not be one.

## 6. Checks

- **26/26 checks pass in `results.json`:**
  - same flow and completeness of both runs;
  - trace facts consistent with every first record, and trace ids = journal ids;
  - one traced birth step per 15m close and direction (11,712 each);
  - no birth in the tail;
  - v0.6 without variant records;
  - lineage and review consistency, every V failure with a review record, at most one successor per impulse;
  - one-to-one matching, reconciled to the births of each policy.
- **All flow reconciliations pass.**
- **Reproducibility.** The tabulation ran twice from the saved journals and traces only, without the engine. The output hashes are identical:
  - `results.json` `ddb0882b…5499`;
  - `impulses.csv` `65da9f91…e9d3`;
  - `divergences.csv` `7ea6fc42…f727`.
- **`compare.py`** is unchanged since registration (sha256 `0b7f00b2…772c`). Its self-test passes 21/21.
- **Amendments** ([DESIGN.md](DESIGN.md)):
  - 1: the cross-check now removes the build from nested envelopes. Only its difference report had been seen.
  - 2: `post_hoc.py` (sha256 `fcec4662…6d41`), written after the results, adds only post-hoc descriptions and changes no registered output. Output `post_hoc.json` `76affbf2…27ec`.
- **Not run:** the 255 DB tests, e2e and CI (none were needed for this description; no product change).

## 7. Artifacts and provenance

- **In Git:** `DESIGN.md`, the scripts, `inputs_verification.json`, `run_manifest_v0.6.json`, `run_manifest_v0.6-a2x.json`, and `out/results.json`, `out/impulses.csv`, `out/divergences.csv`, `out/post_hoc.json`.
- **Outside Git** (session scratchpad, 13 October 2026; hashes in the run manifests):
  - v0.6 journal `21020ce6…2577`, trace `a39a1bbb…a7c9`;
  - v0.6-a2x journal `7e181e91…8ec9`, trace `a799691d…085e`.
- **Input copy:** unchanged since 12 October (exposure register row 11).
- **Exposure:** register row 14.


## Subsequent closure annotation — 13 October 2026

The orchestrator accepted the historical comparison delivered at `d06960d` as descriptive evidence, based on the Director's review. The pending-review statements above belong to the preserved original delivery and are superseded by this annotation. The orchestrator read SUMMARY directly, but did not recalculate the CSV or rerun the engine. The Director's CSV recount and static review remain distinct from the executor's input verification and engine processing.

**Population boundary clarification.** The original conclusion's phrase “two successors expired at H0” includes the warmup successor. In the evaluation population [2025-09-01, 2026-01-01), the four successors are: **one expired at H0, two recoveries excluded for insufficient residual, and one confirmed** (no successor call). Separately, warmup contributes one successor expired at H0. No computation or original result is changed.

**Decision.** v0.6-a2x is retained as an experimental candidate, not promoted; this branch is closed without adaptations or further executions. No reduction of residual time, impulse-life extension or RETURN modification is authorized. Four added reactions, one additional confirmation and three changed conditional-reading dispatches establish behavioural effects, not anticipatory correctness or usefulness. No ordinary birth was displaced in this period; this does not establish harmlessness of the reservation policy in general. Post-hoc checks retain their qualification.

There is no empirical basis here for preferring the candidate to the frozen policy. Any reopening requires a separate motivated decision about the whole policy, including the cost of reservation. v0.6 and the registered studies remain unchanged and INACTIVE. No new activity is activated; CI was not queried.
