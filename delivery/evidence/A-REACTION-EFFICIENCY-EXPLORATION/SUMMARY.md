# A reaction directional efficiency: descriptive exploration of E, September–December 2025

**Executor delivery, 12 October 2026, base `6a0f22a`. The Director's review is PENDING.**
- **Data.** This is an exploration on **already exposed development data**. It is not a test.
- **Excluded.** No significance test, confidence interval or economic result.
- **Unchanged.** Product, v0.6 and HDP-001 frozen. The two future studies stay INACTIVE.

**Order of work.**
1. **Inputs verified.** The copied inputs passed 21/21 checks ([`inputs_verification.json`](inputs_verification.json)).
2. **Conventions registered** in [`REGISTRATION.md`](REGISTRATION.md), committed at `24b701c` **before** the v0.6 processing existed. There were no amendments.
3. **Single offline processing.** [`run_v06_offline.py`](run_v06_offline.py) → [`run_manifest.json`](run_manifest.json).
4. **Tabulation.** [`explore_e.py`](explore_e.py) → [`results.json`](results.json), [`episodes.csv`](episodes.csv) and [`strata.csv`](strata.csv).

## 1. Inputs and processing

**Inputs.**
- Pack `pack-1ae7d36c…`, manifest sha256 `1bec1f15…1f92` (= the registered hash).
- Feed cache `fc-80221b24…`.
- Copied read-only from the Owner volume under Astra's derogation. Kept outside Git.
- Coverage:
  - initialization [2025-07-28, 2025-09-01);
  - evaluation [2025-09-01, 2026-01-01);
  - authorized tail to 2026-01-01T06:05Z;
  - trade, mark and index complete, 0 missing.

**Prior consultation.** Before the derogation, the manifest metadata was read via `docker exec` ([REGISTRATION §1](REGISTRATION.md)).

**Processing.**
- Engine: v0.6 frozen (rules `57bf2309…`, register `98ef101e…`, equal to the frozen references), build `6a0f22a`.
- Path: the worker's construction, offline, with no DB and **no evaluator**. One continuous run with the pack's initialization and tail.
- Size and time: 679,335 events applied, finish at 06:05Z, 352 s.
- Journal: 34,507 entries:
  - 2,003 scenario;
  - 8,193 market_view;
  - 1 call;
  - 1,002 entry_attempt;
  - 15,231 landmark;
  - 8,014 observation;
  - 52 call_revision;
  - 11 material_change.
- Integrity: the final input commitment equals the verification's (`afad3a52…`). 0 trade gaps.
- No existing v0.6 record was reused, because none exists locally.

## 2. Population flow

| Step | Count |
|---|---|
| A owners born in [2025-09-01, 2026-01-01) | **359** (LONG 187, SHORT 172) |
| Never reached ARM | **198** |
|   EXPIRED `SPENT_HIGH_BEYOND_B_BEFORE_REACTION` | 188 |
|   WITHDRAWN context/adverse expansion (BALANCED/TRANSITION 6, BALANCED/ROTATION 2, BALANCED/EXPANSION DOWN 1) | 9 |
|   WITHDRAWN `CLOSE_AT_OR_BEYOND_A_PLUS_ZONE` | 1 |
| First ARM (one observation each) | **161** (LONG 89, SHORT 72) |
| Source window incomplete | 0 |
| E status at the cutoff | VALUE 161; UNDEFINED / INSUFFICIENT / INCOMPLETE 0 |
| Outcome | B_BEFORE_PREMISE_FAILURE 68 · HORIZON_OBSERVED_NO_B 74 · PREMISE_FAILURE_BEFORE_B 19 · AMBIGUOUS 0 · INCOMPLETE_CENSORED 0 |
| Excluded after E (outcome without Y) | 0 |
| **Eligible** (E VALUE, Y defined) | **161** (Y = 1: 68; Y = 0: 93) |

- **Window extent.** Births run from 2025-09-01T02:30Z to 2025-12-31T20:45Z. The last horizon is 2025-12-31T22:45Z, inside the authorized tail.
- **Annotations.** One owner has an engine call (2025-10-26); its class is HORIZON_OBSERVED_NO_B. Annotations are never used as outcomes.

**Reconciliation, all true:**
- born = never armed + armed;
- armed = observed;
- observed = Σ E statuses;
- E VALUE = eligible + excluded;
- eligible = Σ stratum sizes = contributing + without comparison;
- pairs = C + D + T.

## 3. Strata and comparisons

**Strata.**
- 161 eligible episodes fall into **141 strata**:
  - **123 singletons** (no comparison possible);
  - **18 strata with ≥ 2 episodes**, which hold 38 episodes.
- Of those 18, **10 have no Y variation**, so all their pairs are ties.
- No stratum lacks E variation, and no pair is tied in E (0 excluded; E kept exact).

**Episodes.** **38 episodes contribute** to at least one usable pair (Y = 1: 16, Y = 0: 22). **123 have no usable comparison.**

