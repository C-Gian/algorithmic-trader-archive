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

*To be completed and committed before the engine runs.*
