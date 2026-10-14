# Historical study of the complete v0.7 policy — registration before any computation

**Executor registration, 14 October 2026.** Committed **before** any v0.7 run or outcome. Astra's authorization, relayed by the Owner.

**Scope.**
- Two periods, **kept separate and never aggregated**: January–April 2025 and September–December 2025.
- Each runs on its already available pack, outside the Owner stack.
- The policy is the complete ordinary v0.7 one: A/B/C, revisions, conflicts, selection, calls and protections together, with no a2x content.
- **Not authorized:** new acquisition, Owner installation, alternative entry, tuning or other periods. v0.6, HDP-001 and the prospective studies stay unchanged and INACTIVE.

## 0. Checkout, known results, exposure

**Checkout.** `main` at `cb6f7bacecd238d358129e1a1d3044298d7b3b76`, two Director documentation commits after `6df3768`. No pull or fetch. The build of both runs is **the commit containing this registration**, recorded in each run manifest.

**Known before registration:**
- **v0.6 call lists of the same packs** (metadata, no outcome; v0.7 is documented to issue the same calls as v0.6):
  - September–December: 1 A LONG call, 2025-10-26 23:34Z;
  - January–April journal: 7 calls. 3 were issued during the initialization (2024-11-28, 12-01 and 12-05; A SHORT). 4 were issued in the evaluation window: 2025-01-08 B SHORT, then A SHORT on 2025-01-23 and 2025-02-03, then A LONG on 2025-04-15.
- **Earlier native and descriptive results:**
  - the confirmation → opportunity paths (1 of 89 confirmations issued);
  - the expectation, revision and directional-probe studies;
  - the Owner's earlier economic runs of v0.2–v0.5 on September–December. The executor has not computed any v0.6 or v0.7 economic outcome of either pack.

**Exposure.** January–April 2025 exposure is **not completely documented** ([preliminary report](../../A-CONFIRMED-DIRECTION-REPLICATION-PRELIMINARY.md)). September–December 2025 is exposed development data (exposure register rows 1–18).

**January–April authorization.** Extended by a later annotation on [A-CONFIRMED-DIRECTION-REPLICATION-AUTHORIZATION.md](../../A-CONFIRMED-DIRECTION-REPLICATION-AUTHORIZATION.md).
- Its pinned SHA-256 in `study_presets.json` is updated to the annotated text; the preset, its identity and the pack identity are unchanged.
- The preset stays `offline_only`: Workbench exclusion and app refusals unchanged.
- **No product code change** is needed: the offline runner uses no app route.

## 1. Frozen identities

**Method v0.7:**
- `btc.context-action.v0.7` / `tdc.rules.v0.7` / `adviser.core.v7`;
- rules SHA-256 `1f3704f4453bc3ab7528e9de916d05d64e2e0955c0ef81170c26694bf719b39f`;
- register SHA-256 `8525ec74e2ccbaf0834137312c05aff59bae4714a76221d9f42b426ea7d5569c`;
- runtime `algotrader.adviser-runtime.v7`, engine `observe.stream.v8`;
- status ENGINEERING_REVIEW_PENDING; the closure is recorded as accepted.

**Evaluator:**
- `adviser.evaluator.v3`, identity SHA-256 `85504d5843e144d0b86a0ee3e693c064f4d7f64e7928c1e54fb9c9e9f308615c`, the same for both packs;
- **PRIMARY** `mp002.evaluation.primary.v1`:
  - entry delay **60 s**, exit delay 60 s, UTC ceil-minute boundary;
  - opening condition: pre-open evidence plus the minute's own OPEN geometry, no future H/L/C;
  - adequacy envelope 14 bps;
- **costs:** fee **0.0005/leg**, allowance **0.0002/leg**; stress allowance 0.0005/leg (sensitivity only);
- **funding:** PRICE_NET_ONLY;
- secondary paths (ENTRY_DELAY_0 / ENTRY_DELAY_120 / HORIZON_ONLY) are context only.

**Historical profile:** HISTORICAL_BASE execution, dislocation ENABLE_WHERE_SUPPORTED, `funding_outcomes` PRICE_NET_ONLY (funding coverage `EMPTY_UNKNOWN` in both packs), origin HISTORICAL_MODELED; capability profile SHA-256 `7c868337…0296`.

## 2. Packs, initialization, continuity, windows