**Age and phase.** Ages at the cutoff are 1 bar for 138 of the 161 episodes. The 2–5-bar ages are spread thinly and none of them is in a multi-episode stratum. Phases are TRANSITION 57, REACTION 45, EXPANSION 45 and COMPRESSION 14.

The 18 multi-episode strata: key (age, phase, class dB, class dP), size, Y = 1 / Y = 0, C/D/T and weight in the denominator.

| Stratum | n | Y1/Y0 | C | D | T | Weight |
|---|---|---|---|---|---|---|
| 1, TRANSITION, 3, 8 | 4 | 1/3 | 1 | 2 | 3 | 0.2609 |
| 1, COMPRESSION, 4, 4 | 2 | 1/1 | 0 | 1 | 0 | 0.0435 |
| 1, COMPRESSION, 4, 5 | 2 | 0/2 | 0 | 0 | 1 | 0.0435 |
| 1, COMPRESSION, 5, 6 | 2 | 1/1 | 1 | 0 | 0 | 0.0435 |
| 1, EXPANSION, 1, 10 | 2 | 2/0 | 0 | 0 | 1 | 0.0435 |
| 1, EXPANSION, 2, 9 | 2 | 2/0 | 0 | 0 | 1 | 0.0435 |
| 1, EXPANSION, 2, 12 | 2 | 0/2 | 0 | 0 | 1 | 0.0435 |
| 1, EXPANSION, 2, 13 | 2 | 1/1 | 1 | 0 | 0 | 0.0435 |
| 1, EXPANSION, 3, 8 | 2 | 0/2 | 0 | 0 | 1 | 0.0435 |
| 1, EXPANSION, 6, 12 | 2 | 1/1 | 1 | 0 | 0 | 0.0435 |
| 1, REACTION, 5, 5 | 2 | 1/1 | 0 | 1 | 0 | 0.0435 |
| 1, REACTION, 7, 3 | 2 | 2/0 | 0 | 0 | 1 | 0.0435 |
| 1, REACTION, 11, 7 | 2 | 0/2 | 0 | 0 | 1 | 0.0435 |
| 1, TRANSITION, 1, 9 | 2 | 1/1 | 1 | 0 | 0 | 0.0435 |
| 1, TRANSITION, 3, 7 | 2 | 2/0 | 0 | 0 | 1 | 0.0435 |
| 1, TRANSITION, 4, 8 | 2 | 1/1 | 0 | 1 | 0 | 0.0435 |
| 1, TRANSITION, 4, 10 | 2 | 0/2 | 0 | 0 | 1 | 0.0435 |
| 1, TRANSITION, 5, 10 | 2 | 0/2 | 0 | 0 | 1 | 0.0435 |
| **Total** | 38 | 16/22 | **5** | **5** | **13** | 23 pairs |

All 161 rows are in [`strata.csv`](strata.csv). Each pair, with both episodes' times, E and Y, is in `results.json` → `pairs`.

## 4. Concentration and overlap (before the main value)

**Pairs are not independent observations.** There are only 10 pairs with different Y (5 C, 5 D), from the 8 strata with Y variation. The other 13 pairs are Y ties.

**Concentration.**
- **One stratum** (1, TRANSITION, 3, 8: four SHORT episodes, 5–26 October and 17 November) holds 6 of the 23 pairs (26%), including 1 C and 2 D. The top 5 strata hold 43.5% of the pairs.
- Four episodes, all SHORT, take part in 3 pairs each. Every other contributing episode is in one pair.

**Time.**
- Contributing episodes by birth month: Sep 10, Oct 10, Nov 9, Dec 9. Eligible episodes: Sep 37, Oct 42, Nov 39, Dec 43.
- By ISO week: 1–5 per week across W36–W52; none in W42 or W45.
- Most pairs join episodes from different months: 16 of 23. Same-month pairs: Sep 1, Oct 3, Nov 2, Dec 1.

**Overlap.**
- **No pair joins episodes with overlapping observation windows** [birth, H).
- 8 of the 161 eligible episodes overlap another eligible episode in time. None of those overlaps is a pair.
- Pairs by side: LL C 2 / T 3; LS C 2 / D 3 / T 5; SS C 1 / D 2 / T 5.

## 5. Main value

**d(Y|E) = (ΣC − ΣD)/(ΣC + ΣD + ΣT) = (5 − 5)/(5 + 5 + 13) = 0/23 = 0** (exact).

With the standard sign, d < 0 would mean higher E goes with less B before the premise failure. Here the concordant and discordant pairs balance exactly, so no ordinal association appears within strata. No other summary is computed.

## 6. Conclusion (one category, motivated)

**Comparison scarce or concentrated.**
- **Scarce.** 123 of the 161 eligible episodes have no comparable episode under the registered key. Only 38 contribute, and the whole value rests on **10 pairs with differing Y** (5 C, 5 D).
- **Concentrated.** One stratum supplies 26% of the denominator.

Within this scarce comparison the relation is **not observed** (d = 0: C = D). That statement describes these 23 pairs only. It is neither evidence of the absence of a relation nor support for the hypothesis.

