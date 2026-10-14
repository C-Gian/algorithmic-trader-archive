# A confirmed direction — historical replication [2025-01-01, 2025-05-01): registration before acquisition

**Executor registration, 14 October 2026.** Committed **before** any acquisition, pack preparation, engine run or outcome.
- **Authorization and fixed design:** [A-CONFIRMED-DIRECTION-REPLICATION-AUTHORIZATION.md](../../A-CONFIRMED-DIRECTION-REPLICATION-AUTHORIZATION.md) (Astra, relayed by the Owner, 14 October 2026).
- **Design:** [A-CONFIRMED-DIRECTION-REFERENCE-PROPOSAL.md](../../A-CONFIRMED-DIRECTION-REFERENCE-PROPOSAL.md).
- **Preliminary report:** [A-CONFIRMED-DIRECTION-REPLICATION-PRELIMINARY.md](../../A-CONFIRMED-DIRECTION-REPLICATION-PRELIMINARY.md).

## 0. Known results and exposure

- **Known:**
  - the September–December 2025 results of this comparison (89 pairs, 55 against 47, +4.49 points; warmup −16.67 points);
  - every earlier study on that period.
- **Exposure of [2024-11-27, 2025-05-01 06:05) is not completely documented:**
  - literature (`LIB-007`) to April 2025;
  - no register row, which is not absence;
  - human, model and pre-clean-room knowledge undocumented.
- **No price, bar or outcome** of the replication period has been read by the executor at registration.

## 1. Frozen engine and classifier

- **Method.** v0.6 = `btc.context-action.v0.6` / `mp005.rules.v0.6` / `adviser.core.v6`.
  - Rules SHA-256 `57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66`.
  - Register SHA-256 `98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda`.
  - Checked again on the run's engine identity.
- **Build.** The commit that contains this registration and the registry change (`HEAD` at the run, recorded in the run manifest). The v0.6 engine code is unchanged by it.
- **Classifier.** `delivery/evidence/A-CONFIRMED-DIRECTION-REFERENCE/probe.py`, SHA-256 `ffc9833094347ff8eb910bd6a370859cb15ce6582518a1da58e5f67a092694a0`, byte-identical. It is used through [`replicate.py`](replicate.py), which:
  1. verifies the SHA-256 of `probe.py`'s bytes and stops on any difference;
  2. imports it unchanged;
  3. sets only its population window constant `WINDOW` to the authorized population ("2025-01-01T00:00:00Z", "2025-05-01T00:00:00Z"), instead of the registered September–December one;
  4. calls the unchanged `main_run`.

  `WINDOW` is the population interval, fixed by the authorization, not a classification rule. All geometry, barrier, time and outcome rules are untouched.

  **Consequence of the unchanged labels:**
  - births before 2025-01-01 (the initialization) are tabulated as `warmup`, separately;
  - births at/after 2025-05-01 are labelled `tail`. Probe's registered check "no tail-window birth" reports any confirmed tail birth; such an episode is excluded from both tables and never added to the population.

## 2. Registry change (additive)

- `StudyPreset` gains two optional fields, absent from every existing entry:
  - `study_kind: "HISTORICAL_REPLICATION"`: classification;
  - `offline_only: true`: usage.
- With `study_kind`, `classify()` keeps the label `REGISTERED_STUDY_WINDOW` and adds `study_kind`. Its note is historical, states that exposure is not completely documented, and keeps `certified_uncontaminated = false`.
- With `offline_only`, the backend:
  - omits the preset from `GET /api/corpus/presets`;
  - refuses `POST /api/corpus/presets/{id}/prepare` (409, no job);
  - refuses `POST /api/evaluations` on a pack of that preset (409, no evaluation or replay).
- The offline preparation goes through the ordinary `create_pack_job` and the ordinary corpus worker, which are unchanged.
- **Unchanged:**
  - every existing preset and study: identity, behaviour, classification;
  - the guards: target, month builder, development/protected overlap, field-for-field study equality, the protected-period evaluation gate;
  - no test-only override is used for the real preparation.

