# A confirmed direction — historical replication on [2025-01-01, 2025-05-01) (v0.6, offline)

**Executor delivery, 14 October 2026.** The Director's review is separate and PENDING.
- **Authorization:** [A-CONFIRMED-DIRECTION-REPLICATION-AUTHORIZATION.md](../../A-CONFIRMED-DIRECTION-REPLICATION-AUTHORIZATION.md).
- **Registration:**
  - registration and registry change committed at `1a11154`, before acquisition;
  - input identities committed at `363fb74`, before the engine ([REGISTRATION.md](REGISTRATION.md)).
- No amendment.
- **Nature.** One standardized directional price probe on a replication period whose exposure is **not completely documented**. It is not a scenario success rate, profit, method or v0.7 evaluation.
- **Separate.** Kept apart from September–December 2025, with no pooled aggregate.

## 1. Coverage and identities

**Pack** `pack-ec195b0b4bee44ee5d9c3c564ab8aa9631ed8fd4` (**READY**, manifest `b7f4ddb8…5e7c`):
- prepared offline by the ordinary pack job and corpus worker on a disposable database;
- data from public OKX endpoints, retrieved 2026-10-14 10:58–11:37Z.

**Windows:** initialization [2024-11-27, 2025-01-01), population [2025-01-01, 2025-05-01), tail to 2025-05-01T06:05Z.

**Bars and checks:**
- trade, mark and index 1m complete in every window: 223,565 minutes each, **0 missing, 0 rejected, 0 conflicts**;
- 7 source datasets, all passing the ordinary verification, quality clean;
- `verify_pack_inputs.py`: **10/10**.

**Funding:** 0 rows, as in the September–December pack; not used.

**Run.** One continuous offline v0.6 run without evaluator. Frozen identity `adviser.core.v6`, rules `57bf2309…`, register `98ef101e…`, build `363fb74`:
- 670,695 events applied in 337 s;
- 33,934 journal entries, last chain `80587898…6dd9`;
- 223,565 admitted trade bars, 0 gaps.
- Manifest: [run_manifest.json](run_manifest.json). Journal SHA-256 `4ea53077…ee65`, bars `4ebd6299…9f3c`, kept outside Git.

**Classifier.** `probe.py` byte-identical (`ffc98330…94a0`, checked at load), run through [`replicate.py`](replicate.py) with only its population window set.

## 2. Population (reconciled)

| | Population [2025-01-01, 2025-05-01) | Initialization births (separate) |
|---|---|---|
| A scenarios born | **376** | 99 |
| … never confirmed | 288 | 71 |
| … **first confirmations** (one per scenario) | **88** (53 LONG, 35 SHORT): 28 on the original anchor, 60 on a later one | 28 |
| Not evaluable / invalid geometry | 0 / 0 | 0 / 0 |
| **Valid geometry** | **88** | 28 |

No birth in the tail; probe check "no tail-window birth" passes.

## 3. Outcomes per orientation and the paired table

| | Selected A (B/V) | Opposite O (mirrored) | *Init. A* | *Init. O* |
|---|---|---|---|---|
| Favourable first (Y = 1) | 53 | 51 | 18 | 17 |
| Adverse first (Y = 0) | 33 | 36 | 10 | 9 |
| Horizon without favourable (Y = 0, own category) | 2 | 1 | 0 | 2 |
| Undetermined | 0 | 0 | 0 | 0 |

**Pairs:** 88 determined, **0 unresolved**. No ambiguity, straddle, missing interval or data end. Bounds therefore equal the determined value.

**Paired 2×2** (population):

| | Y_O = 1 | Y_O = 0 | Total |
|---|---|---|---|
| **Y_A = 1** | 21 | 32 | 53 |
| **Y_A = 0** | 30 | 5 | 35 |
| **Total** | 51 | 37 | 88 |

- (0,0) = 3 adverse/adverse, 1 A horizon with O adverse, 1 horizon/horizon.
- *Initialization births:* (1,1) 10, (1,0) 8, (0,1) 7, (0,0) 3.

**Primary result:**
- selected favourable-first: **53**;
- opposite favourable-first: **51**;
- reference total **52** (mean reference 13/22 = 59.09%);
- **mean difference (Y_A − Y_O)/2 = 1/88 = +1.14 percentage points.** These are 32 against 30 discordant pairs.

*Initialization births, separate:* 28 pairs, 18 against 17, mean difference 1/56 = **+1.79 points**.

*For reference only, not pooled:* September–December 2025 gave 89 pairs, 55 against 47, +4.49 points (warmup −16.67).

## 4. Overlap, concentration and limits

**Overlap.**
- 13 of 88 probe windows overlap another: 12 overlap one other, 1 overlaps two.
- None overlaps an opposite-direction window.
- That gives 81 clusters: 75 single, 5 pairs, 1 of three.

**Concentration.**
- Cutoffs by month: January 22, February 15, March 26, April 25.
- They fall on 60 days, at most 5 per day; 7 days have 3 or more.

**Native terminal markers** of the selected orientation (descriptive): favourable = 52 DESTINATION_REACHED + 1 STALLED; adverse = 32 INVALIDATED + 1 STALLED; horizon = 2 TIME_EXPIRED. As in September–December, Y_A largely re-expresses the native terminal. The opposite orientation is the only new element.

**Limits:**
- the reference includes A and A's moments; it is not independent and does not evaluate the choice of moments;
- the observations are dependent;
- no significance test, subgroup, alternative horizon, tuning or pooled aggregate;
- exposure of the period is not completely documented ([preliminary report](../../A-CONFIRMED-DIRECTION-REPLICATION-PRELIMINARY.md));
- the instrument definition is a retrieval-time snapshot assumed for the whole window, a pack limitation also present in September–December;
- funding is absent in the source data.

## 5. Backend block (offline-only historical entry)

**Synthetic DB tests,** `tests/test_historical_replication_study.py`:
- historical classification, with the existing study and every preset unchanged (pinned `preset_sha256`);
- exact window, initialization, tail and protections;
- ordinary offline preparation admitted;
- preset absent from the Workbench list;
- direct preparation, evaluation (all run types) and Replay Lab starts refused with 409 and no row;
- an ordinary study still listed and preparable.

They pass, as do `test_a_v06_study.py` and `test_a_v06_study_db.py`.

**One pre-existing flake:** `test_a_registered_study_window_may_not_overlap_development_or_protected` fails intermittently on Windows on the **original** code too, 12 of 25 runs. Its cause is `lru_cache` keyed by `st_mtime` with a same-tick rewrite. Reported, not changed.

**On the real pack** ([backend_block_proof.json](backend_block_proof.json)):
- the preset is not listed;
- `POST /api/corpus/presets/{id}/prepare`, `POST /api/evaluations` (adviser v0.6 and observation-only) and `POST /api/observations` (pack) all return **409**;
- row counts are unchanged: 1 offline job, 0 evaluations, 0 replays.

## 6. Reproducibility

The tabulation ran twice on the same run outputs, without a second engine run, with identical hashes:
- `results.json` `d282a536…abdb`;
- `episodes.csv` `bf7d1c54…1d8c`.

Checks 7/7 and reconciliations 5/5 per window, in [`out/results.json`](out/results.json). Per-episode detail: [`out/episodes.csv`](out/episodes.csv).

**Not run:** full product suites and CI (Owner-operated: PENDING / NOT CHECKED). No Owner access or installation, economic evaluation or protected 2026 data.
