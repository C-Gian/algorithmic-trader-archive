# A revisions — how the published thesis evolves and which formulation is confirmed (v0.6, Sep–Dec 2025)

**Executor delivery, 14 October 2026.** The Director's review is PENDING.
- **Design** at `91578fc`. **Registration** committed before tabulation at `bd6f1fa` ([REGISTRATION.md](REGISTRATION.md)). One declared amendment (§8).
- **Nature.** A description on exposed development data, from existing local artifacts only. No replay, extraction, acquisition, engine run, product change, economic figure or v0.7 evaluation.
- **Already known.** The results of the earlier studies on the same artifacts were known before this registration (registration §0).
- **Frozen.** v0.6 and HDP-001 stay frozen; future studies stay INACTIVE.

## 1. Inputs and method

**Inputs.** The local 12 October v0.6 journal and its admitted trade 1m bars, re-verified **6/6** against the committed manifest ([inputs_verification.json](inputs_verification.json)):
- hashes `ea3ce997…f0f0` / `06a11024…6abe`;
- 34,507 entries;
- 226,445 bars, 0 missing;
- frozen v0.6 identity on every record.

**Unit and chain.**
- **Unit.** One A scenario. Population: born in [2025-09-01, 2026-01-01), **359**; warmup births separately, 106.
- **Chain.** The scenario's own records in journal order. Every ARM / REVISE / REARM is an immutable **formulation**, with:
  - its levels (K, R, V, B, T = K + tick);
  - its **observed** source 15m bar;
  - its **publication** time and admitted **cursor**.
- **Anchor loss.** An ANCHOR_LOST opens an observation-only **gap** (WATCH).
- **Confirmation.** At most one CONFIRM, linked to its own epoch, followed to the scenario's actual terminal.

**Bars only corroborate:**
- the source levels;
- every claimed contact or confirmation minute;
- the absence of an unrecorded contact or confirmation inside each domain.

**Trigger/destination compatibility** is **derived** with the later criterion (Tq ≥ Bq incompatible). It is not a v0.6 verdict.

**Result of the corroboration:**
- every chain links;
- **0** scenarios NOT_RECONSTRUCTABLE;
- **0** unrecorded V, destination or qualifying minutes;
- each confirming minute is the first qualifying minute of its formulation.

## 2. Reconciled scenario table

| | Evaluation (born Sep–Dec 2025) | Warmup (separate) |
|---|---|---|
| **A scenarios born** | **359** | 106 |
| Never armed | 198 (188 spent beyond B before reaction; 9 context withdrawal; 1 close at/beyond A+z) | 61 (60 spent; 1 context) |
| **Armed (first ARM published)** | **161** | 45 |
| … armed, never confirmed | **72**: | 21: |
| … … destination before confirmation, while armed | 21 | 5 |
| … … destination in an observation gap (not a continuation) | 3 | 1 |
| … … original setup expiry | 3 | 0 |
| … … structural / context terminal | 45 | 15 |
| … **first confirmation on the original formulation** (epoch 1 = first ARM) | **28** | 5 |
| … **first confirmation on a later formulation** | **61**: 54 REARM, 7 REVISE | 19: 16 REARM, 3 REVISE |
| … not reconstructable / ambiguous / data loss | 0 / 0 / 0 | 0 / 0 / 0 |

**Reconciliation:**
- born = never armed + armed;
- armed = never confirmed + confirmed on original + confirmed on revised + confirmed on rearmed + not reconstructable;
- every detail sums to its category.

**Paths.** All 61 confirmations on a later formulation followed at least one certified anchor loss. None came from a revision without a loss.

## 3. What follows the formulation actually confirmed

**Descriptive, selected by confirmation.** Each column is the scenario's actual terminal after the formulation that confirmed. A difference between rows is **not** evidence that revisions help: paths, geometry (B−T, §4) and the selection by confirmation differ. No percentage is compared.

| Confirmed formulation | Destination | V contact | Hard deadline | Stalled | Total |
|---|---|---|---|---|---|
| Original (first ARM) | 17 | 9 | 1 | 1 | 28 |
| Revised or rearmed | 37 | 19 | 3 | 2 | 61 |
| *Warmup:* original | 4 | 0 | 1 | 0 | 5 |
| *Warmup:* revised or rearmed | 5 | 14 | 0 | 0 | 19 |

The results after a revision belong to the formulation that confirmed, never to the first promise.

**Children and calls**, kept separate from scenarios:
- the 359 children end mostly with their scenario's terminal, or with the child's own v0.5/v0.6 conditions (no economic return region 22, pre-entry target contact 18, initial response incompatible 12, …);
- **one** child issued a call: `call-AL-2025-10-26T23:34…`, which is not an execution.

