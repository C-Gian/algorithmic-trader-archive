# A confirmed direction — historical replication on [2025-01-01, 2025-05-01): authorization and fixed design

**Recorded by the executor, 14 October 2026, from Astra's authorization relayed by the Owner.** This is a stable source text, pinned by SHA-256 in `src/algotrader/corpus/study_presets.json`. Later execution facts (input hashes, results) go to `delivery/evidence/A-CONFIRMED-DIRECTION-REPLICATION-2025/`, never here.

## Authorization

- One replication of the A directional comparison: [design](A-CONFIRMED-DIRECTION-REFERENCE-PROPOSAL.md); Sep–Dec 2025 tabulation registered at `6f3ac03` and delivered at `cd579d5`. It runs on scenarios born in **[2025-01-01, 2025-05-01)**.
- **Authorized steps:**
  - acquisition of public OKX data;
  - pack preparation **outside the Owner stack**;
  - **one** continuous offline v0.6 processing **without evaluator**;
  - then `probe.py` unchanged.
- **Additive registry change.** One registered study entry `study_kind = HISTORICAL_REPLICATION` (classification) with `offline_only = true` (usage):
  - ordinary preparation is allowed on the offline path;
  - the preset is excluded from the Workbench selections;
  - the Workbench preparation route and the start of any app evaluation on it are refused by the backend, even on direct request and even if a pack was already prepared offline.
- **Not authorized:**
  - Owner access or installation;
  - economic evaluation, tuning, method change;
  - any 2026 protected data;
  - pull/fetch, CI queries, full product suites.

## Fixed intervals (UTC, half-open, whole minutes)

| Part | Interval |
|---|---|
| Initialization (not evaluated) | [2024-11-27T00:00Z, 2025-01-01T00:00Z), 35 days; no Monday extension |
| Population (A births by BIRTH publication) | [2025-01-01T00:00Z, 2025-05-01T00:00Z) |
| Tail | [2025-05-01T00:00Z, 2025-05-01T06:05Z), 365 min |

- The tail adds no birth to the population and does not lengthen the four-hour horizon.
- **Data:** OKX BTC-USDT-SWAP trade 1m, mark 1m, the associated index 1m, and funding settlements. Funding is included only because the ordinary dataset contract requires it (`HISTORICAL_FAMILIES`); there is no economic use.

## Comparison kept unchanged

- **Method.** Frozen v0.6: `btc.context-action.v0.6`, `mp005.rules.v0.6`, `adviser.core.v6`, rules `57bf2309…2e66`, register `98ef101e…5bda`.
- **Classifier.** `probe.py`, byte-identical to its registration at `6f3ac03`: SHA-256 `ffc9833094347ff8eb910bd6a370859cb15ce6582518a1da58e5f67a092694a0`. It keeps:
  - the first confirmation per scenario, revised anchors included;
  - the cutoff price available at publication;
  - mirrored barriers;
  - four hours;
  - ambiguity and incompleteness undetermined;
  - the difference on determined pairs and the overall bounds when needed.
- **Separation.** Results are reported separately from September–December 2025, with no aggregate chosen after the result, no subgroup, no alternative horizon and no tuning.
- **Already known.** Earlier results on September–December 2025 are known.
- **Exposure.** Exposure of the replication period is **not completely documented** ([preliminary report](A-CONFIRMED-DIRECTION-REPLICATION-PRELIMINARY.md)).
