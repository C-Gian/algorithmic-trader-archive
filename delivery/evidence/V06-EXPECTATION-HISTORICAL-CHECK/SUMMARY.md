# Historical check of the v0.6 A/B/C expectations, September–December 2025

**Executor delivery, 13 October 2026.** Design registered before tabulation at `501393c` ([DESIGN.md](DESIGN.md)), with three declared amendments. The Director's review is PENDING.
- **Nature.** A description on exposed development data, from existing artifacts only. No replay, acquisition, Owner access, a2x, E, tuning, evaluator or economic calculation.
- **A call is not an executed entry.** The narrative destination is not a call target.
- **Unchanged.** v0.6 is frozen; the future studies stay INACTIVE.

**Question.** At the first publication of a new conditional expectation, what follow-up does its narrative destination find, respecting the antecedent, the invalidation and the scenario's life?

## 1. Inputs and method

- **Inputs** (verified before use):
  - the pack copy: **21/21**;
  - the 12 October v0.6 journal and its admitted trade 1m bars, plus the 13 October v0.6 journal: hash, entries, kinds, last chain and 226,445 bars with 0 missing, all equal to their committed manifests: **7/7**.
- **Cutoff** (derived from the v0.6 code): the **first published ARM** for A, B and C.
  - It is the first record where the trigger K0, the invalidation V0, the destination, the premise and the original expiry are all published.
  - BIRTH (WATCH) has no trigger or invalidation. For C, BIRTH and ARM can share a dispatch.
  - A hypothesis never armed never became a published expectation; it is counted with its final state.
- **Promise.** As published at the cutoff. The post-activation life is the registered hard horizon: A 4h, B 6h, C 2h.
- **Evaluation.** From the admitted 1m bars, in engine dispatch order: timer, then 1m contacts, then 15m premise, then activation. A V and a B in the same minute is AMBIGUOUS; a B before activation never counts as continuation.
- **Life bound.** No contact after the scenario's terminal recovers a success.
- **Lifecycle and revisions.** Reported separately, never credited to the original promise.
- **Units.** One observation per scenario, at its first ARM. Overlapping scenarios are not independent. No aggregate percentage across families.

## 2. Reconciled tables per family (born in [2025-09-01, 2026-01-01))

| | **A** | **B** | **C** |
|---|---|---|---|
| Hypotheses born | 359 | 44 | 37 |
| … never a published expectation | 198 (188 spent beyond B before reaction; 9 context/adverse expansion; 1 close at/beyond A+z) | 38 (14 returned inside before retest; 13 original deadline; 7 box expiry; 4 context forbidden at birth) | 19 (13 context not BALANCED at birth; 6 directional expansion at birth) |
| **Published expectations (first ARM)** | **161** (89 LONG, 72 SHORT) | **6** | **18** |
| … MarketView role at the cutoff | 160 PRINCIPAL, 1 ALTERNATIVE | 5 PRINCIPAL, 1 ALTERNATIVE | 18 PRINCIPAL |
| … abstention or unavailability at the cutoff (ABSENT / NO_VIEW) | 0 | 0 | 0 |
| Not evaluable / evaluable | 0 / 161 | 0 / 6 | 0 / 18 |
| **Original antecedent activated** (K0 + tick within the life) | **28** | **4** | **12** |
| **Original outcome:** antecedent never activated | 133 | 2 | 6 |
| … original V0 contact before activation | 112 | 2 | 2 |
| … destination before activation (not continuation) | 19 | 0 | 1 |
| … original expiry | 1 | 0 | 1 |
| … scenario ended first (context withdrawal) | 1 | 0 | 2 |
| **Destination reached after activation** | **17** | **2** | **4** |
| Invalidated after activation (V0) | 9 | 1 | 5 |
| Expired without destination (hard horizon) | 1 | 1 | 1 |
| Scenario ended after activation (life bound) | 1 (STALLED) | 0 | 2 (STALLED; PRICE_PREMISE_FAILED) |
| Ambiguous / insufficient data | 0 / 0 | 0 / 0 | 0 / 0 |
| Revised before the original resolution | 9 (all "never activated") | 0 | 0 |
| Revision records after the cutoff | 179 ANCHOR_LOST, 143 REARM, 22 REVISE | none | none |
| Engine confirmations | 89: 28 same levels and time as the original activation, 61 on **revised** levels | 4, all same | 12, all same |
| **Effective lifecycle terminal** | 78 DESTINATION_REACHED, 33 WITHDRAWN context, 28 INVALIDATED V, 12 WITHDRAWN A+z, 4 TIME_EXPIRED, 3 STALLED, 3 EXPIRED original deadline | 2 DESTINATION_REACHED, 3 INVALIDATED, 1 TIME_EXPIRED | 5 DESTINATION_REACHED, 7 INVALIDATED, 2 WITHDRAWN context, 1 each STALLED, PRICE_PREMISE_FAILED, TIME_EXPIRED, EXPIRED |
| Lifecycle destination after a confirmation that is **not** a destination under the original promise | **37** (all original V0 contact before activation, followed by an engine revision and a confirmation on revised levels) | 0 | 0 |
| Scenarios with a call (proposal) / calls | 1 / 1 | 0 / 0 | 0 / 0 |

