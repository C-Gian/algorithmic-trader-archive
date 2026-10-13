# Historical check of the v0.6 A/B/C expectations, September–December 2025 — design registered before tabulation

**Registered by the executor on 13 October 2026, base `d06960d6d7b89263f931bdb8fd6cc62c23f70219`, before any tabulation.**
- At this commit the tabulation of this study has not run. No observation, promise, outcome or count of this study exists or has been consulted.
- Read so far:
  - the input re-verification (families, kinds and times only);
  - the artifact hashes and counts;
  - one ARM record per family, for its field structure only.
- **Authority.** Astra authorized design, registration and execution as one step, relayed by the Owner on 13 October 2026. Only this descriptive historical study is active.
- **Frozen.** v0.6 stays frozen. E and a2x are closed. The future studies stay INACTIVE. No product change.
- **Review.** Executor delivery; the Director's review is pending.

**Question.** At the first publication of a new conditional expectation, what follow-up does its narrative destination find, respecting the antecedent, the invalidation and the scenario's life?

## 1. Inputs (existing artifacts only; no replay, acquisition or Owner access)

| Artifact | Identity / verification |
|---|---|
| Pack copy (outside the Owner stack, 12 Oct) | `pack-1ae7d36c…`, cache `fc-80221b24…`. [`verify_inputs.py`](verify_inputs.py) (logic unchanged) → [`inputs_verification.json`](inputs_verification.json): **21/21**. Initialization [2025-07-28, 2025-09-01), evaluation [2025-09-01, 2026-01-01), tail to 2026-01-01T06:05Z, 0 missing |
| v0.6 baseline journal, 12 Oct processing (build `6a0f22a`) | sha256 `ea3ce997…f0af0` = committed manifest; 34,507 entries, counts and last chain = manifest. Rules `57bf2309…2e66`, register `98ef101e…5bda` (frozen v0.6); every event, finish 06:05Z, no evaluator |
| Admitted trade 1m bars of the same processing | sha256 `06a11024…5abe` = manifest; 226,445 bar observations, 0 non-observations |
| v0.6 journal, 13 Oct processing | sha256 `21020ce6…2577` = manifest. Identical entry for entry to the 12 Oct one (build/digest/chain removed; A2X comparison, amendment 1). Corroboration only; it is not tabulated |

- Verified by [`verify_artifacts.py`](verify_artifacts.py) → [`artifacts_verification.json`](artifacts_verification.json): **7/7**.
- **Not needed:** the passive traces (complete source lists), because no cross-policy matching is done.
- **Not used:** a2x, E, and any evaluator or economic record.

| Script | sha256 at registration (LF bytes as committed) |
|---|---|
| `verify_inputs.py` | `333963c478eeb314ce0a679810eae062fc71f3dfa714edaaa6a2564568be1fa7` |
| `verify_artifacts.py` | `3f65a31b71dae5c4c1881e17c0db0bbb606cd89e7613270a809f037a5b1a4960` |
| `expectations.py` | `6fe9419a8ec3da43489f4a99a2fc3b35f9bafb8fe0dccdf08a4476ee85ff405d` |

`expectations.py --selftest` passes **29/29** before registration:
- every outcome category LONG and SHORT, from hand-built minute paths;
- K0 exactly versus K0 + tick;
- contacts before activation in the same minute;
- the timer at H;
- 15m premise;
- censoring;
- the life-bound precedences;
- a hand-derived integration on the synthetic engine tape `two_calls`.

## 2. Cutoff: one observation per scenario at its first published ARM (from the v0.6 code)