| | January–April 2025 | September–December 2025 |
|---|---|---|
| Pack | `pack-ec195b0b4bee44ee5d9c3c564ab8aa9631ed8fd4` | `pack-1ae7d36c20adbde0a468a7e0f6d8750a9951aa8e` |
| Manifest SHA-256 | `b7f4ddb885a6e60fe5418ded18c141ea33ef2552eca13a60ca2e0094a74c5e7c` | `1bec1f1575306d4444969569675e28bfdc9dac60e2d6f461b283871362221f92` |
| Feed cache | `fc-200b0433…` (manifest `f1b114b3…`) | `fc-80221b24…` (manifest `95478a50…`) |
| Content identity | `feedcontent.v1:a0142cae…` | `feedcontent.v1:f2cf8790…` |
| Events | 670,695 | 679,335 |
| Local copy | session scratchpad `replica/data` (prepared offline, verified 10/10) | scratchpad `0d87e1fc…/inputs/data` (read-only copy of the Owner pack, verified earlier) |
| Classification | REGISTERED_STUDY_WINDOW + HISTORICAL_REPLICATION (offline_only) | DEVELOPMENT |
| Initialization (not evaluated) | [2024-11-27, 2025-01-01), 840 h | [2025-07-28, 2025-09-01), 840 h |
| Evaluation | [2025-01-01, 2025-05-01) | [2025-09-01, 2026-01-01) |
| Tail / clock end | to 2025-05-01T06:05Z | to 2026-01-01T06:05Z |

**Continuity.** One continuous run per pack: one WARMUP→EVALUATION transition at the evaluation start, no monthly reset or finish, the ordinary tail semantics and a finish at the clock end.

## 3. Cohorts and boundaries

- **Calls (primary cohort):** every A/B/C call issued in [evaluation start, evaluation end). These are exactly the calls the evaluator consumes (`_in_window`).
  - Calls issued during the initialization are cleared at the evaluation start and have no path. They are listed as a boundary, never scored.
  - No call can be issued in the tail (EVALUATION_WINDOW_ENDED); a check verifies it.
- **Scenarios (funnel):** born (BIRTH publication) in the evaluation window, by family. A call whose scenario was born before the evaluation start is counted as a call and flagged.
- **Stages kept distinct:**
  - engine admissibility (the structural CONFIRM of the scenario);
  - issuance (call);
  - modelled entry (PRIMARY path entered) or NO_ENTRY;
  - outcome (path status and exit class).
- **Revisions and updates** (`call_revision`) are counted, never as independent opportunities.
- **Families** A/B/C are reported separately.

## 4. Primary result and accounting conventions

**Primary result, one per period:** the **sum of `price_net` over the PRIMARY paths with status CLOSED** of all A/B/C calls of the period's cohort.
- **Unit.** Normalized one-unit hypothetical paths: N0 = 1 abstract USDT reporting unit, q = 1/E. The sum adds per-path net fractions. It is **not** a return on Owner capital and is not compounded.
- **Costs included.** fees 0.0005 × (1 + X/E) + allowances 0.0002 × (1 + X/E) per path. **PRICE_NET_ONLY:** funding is not covered, `total_net` is unavailable and never zero.
- **NO_ENTRY and "no call" are not successes.** They add no price_net and are counted separately.
- **AMBIGUOUS / CENSORED / UNRESOLVED** PRIMARY paths are **not zero**.
  - If any exist, only the determined subtotal (CLOSED paths) is reported, with each undetermined path and its reason (ambiguity bounds, censoring time, unresolved at the clock end).
  - The result is then marked incomplete.
- **Never aggregated** across the two periods.

**Reconciliation, per period:**
- calls = CLOSED + NO_ENTRY + undetermined;
- the sum = the ordinary report's (`adviser.report7.build`) PRIMARY `sum_price_net` and counts;
- funnel per family: scenarios born → engine-admissible → calls → entered/NO_ENTRY → outcome classes → sum.

## 5. Execution and targeted verification

**Runner.** [`run_v07_economic.py`](run_v07_economic.py), one run per pack. It uses the same construction as the app's adviser-evaluation job (`engine_config` + `new_runtime` with the pinned evaluator + `Kernel` + finish), stops on any identity difference, and generates the report with the app's own `report7.build`. Outputs (journal, records, report, manifest with hashes) are kept outside Git; the manifest and the report are copied here.

**Tabulation.** [`tabulate.py`](tabulate.py) checks:
- output hashes against the manifest;
- v0.7 and evaluator identities, and the implementation on every record;
- costs recomputed from the fills;
- PRIMARY entry at/after ceil-minute(issue + 60 s);
- one PRIMARY path per evaluation-window call and none outside it;
- no tail call;
- the report equals the tabulation;
- **v0.7 calls identical to the v0.6 calls of the same pack** (id, time, family, direction; the v0.6 journals of the earlier offline runs).

**Reproducibility.** The tabulation is rerun on the same outputs; no second engine run. Targeted product tests only: the study registry and v0.7 release tests. No full suite.

**Corrections.** A technical restart of the same run is documented and its trace kept. Any change of convention after outcomes are visible is an explicit amendment that states what was visible. The policy is never modified to improve a balance.
