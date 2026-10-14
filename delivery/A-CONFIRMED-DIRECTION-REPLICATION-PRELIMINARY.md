# A confirmed direction — replication on Jan–Apr 2025: preliminary exposure and availability report

**Executor report, 14 October 2026.** Astra authorized one replication of the A directional comparison on scenarios born in **[2025-01-01, 2025-05-01)**, relayed by the Owner. This preliminary step covers only documented exposures and artifact availability.

**Nothing was consulted beyond documents and metadata:**
- no price, outcome or bar content;
- no Owner stack or DB access;
- no acquisition, extraction or engine run.

The window is not changed. The comparison to keep is frozen v0.6 with `probe.py` as registered at `6f3ac03` and delivered at `cd579d5` (SHA-256 `ffc98330…94a0`), unchanged.

## 1. Documented exposures and gaps for 2025-01-01 → 2025-05-01 (plus initialization and tail)

**Attested exposure.**
- **Literature, not BTC prices.** `source_notes/LIB-007` (Man AHL, June 2025) reports trend-following (SG Trend Index) results to **30 April 2025**, with distributions January 2000–April 2025. It describes 2025 as a difficult period for trend following. This is a general multi-asset exposure, without BTC levels.
- **No row of the [exposure register](STUDY-EXPOSURE-REGISTER.md)** concerns this period. Rows 1–17 cover July 2025 → January 2026, September 2025 (RP-001), October 2026 live use, and the future study windows.

**Attested absence: none.** No document certifies that the period was not examined. The missing register row is **not** an absence: the register states that unknown is never "no exposure".

**Insufficient information:**
- **Pre-clean-room exposure:** not documented (register, Known gaps).
- **Owner, Director and Astra:** their knowledge of the BTC market in early 2025, public or personal, is not documented.
- **The executor:** a language model whose general training knowledge may include the public BTC market of early 2025. This cannot be documented or measured.
- **Owner stack market-data volume:** never inventoried. The only Owner metadata in hand is the read-only DB snapshot of 14 October, taken during the v0.7 update: 5 packs, each referenced by an evaluation whose preset covers 2025-07-28 → 2026-01-01. No dataset listing was taken, and none is taken now.

## 2. Inputs present locally (outside the Owner stack): identity and coverage

| Artifact | Coverage | Relevant to the window? |
|---|---|---|
| Pack `pack-1ae7d36c…` + feed cache `fc-80221b24…` (copy of 12 October) | 2025-07-28 → 2026-01-01 06:05 | No |
| v0.6 offline journals and admitted trade bars (12 and 13 October runs) | 2025-07-28 → 2026-01-01 06:05 | No |
| Exported feed caches `fc-fa83…`, `fc-de5a…`, `fc-83bb…`, `fc-29ae…` | 2025-08-28 → 2026-01-01 (monthly packs) | No |
| Small OKX datasets (UI/smoke fixtures) | 2026-09-25 → 2026-09-30 | No |

**Benchmark datasets labelled 2026-06 and 2026-08.** Two exist (`var/benchmarks/r1c`, bench scratchpads), labelled OKX 2026-06-01 → 07-01 and 2026-08-03 → 08-10, inside the protected period. The README labels the R1C benchmarks *synthetic*. They were not opened. This is a note for the protected-period inventory, not an input.

**No local artifact covers any part of 2024-11-27 → 2025-05-01 06:05.**

**Registered corpus.** The checked-in corpus plan and presets cover only the target 2025-09-01 → 2026-09-01 (development 2025-09 → 2026-01). No preset or plan chunk exists for 2024–early 2025.

## 3. Exact intervals required (derived from existing rules; UTC, half-open, whole minutes)

| Part | Interval | Rule |
|---|---|---|
| Initialization (not evaluated) | **[2024-11-27T00:00Z, 2025-01-01T00:00Z)**, 35 days, 840 h | Registered explicit initialization of 35 days before the window start: the reference run's preset `…-init35d-v1`, and the A v0.6 study references (`[2026-12-21, 2027-01-25)`, "35 days") |
| Evaluation (births by BIRTH publication time) | **[2025-01-01T00:00Z, 2025-05-01T00:00Z)** | Astra's window, unchanged |
| Tail | **[2025-05-01T00:00Z, 2025-05-01T06:05Z)**, 365 min | `outcome_tail_minutes` 365 (presets; MP-005 register) |
| Whole pack request | **[2024-11-27T00:00Z, 2025-05-01T06:05Z)** | Families: trade 1m, mark 1m, index 1m and funding settlements, OKX BTC-USDT-SWAP (the reference pack's coverage) |

**Probe coverage inside the tail.**
- The last possible birth publication is 2025-04-30T23:45Z.
- The A setup lifetime is 120 min (v0.6 register), so any confirmation comes before 2025-05-01T01:45Z.
- Every 4 h horizon therefore ends by **05:45Z**, inside 06:05Z.

**Note.** WP-013 explained its 28 July start also as a Monday. 2024-11-27 is a Wednesday. The 35-day length still contains the complete previous month, the previous week, the previous day and the 168 h pivot memory. Whether the Monday property must be reproduced, for example 2024-11-25, is left to the Director. It is not changed here.

## 4. Missing need (only what is missing)

1. **Data acquisition.** Public OKX BTC-USDT-SWAP trade, mark and index 1m bars and funding settlements for [2024-11-27T00:00Z, 2025-05-01T06:05Z).
   - Nothing is local.
   - Whether the Owner stack holds it is not inventoried.
   - Source availability and completeness for that period are unverified.
2. **Pack preparation for that window.** No registered preset exists. Preparing it needs either a registered preset (a configuration change and a Director decision) or another authorized pack path. A read-only copy of the finished pack and feed cache must then be made outside the Owner stack. An **Owner copy** suffices instead if the Owner already holds such a pack.
3. **v0.6 offline processing** of that pack, as in the E exploration (`run_v06_offline.py`): one continuous run with the 35-day initialization, producing the journal and admitted trade bars with a run manifest and identities.

Then `probe.py` runs unchanged after its registration. The registration of identities and conventions was **not** prepared, because the inputs do not exist yet.

No product suite, CI query, pull/fetch or methodological change. January–August 2026 stays protected; future studies stay INACTIVE.