## 4. How the published formulations change

**Formulation and gap ends.** These are publications, not independent scenarios.

| Formulation | Count | Confirmed on it | Superseded by REVISE | Anchor lost (certified) | Destination before confirmation | Setup expiry | Structural / context |
|---|---|---|---|---|---|---|---|
| ARM | 161 | 28 | 9 | 103 | 19 | 1 | 1 |
| REARM | 143 | 54 | 10 | 66 | 2 | 2 | 9 |
| REVISE | 22 | 7 | 3 | 10 | 0 | 0 | 2 |
| **WATCH gaps** | **179** | ended by REARM 143 · destination in gap 3 · structural/context 33 | | | | | |

**Supplementary description** ([describe.py](describe.py) → `out/supplementary.json`). This was **not registered**: it was computed after the tabulation from `formulations.csv` only.
- **The destination B never changes** within a scenario. Every REVISE and REARM publishes a strictly deeper reaction:
  - R and V move against the direction (median −12.5 for REVISE, −111.1 for REARM, in q units);
  - K usually moves too (median −86.4 / −137.1), occasionally the other way (max +16.5 / +185.5).
- **The conditional distance to B grows.** Median B−T at publication: ARM 86.9, REVISE 266.9, REARM 285.4 (q units). This geometric difference alone forbids reading §3 as a revision benefit.
- **Derived incompatibility exists only on first ARMs:** 20 of 161 (T at or beyond B). None was confirmed: 12 anchor lost, 6 destination before confirmation, 2 superseded. No REVISE or REARM was derived-incompatible (minimum B−T 41.8 and 50.4).
- **Confirmed epoch:**
  - epoch 1: 28;
  - epoch 2: 38;
  - epoch 3: 15;
  - epoch 4: 6;
  - epoch 5: 2.
- **Formulations per armed scenario never confirmed:**
  - 1 formulation: 32;
  - 2: 16;
  - 3: 19;
  - 4: 3;
  - 5: 2.
- **Observation gaps** lasted a median of 11 minutes (0–40).
- **Dispatch order, one visible case.** In `AS-2025-10-05T19:45…`, the REARM3 published at 20:45 had a qualifying minute 20:59 admitted in the 21:00 dispatch. That same dispatch's context withdrawal ended the scenario first: timers, contacts and 15m predicates precede confirmations. The minute is reported, never credited.

## 5. Illustrations (chosen by type: the first evaluation-window occurrence in birth order; not by outcome)

Times are UTC; levels are prices; c = admitted cursor; source = the observed 15m bar.

1. **Destination before confirmation, derived-incompatible.** First occurrence of both types: `AL-2025-09-01T18:45…`, LONG.
   - ARM1: source 19:00–19:15, published 19:15 (c154665). K 109263.8, T 109263.9, V 109103.945, **B 109244.6**, so T is beyond B.
   - The first eligible interval is 19:15–19:16.
   - Destination contacted at 19:25 while armed, before any confirmation. That is not a continuation; the child ended with the scenario.
2. **Anchor loss → WATCH → REARM.** `AL-2025-09-03T14:30…`, LONG, B 112465.
   - ARM1: source 14:45–15:00, published 15:00 (c162540). K 112450, T 112450.1, V 111997.355.
   - V contact, loss at 15:23. Gap 15:23 → 15:30.
   - REARM2: source 15:15–15:30, published 15:30 (c162630). K 112150, T 112150.1, V 111826.055.
   - Confirmed by the 15:36 minute (dispatch 15:37); deadline 19:37. Terminal **V contact** at 16:44.
   - The child ended INITIAL_RESPONSE_INCOMPATIBLE (historical economics); no call.
3. **Revision while armed.** `AL-2025-09-05T02:15…`, LONG, B 111413. Observed and published differ: the ARM source bar is 02:30–02:45, published 03:00.
   - ARM1 is derived-incompatible (T 111429.7 > B). It was lost at 03:13.
   - REARM2 (03:15) was lost at 03:28.
   - REARM3 (03:30, K 111237.6) was **superseded** at 03:45 by REVISE4 (source 03:30–03:45, c169155). REVISE4 has K 111153.2, R 111050, V 111021.435.
   - Confirmed by the 03:46 minute; terminal **destination** at 04:53. The child ended in the no economic return region; no call.
4. **Revised/rearmed formulation never confirmed.** `AL-2025-09-05T07:45…`, LONG, B 112988.9.
   - ARM1 08:15 and REARM2 08:30 each lost to V, at 08:18 and 08:50.
   - REARM3 09:00 lost at 09:03. REARM4 09:15 (K 112588.8, V 112407.95) lost at 09:18.
   - Gap ended by a **context withdrawal** at 09:30: four formulations, none confirmed.