**Registered study entry:**
- `study_id` `A-CONFIRMED-DIRECTION-HISTORICAL-REPLICATION-2025`;
- `run_type` `adviser_evaluation` and `method` `v0.6`, the only values the schema admits; the app never runs it (`offline_only`);
- preset `a-confirmed-direction-historical-replication-2025-v1`:
  - warmup [2024-11-27T00:00Z, 2025-01-01T00:00Z);
  - evaluation [2025-01-01T00:00Z, 2025-05-01T00:00Z);
  - tail [2025-05-01T00:00Z, 2025-05-01T06:05Z);
  - `REGISTERED_EXPLICIT_INITIALIZATION`, `evidence_class` `REGISTERED_STUDY_WINDOW`, not default, `automatic_prepare` false;
- sources: the authorization and the design, pinned by `sha256_lf`.

## 3. Acquisition and pack (outside the Owner stack)

**Environment.**
- A disposable local PostgreSQL 18 cluster in the session scratchpad, migrated by `algotrader migrate`.
- `ALGOTRADER_DATA_ROOT` in the scratchpad, outside Git.
- Official OKX REST base URL `https://www.okx.com` (`configured_base_url`, validated).

**Procedure.**
1. `create_pack_job(conn, presets, preset)` for the registered preset.
2. The ordinary `algotrader corpus-worker` until the job is terminal. It plans month children within the 31-day bound and runs the ordinary `OkxPublicClient` + `marketdata.dataset.acquire` with `verify`. It then builds the receipt-pinned source caches, composes the pack feed cache and publishes the pack.
3. **Families**, from the ordinary contract: trade, mark and index 1m, and funding settlements (funding not used economically).

**Interruptions.** A technical resumption of the same job, with verified identity and state, is allowed through the worker's lease reclaim. A full restart after an error is documented, and the earlier trace is kept. No alternative attempt is chosen from outcomes.

## 4. Verification before processing (recorded in §7 before the engine runs)

- **Provenance:** official OKX endpoints and dataset manifests (request window, retrieval times, pages).
- **Effective intervals and completeness per family:** expected and observed minutes, missing minutes.
- **Duplicates and conflicts:** the dataset quality reports and the pack overlap/provenance.
- **Identities and hashes:** pack id, pack manifest SHA-256, cache id, cache manifest SHA-256, feed content identity, event count and dataset ids.

No interpolation, source substitution or silent correction. If gaps prevent the ordinary path or reliably reconstructable states, stop with the precise reason.

## 5. Processing

- [`run_v06_replication.py`](run_v06_replication.py) has the same construction as the earlier `A-REACTION-EFFICIENCY-EXPLORATION/run_v06_offline.py`:
  - `temporal_config` + `engine_config(feed manifest, pack manifest, build, "v0.6")`;
  - one `observe.kernel.Kernel` over every canonical line;
  - `Kernel.finish` at the declared clock end;
  - **no evaluator**.
- The pack id and the expected manifest SHA-256 are arguments, checked against §7 before anything is applied.
- **One continuous run:** no monthly reset, no gate bypassed, no parameter changed.
- **Outputs, outside Git:** `journal.jsonl.gz`, `trade_bars.csv.gz`, `progress.log`, `run_manifest.json`. A copy of the manifest goes here.

## 6. Tabulation

- `replicate.py run <run_dir> out/`: the population is the authorized window, initialization births go to `warmup`, both tabulated by unchanged `probe.py`.
- Reproducibility: a second tabulation on the same run outputs, without a second engine run, must give identical hashes.
- Results are kept separate from September–December 2025.

## 7. Input identities (added after acquisition, before processing)

Acquired and prepared 2026-10-14 10:58 → 11:37Z by the ordinary job `pack-job-20261014T105836-68903c` (corpus worker, disposable DB `replica2025`, data root in the session scratchpad, base URL `https://www.okx.com`). Verified by [`verify_pack_inputs.py`](verify_pack_inputs.py) → [`inputs_verification.json`](inputs_verification.json): **10/10 checks pass**.

**Pack:**
- `pack-ec195b0b4bee44ee5d9c3c564ab8aa9631ed8fd4`, status **READY**;
- manifest SHA-256 `b7f4ddb885a6e60fe5418ded18c141ea33ef2552eca13a60ca2e0094a74c5e7c` (= its trusted receipt);
- preset SHA-256 `d2c8b5bc4deae93898249d3f5e190ad69dccbaa7848e258111d590bf8be6cd30`;
- classification `REGISTERED_STUDY_WINDOW` + `HISTORICAL_REPLICATION`, `certified_uncontaminated` false;
- clock end 2025-05-01T06:05:00Z.