**Original outcome against the effective lifecycle** (evaluation window):
- **A.** The 17 original destinations are the lifecycle's DESTINATION_REACHED; the 9 original invalidations are the lifecycle's INVALIDATED.
  - The 61 lifecycle destinations of never-activated originals are 24 destinations before any confirmation and 37 after a REARM/revised confirmation.
- **B and C.** Original and lifecycle coincide case by case, apart from the life-bound endings.

**Warmup** (born in [2025-07-28, 2025-09-01), separate):

| | A | B | C |
|---|---|---|---|
| Hypotheses born | 106 | 13 | 12 |
| Published expectations | 45 | 3 | 8 |
| Activated | 6 | 3 | 6 |
| Destination reached after activation | 4 | 3 | 3 |
| Never activated | 39 (33 V0 before activation; 5 destination before activation; 1 scenario ended) | 0 | 2 |
| Other | 1 invalidated with revision before resolution; 1 expired | — | 2 invalidated; 1 expired |

Every table reconciles: born = never published + published; published = evaluable + not evaluable; the outcomes sum to the evaluable; the outcomes with and without revision sum to the evaluable; the view roles sum to the published.

Per-scenario detail: [`out/scenarios.csv`](out/scenarios.csv), one line per scenario (571). It gives the cutoff, the promise (K0, V0, destination and type, premise, expiry), the view role, the revisions, the original outcome bounded and unbounded, the engine confirmation and terminal, and the calls. Full records: `out/observations.json`.

## 3. What is evaluable, the descriptive check, and what stays unjudged

**Evaluable.** All 185 published expectations of the evaluation window: A 161, B 6, C 18. There are 0 not evaluable, 0 ambiguous and 0 with insufficient data. 255 hypotheses never became a published expectation (A 198, B 38, C 19), and their final states are reported.

**Descriptive check under the original promise:**
- **A.** The conditional antecedent at the first ARM was rarely activated: **28 of 161**.
  - **112** lost the original invalidation level V0 before activating.
  - **19** reached the destination before activating; post-hoc, 6 of those 19 (and 14 of the V0 cases) had a trigger already at or beyond B, so their activation could not occur without touching B.
  - Of the 28 activated: **17** destination reached, 9 invalidated, 1 expired, 1 STALLED.
  - The adviser's lifecycle continued through 143 REARM and 22 REVISE. The 37 destinations reached after a revised confirmation belong to the **effective lifecycle, not to the original promise**.
- **B.** 6 expectations, 4 activated: 2 destination, 1 invalidated, 1 expired.
- **C.** 18 expectations, 12 activated: 4 destination, 5 invalidated, 1 expired, 2 ended by the life bound.
- **Calls.** One call for all families: the expectation is not a proposal.

**Interpretation limits:**
- These frequencies **do not demonstrate predictive capability or information beyond the geometry**. The distances between trigger, invalidation, destination and premise largely determine the contact order. The trigger sometimes lies beyond the destination.
- No baseline or comparison was built, as registered.
- Exposed development data; few B and C observations; overlapping scenarios.

**Adviser capabilities left unjudged:**
- the anticipatory correctness of the MarketView direction;
- the value of the revisions (REARM / REVISE) as reasoning;
- the call, its target and its entry window;
- economics and costs;
- the WATCH hypotheses (never a published expectation);
- B and C beyond a handful of cases;
- generalization to other periods (protected or prospective).

## 4. Checks and amendments

- **11/11 checks pass in `results.json`:**
  - one observation per scenario; every first record is BIRTH;
  - every A cutoff = its first-ARM destination-monitoring origin;
  - antecedent text = K0 + tick and V0;
  - causality: resolution at or after the cutoff; activation after the cutoff, before H, and before the resolution and the engine terminal;
  - the registered hard horizon equals the engine `confirmed_deadline` wherever the activation equals the engine confirmation;
  - contiguous coverage with no missing minute; no tail birth.
- **All reconciliations pass.**
- **Self-test 30/30.**
- **Reproducibility.** The tabulation ran twice from the artifacts with identical hashes:
  - `results.json` `342f4d4a…5d17`;
  - `scenarios.csv` `4a80f882…d6dd`;
  - `observations.json` `dfd99e0d…fa87`.
- **Script.** `expectations.py` final sha256 `b538f8990ffa171dc2c95c100ef184deb156c198eb1c82eed81ecafe1d07fd69`.
- **Amendments** ([DESIGN.md](DESIGN.md)):
  1. Base correction: the Owner's checkout was at `9bd8c0a`, three Director documentation commits after `d06960d`. No input or definition is affected.
  2. Parsing of the antecedent-text check: "1m" was read as a level. Only the check changed; `scenarios.csv` is byte-identical before and after.
  3. **Made with the results visible:** the life bound now applies "before activation" when the market activation came after the scenario's end, as §3 states. It moves 3 observations, A and C evaluation and A warmup, from "ended after activation" to "never activated". The case was revealed by reconciling activations against engine confirmations.
- **Post-hoc** (not registered): the count of A triggers at or beyond B.
- **Not run:** DB tests, e2e and CI (no product change).

## 5. Provenance and exposure

- **Artifacts** (outside Git, unchanged): `…/0d87e1fc-…/scratchpad/run/` (12 October processing), `…/48191428-…/scratchpad/run_v06/` (13 October journal), and the pack copy `…/0d87e1fc-…/scratchpad/inputs/data`.
- **Exposure:** register row 15.