| Family | BIRTH publishes | First ARM publishes | Why the cutoff is the first ARM |
|---|---|---|---|
| A (`core3._new_a`, `core4._publish_anchor`) | WATCH: antecedent text "if a clean reaction and recovery confirm…", destination B, premise; **no trigger or invalidation** | trigger K, invalidation V = R − z, destination B, premise "15m close beyond A", original expiry = birth + 2h; destination monitoring starts here (`destination_monitoring_from`) | The first moment the condition, its failure level, the destination and the deadline are all defined |
| B (`core3._bc_geometry`) | WATCH after the breakout close: destination U + width, premise U − z; **no trigger or invalidation** (retest pending) | at the retest bar: K = max(U + tick, close), V = low − z, expiry min(box expiry, birth + 1h) | Same |
| C (`core3._bc_geometry`) | WATCH and, in the same dispatch if the gates allow, ARM | K = close, V = low − z, destination = frozen midpoint, premise L − z, expiry min(box expiry, birth + 30 min) | Same; for C, birth and arm can coincide |

**Rules for the cutoff:**
- **It is never the CONFIRM.** Antecedents never activated stay visible.
- **A birth that is never armed** is a hypothesis that never became a published expectation. It is counted with its final state:code.
- **REVISE / ANCHOR_LOST / REARM** are revisions (§4), not new observations.
- **MarketView role** is taken from the latest `market_view` published at or before the cutoff. The view is published in the same dispatch after the scenario record, and only on change. The roles are:
  - **PRINCIPAL**: an armed or confirmed scenario leading a single-direction view;
  - **ALTERNATIVE**: in the alternatives, for example in opposing scenarios with the view UNCERTAIN;
  - **WATCH**;
  - **ABSENT**: not in the view, with its table row (e.g. context unavailable = unavailability);
  - **NO_VIEW**.

  The scenario record's existence is never equated with its presence in the view. A WATCH hypothesis is never a confirmed direction.

## 3. The original promise (as published by the ARM record at the cutoff)

**Saved fields:**
- direction and antecedent text;
- `trigger_level` K0, `invalidation_level` V0, `destination` B and its type;
- `premise` and its level P (the number in "15m close beyond P");
- `original_expiry` H, and the setup S15.

**Rules:**
- No later reference is used as original.
- The **post-activation life** is the family's **registered hard horizon** (A 4h, B 6h, C 2h, `params.hard`), counted from the activation publication. This rule is known at the cutoff. The engine's later `confirmed_deadline` is used only to check the rule (§7).
- A missing essential field (K0, V0, B, P, H) makes the observation **NOT_EVALUABLE** with the missing field named. Nothing is invented.

**Evaluation from the admitted trade 1m bars:**
- q = d × price; threshold = K0_q + tick (tick 0.1 × trigger ticks 1, checked against the antecedent text).
- Only minutes starting at or after the cutoff are used; the 15m bars are the complete UTC bars derived from them.