Every sequence: `out/sequences.json`, with all records, segments, levels and times. Each scenario row in `out/scenarios.csv` carries its path, for example `ARM1[ANCHOR_LOST_CERTIFIED]>WATCH[REARM]>REARM2[CONFIRMED_ON_THIS_FORMULATION]`. Every formulation and gap: `out/formulations.csv`.

## 6. What the first-formulation study represented, and what it left out

**What it represented.** The earlier expectation check (`V06-EXPECTATION-HISTORICAL-CHECK`, cutoff = first ARM) described the **first published conditional thesis** of each armed A scenario: 161 formulations.
- **28** were confirmed on that formulation, and this study's original-group follow-up is the same: 17 destination, 9 V, 1 deadline, 1 stalled.
- The rest ended by certified anchor loss (103), destination before confirmation (19), supersession (9), expiry (1) and structural withdrawal (1).
- 20 first formulations had a trigger at or beyond B; this study classifies them DERIVED-incompatible.

**What it left out, by construction.** The life of the scenario after its first formulation:
- **179** observation gaps and **165** later formulations (143 REARM, 22 REVISE).
- Each later formulation was immutable with its own levels:
  - the same B;
  - a deeper R and V;
  - mostly a lower K;
  - a larger distance to B.
- **61** first confirmations (54 rearmed, 7 revised) occurred on those later formulations, always after an anchor loss. Their follow-ups: 37 destination, 19 V contact, 3 hard deadline, 2 stalled. These are the 37 "lifecycle destinations after a revised confirmation" of the earlier study, now linked to the formulation that actually confirmed.
- 57 of the 103 lost first formulations and 4 of the 9 superseded ones led to such a later confirmation.
- 72 armed scenarios were never confirmed on any formulation, 40 of them after more than one formulation.

**What neither study establishes:**
- whether revising improves anticipation;
- whether it beats a fixed-geometry or no-revision policy;
- whether any formulation has value beyond its geometry.

The confirmed groups are selected by confirmation, and their levels differ systematically. The scenario, its child and its call remain distinct: one call in four months.

## 7. Checks and reproducibility

- **Checks: 8/8 pass** in `results.json`:
  - every A scenario once;
  - one BIRTH each;
  - journal sequence strictly increasing and record ids unique;
  - segments ordered with non-overlapping domains;
  - epochs 1..n;
  - at most one confirmation, on its last formulation, linked to its epoch and derived-compatible;
  - no tail birth;
  - each confirming minute is the first qualifying minute (amendment 1).
- **Reconciliations:** 6/6 per window.
- **Synthetic discriminating cases:** **34/34** ([selftest.json](selftest.json)).
- **Reproducibility.** The tabulation ran twice from the same artifacts, without the engine. Identical hashes:
  - `results.json` `18f440dd…51ff`;
  - `scenarios.csv` `ac46b99b…340d`;
  - `formulations.csv` `6624b0f2…5c69`;
  - `sequences.json` `821d4b2f…ead5`.
- **Script.** `revisions.py` final SHA-256 `fed62bfd80093cb64c55b6bd6f22d8b7d5ed29ad5a6e18a792cb983dc9afca9e`; at registration `9bdf912d…2719`.

## 8. Amendment (made with results visible)

**Amendment 1 — audit label of the confirming minute.**

*What was visible.* The first registered run (`results.json` `848babe9…`) had already shown:
- all checks and reconciliations passing;
- every table of §§2–4;
- a bar-audit count of 114 `QUALIFYING_MINUTE_IN_ENDING_DISPATCH`.

*The defect.* Broken down by segment end, 113 of the 114 were the recorded confirming minute itself (89 evaluation, 24 warmup), which the registered note was not meant to include ("qualifies for the **old** formulation"). The other note was the context-withdrawal case of §4.

*The change.*
- The confirming minute is no longer reported as an audit note.
- A new check verifies that it is the first qualifying minute of its domain. It passes for all 113.
- Audit notes are broken down by window and segment end.

*Effect.* No classification, table or count changed. Only the audit columns and `results.json` changed.

## 9. Limits

- **One engine, one run.** It is v0.6's own account of itself, on one exposed development period. It says nothing about v0.7 (its MarketView or its policy).
- **Categories empty in these data.** The ambiguous, data-loss and not-reconstructable categories exist and are tested synthetically, but they are empty here.
- **The bars corroborate the journal; they do not judge it.** Nothing counterfactual was computed.
- **Dependence.** Overlapping scenarios and successive formulations are not independent.