**Feed cache:**
- `fc-200b0433840be874609b2ff2b39f2f4f9b42250b`, manifest SHA-256 `f1b114b3d125f716e5b93bec889c16a45918be1b9c74fef75c35b74474c7e40a`;
- content identity `feedcontent.v1:a0142cae7699d138f488335fe9509d6bfc26abd6b1589317d6cfd62dea6e12b0`;
- 670695 events: trade, mark and index 1m bar observations, 223565 each;
- availability `feed.modeled.v1(bar+PT0S,funding+PT0S)`.

**Coverage.** Trade, mark and index 1m are complete in every window: warmup 50,400, evaluation 172,800, tail 365 slots, with 0 missing and 0 rejected. Overlap: 0 conflicts, 0 identical collapses, 0 overlapping slots. Readiness preview at 2025-01-01: 3,360 contiguous complete 15m bars, 840 1h bars, 61 matched mark/index minutes.

**Funding.** 0 funding rows in every source dataset: the public `funding-rate-history` returned none for this period. The pack carries the ordinary limitation "funding completeness unproven: … PRICE_NET_ONLY". This is the same condition as the September–December reference pack, whose feed also held 0 funding events (679,335 = 3 × 226,445 bar events). Funding feeds no v0.6 professional record and is not used. Nothing was interpolated, substituted or corrected.

**Sources** (OKX public endpoints `/api/v5/market/history-candles`, `history-mark-price-candles`, `history-index-candles`, `/api/v5/public/funding-rate-history`; every dataset passes the ordinary full `verify`, quality clean, no duplicate or conflict finding):

| Dataset | Slice | Retrieval started | Manifest SHA-256 | Quality |
|---|---|---|---|---|
| `okx-btc-usdt-swap-1m-20241127T0000-20241201T0000-f83211857887` | 2024-11-27T00:00:00Z → 2024-12-01T00:00:00Z | 2026-10-14T10:58:43.178749Z | `5574d4e820e81f91ed2b2edd18ef2bad6d87a540d4009f38cb0cf444e590ec1a` | clean |
| `okx-btc-usdt-swap-1m-20241201T0000-20250101T0000-fd3a9c6bdd12` | 2024-12-01T00:00:00Z → 2025-01-01T00:00:00Z | 2026-10-14T10:59:38.080233Z | `0ad10d00ce7416e91178a1fb2514e5e2c29664317e0206ba90dbd8f065bf9b75` | clean |
| `okx-btc-usdt-swap-1m-20250101T0000-20250201T0000-39eda1bd9c38` | 2025-01-01T00:00:00Z → 2025-02-01T00:00:00Z | 2026-10-14T11:06:37.453437Z | `d072d6c17e4792c1dc9bbab0b6cfff37d03026eacd51611356e3bbe30c75fe6d` | clean |
| `okx-btc-usdt-swap-1m-20250201T0000-20250301T0000-0ebb92ecf9f0` | 2025-02-01T00:00:00Z → 2025-03-01T00:00:00Z | 2026-10-14T11:13:27.421296Z | `1856e74fe079844baafe6f429b85945648770911101914d099f2d575225e88a2` | clean |
| `okx-btc-usdt-swap-1m-20250301T0000-20250401T0000-7a389c3cf848` | 2025-03-01T00:00:00Z → 2025-04-01T00:00:00Z | 2026-10-14T11:19:50.723686Z | `2f813ac6537641f8c4c7f997342e18843b23b9c9c952158c6a87cdb8dbeb6ace` | clean |
| `okx-btc-usdt-swap-1m-20250401T0000-20250501T0000-9b10103db3c4` | 2025-04-01T00:00:00Z → 2025-05-01T00:00:00Z | 2026-10-14T11:26:47.041792Z | `95d6e11ad54278732f0ae3f67d2d1a4db56011102081b2821092c83adb21f052` | clean |
| `okx-btc-usdt-swap-1m-20250501T0000-20250501T0605-f1d0904d1396` | 2025-05-01T00:00:00Z → 2025-05-01T06:05:00Z | 2026-10-14T11:33:30.324911Z | `8deb1fb854c5b254d64266f1791a63a468db316a7f0d2a71da5e5ad360089273` | clean |

**Run arguments fixed now:**
- pack `pack-ec195b0b4bee44ee5d9c3c564ab8aa9631ed8fd4`;
- expected manifest SHA-256 `b7f4ddb885a6e60fe5418ded18c141ea33ef2552eca13a60ca2e0094a74c5e7c`;
- build = this commit.