No sufficiency threshold is applied. The design, the key and the classes are not changed after the result.

## 7. Declared limits

- **R uncontrolled.** E uses closes. The reaction depth R/I is not in the key and may differ within a stratum. Per-episode `R_depth_I_descriptive` is in `episodes.csv`, reported only.
- **Approximate geometry.** The 0.25·S15 classes make dB and dP comparable within a quarter of S15 each, not identical. I/S15 and the retracement vary within a stratum.
- **Dependence.**
  - Episodes share one market path and one engine state, and the same owner latch governs successive births.
  - Pairs reuse episodes (four episodes in 3 pairs each).
  - Overlapping observation windows exist in the population (8 episodes), although not within pairs.
- **Prior exposure.** September–December 2025 is exposed development data, documented in the exposure register (rows 1–7 and 9):
  - the v0.4 and v0.5 continuous runs over the same pack and their diagnoses;
  - the MarketView/HDP-001 tabulations;
  - the method lineage up to v0.6, developed on them.

  This exploration therefore cannot be independent evidence.
- **Input labelling.** The pack's input-requirement label remains `btc.context-action.v0.2`, as for every pack. The method run is the pinned v0.6.
- **Approximation in the pack.** The instrument definition is a retrieval-time snapshot. Funding completeness is unproven, which is irrelevant here because there are no economic outcomes.
- **Scope.** This is descriptive only, with no predictive, economic or method-validation claim.

## 8. Checks actually run

**Inputs.** 21/21 (§1).
- The processing's final input commitment equals the verification's.
- The journal file hashes are in `run_manifest.json`.

**Self-test before registration.** `explore_e.py --selftest`: 65/65.

**Per owner (161 armed), 0 failures each:**
- Aq and Bq match the BIRTH record;
- the source window is complete;
- the first ARM equals `destination_monitoring_from`;
- the horizon equals `original_expiry`;
- only BIRTH precedes the cutoff;
- the age equals the ARM `bars_seen`;
- every E bar is causal (start ≥ origin, end ≤ cutoff, known_at ≤ cutoff);
- no bar crosses the origin.

**Population-level:**
- one BIRTH and one observation per owner;
- every origin lies on the 15m grid and matches the scenario id;
- every horizon lies within the authorized tail;
- the reconciliation is all true.

**Reproducibility.** A second tabulation run gives byte-identical `results.json`, `episodes.csv` and `strata.csv`.

**Not run.**
- No product suite: no product code changed.
- No lint: ruff is not installed.
- CI not queried.

## 9. Artifacts

| File | Content |
|---|---|
| `REGISTRATION.md` | Conventions, identities and hashes before outcomes (`24b701c`) |
| `verify_inputs.py`, `inputs_verification.json` | Verification of the copied inputs, with provenance |
| `run_v06_offline.py`, `run_manifest.json` | The single processing: identities, counts, hashes of the journal and bars kept outside Git |
| `explore_e.py` | Population, E, key, outcome, Somers' D, concentration; `--selftest` |
| `results.json` | Flow, strata, pairs, concentration, checks, every owner with lifecycle annotations |
| `episodes.csv`, `strata.csv` | One row per owner, one row per stratum |

**Outside Git** (session scratchpad): the copied inputs, `journal.jsonl.gz` (sha256 `ea3ce997…f0f0`), `trade_bars.csv.gz` (`06a11024…abe`) and `progress.log`.


## Subsequent closure annotation — 12 October 2026

The orchestrator accepted closure of the descriptive E exploration delivered at `d2729e1`, on the Director's review. This annotation supersedes the pending-review status above; the original registration and executor delivery remain preserved.

The Director independently recalculated the comparison from `episodes.csv`: 359 owners, 161 armed, 141 strata, 123 singletons, 38 contributing episodes; C = 5, D = 5, T = 13 and d(Y|E) = 0/23. Input integrity and the full engine processing remain executor verifications. The orchestrator read SUMMARY and REGISTRATION, without independently rerunning scripts or the CSV comparison.

The accepted conclusion is a scarce and concentrated comparison, with zero aggregate association. Opposite-signed stratum contributions cancel; this does not establish absence of association in every stratum or irrelevance of reaction character generally.

**Decision: this E branch stops here. E is not promoted to an operational criterion; A remains unchanged.** No weight, filter, class widening, new cutoff, other curve summary or further period is authorized. Definitions, tools and results are retained as acquired knowledge. No new activity is activated. v0.6 and HDP-001 remain frozen; the two future studies remain INACTIVE. CI was not queried.


## Later annotation — branch closed (14 October 2026)

The text above is the original delivery, unchanged. Astra's instruction relayed by the Owner on 14 October 2026 (assignment "A confirmations → entry opportunities") states that the E exploration, the a2x branch and the confirmed-direction comparison are **closed**. No further execution, adaptation or follow-up study is authorized from this branch; v0.6 stays unchanged and future studies stay INACTIVE.