**Order at each minute end t (the engine's dispatch order):**
1. **Timer.** Before activation, t ≥ H gives ANTECEDENT_NEVER_ACTIVATED:ORIGINAL_EXPIRY; the timer precedes, so a recovery available exactly at H does not activate. After activation, t ≥ D (activation + hard horizon) gives EXPIRED_WITHOUT_DESTINATION.
2. **1m contacts of the minute ending at t:**
   - low_q ≤ V0_q and high_q ≥ B_q in the same minute → **AMBIGUOUS**;
   - V0 → before activation ANTECEDENT_NEVER_ACTIVATED:ORIGINAL_INVALIDATION_CONTACT, after it INVALIDATED:V_CONTACT;
   - B → before activation **ANTECEDENT_NEVER_ACTIVATED:DESTINATION_BEFORE_ACTIVATION** (a B reached before activation does **not** demonstrate continuation after it), after it DESTINATION_REACHED.
3. **15m close** ending at t, after the cutoff (or after activation), with close_q < P_q → before activation ANTECEDENT_NEVER_ACTIVATED:PREMISE_15M_CLOSE_BEYOND, after it INVALIDATED:PREMISE.
4. **Activation** (before activation only): close_q ≥ threshold. Contacts in that same minute were processed first.
5. **Data.** A missing minute, or the end of the data (06:05Z) before resolution, gives **INSUFFICIENT_DATA**.

**Life bound** ("no contact after the terminal recovers a success"). The scenario's last journal record, when TERMINAL, ends the promise when it is earlier than the resolution, or at the same dispatch with an earlier rank. The ranks are timers and staleness, then 1m intervals (contacts, progress), then 15m closes and gates. At the same rank, a different kind also ends it. The result is then:
- before activation: ANTECEDENT_NEVER_ACTIVATED:SCENARIO_ENDED:<terminal>;
- after it: SCENARIO_ENDED_AFTER_ACTIVATION:<terminal> (STALLED, context withdrawal, …).

The unbounded market result is kept alongside for inspection.

**Distinctions:**
- The narrative destination is never the call's target.
- A call is linked only to tell an expectation from a proposal: count only, with no call outcome and no assumed executed entry.

## 4. Revisions

**Recorded:** every scenario record after the cutoff with REVISE, ANCHOR_LOST or REARM, with its time, K, V, expiry and destination. The engine CONFIRM is recorded too: time, K, V and `confirmed_deadline`.

**The original promise is immutable.** Each observation states three things separately:
1. **Under the original promise:** the §3 result, which uses K0, V0, B, P, H and the rule horizon only.
2. **Substantial revision:** `revised_before_resolution`, meaning a revision strictly before the original resolution; and the engine confirmation compared with the original: SAME_LEVELS_SAME_TIME / SAME_LEVELS_OTHER_TIME / REVISED_LEVELS. The original outcomes are tabulated without and with a revision before resolution.
3. **Effective lifecycle:** the engine terminal state:code.

A lifecycle DESTINATION_REACHED after an engine confirmation that is not DESTINATION_REACHED under the original promise is counted separately. It is never credited to the original promise.

## 5. Population, units, tables

**Population and units:**
- All A, B and C scenarios whose BIRTH is in [2025-09-01, 2026-01-01). Scenarios born in the initialization are in **separate warmup tables**. A tail birth fails a check.
- The unit is the **scenario**: one observation at its first ARM. Journal record counts are never used as durations or as independent observations. Overlapping scenarios are not independent.

**Per family and window, reconciled:** hypotheses born → never published (by final state) / published → view role at the cutoff (and the row when absent) → not evaluable / evaluable → original activation → original outcome by category:detail, without and with revision → engine confirmation compared with the original → engine lifecycle terminal → scenarios with a call.

**Not given:** aggregate percentages across families, subgroup searches, or comparisons with any baseline or geometry.

**Outputs:** `out/results.json` (tables, checks), `out/scenarios.csv` (cutoff, promise, view role, revisions, outcomes, lifecycle and calls per scenario), `out/observations.json`.

## 6. Interpretation limits (fixed now)

- A destination reaching frequency is **not** predictive capability, and not information beyond the geometry: the distances to B, V and the premise largely determine contact orders. No artificial comparison or new parameter is introduced to say otherwise.
- The data are exposed development data (exposure register rows 1–5 and 11–14). This is a description, not a test.

## 7. Checks

- **Uniqueness:** one observation per scenario id; every first record is BIRTH.
- **Cutoff:** every A cutoff equals its `destination_monitoring_from` (first ARM).
- **Antecedent:** the text equals K0 + tick and V0.
- **Causality:** resolution at or after the cutoff; activation strictly after the cutoff and before H.
- **Rule:** the registered hard horizon equals the engine `confirmed_deadline` wherever the original activation coincides with the engine confirmation at the same levels.
- **Coverage:** contiguous minutes with no missing one; no tail birth.
- **Reconciliations:** every table.
- **Reproducibility:** the tabulation runs twice from the artifacts, with identical output hashes.
- **Definitions:** fixed now. A necessary correction after results is appended as an amendment, saying what had been seen.

## Amendments

1. **Base correction, 13 October 2026, after the registration commit `501393c` and before any tabulation.**
   - **Error.** The header names the base `d06960d`. The checkout given by the Owner was actually at `9bd8c0a`.
   - **Why.** It held three Director documentation commits after `d06960d` (`3992050`, `eeca812`, `9bd8c0a`: A2X closure annotations in SUMMARY, STATE and task).
   - **Impact.** These commits change no product file, input, script or definition. The registration content is unaffected, and `501393c` is a normal descendant of `9bd8c0a`.
   - **What had been seen.** No result of this study had been seen.
