# Historical study of the complete v0.7 policy — January–April 2025 and September–December 2025 (separate)

**Executor delivery, 14 October 2026.** The Director's review is separate and PENDING.
- **Registration:** committed before any computation at `1326864` ([REGISTRATION.md](REGISTRATION.md)).
- **Runs:** one offline v0.7 adviser evaluation per pack with the ordinary evaluator (build `1326864`), outside the Owner stack. They use the app job's construction and the app's own `report7.build`.
- **Amendments:** two, both to the verification script only (§5).
- **Unit.** Normalized one-unit hypothetical paths, PRICE_NET_ONLY. **Not a return on Owner capital.**
- **Periods** are never aggregated.

## 1. Reconciled path per period and family

Stages are kept distinct: engine admissibility = the structural CONFIRM; issuance = call; modelled entry = PRIMARY entered or NO_ENTRY; outcome = path status and exit class.

| | **January–April 2025** | | | **September–December 2025** | | |
|---|---|---|---|---|---|---|
| | A | B | C | A | B | C |
| Scenarios born in the evaluation window | 376 | 33 | 32 | 359 | 44 | 37 |
| … armed | 167 | 6 | 19 | 161 | 6 | 18 |
| … confirmed (engine-admissible) | 88 | 5 | 16 | 89 | 4 | 12 |
| Calls issued in the evaluation window | **3** | **1** | 0 | **1** | 0 | 0 |
| … call revisions (not opportunities) | 44 | 4 | — | 52 | — | — |
| PRIMARY entered / NO_ENTRY | 2 / 1 | 1 / 0 | — | 1 / 0 | — | — |
| Outcomes (CLOSED) | 1 TARGET, 1 GUIDANCE_TIME_EXPIRED | 1 STOP | — | 1 GUIDANCE_TIME_EXPIRED | — | — |
| AMBIGUOUS / CENSORED / UNRESOLVED | 0 / 0 / 0 | 0 / 0 / 0 | — | 0 / 0 / 0 | — | — |
| Σ price_net of CLOSED PRIMARY paths | +0.0035416 | −0.0025778 | — | +0.0010088 | — | — |

**The calls, in detail:**
- **January–April:**
  - B SHORT 2025-01-08 12:01, entered 12:03, **STOP** at 12:07: **−25.8 bps**.
  - A SHORT 2025-01-23 03:48: **NO_ENTRY** (the call terminated before a qualifying open).
  - A SHORT 2025-02-03 03:31, entered 03:32, guidance time expiry at 07:32: **+4.9 bps**.
  - A LONG 2025-04-15 06:59, entered 07:00, **TARGET** at 07:24: **+30.5 bps**.
- **January–April boundary.** 3 more A SHORT calls (2024-11-28, 12-01, 12-05) were issued during the **initialization**; they are not scored (no path, as registered).
- **September–December:** A LONG 2025-10-26 23:34, entered 23:35, guidance time expiry at 03:35: **+10.1 bps**.
- **Per-call detail:** `<period>/out/calls.csv` (fills, costs, revisions, secondary paths).

## 2. Primary result and coverage

| | January–April 2025 | September–December 2025 |
|---|---|---|
| Calls in the cohort | 4 (A 3, B 1, C 0) | 1 (A 1) |
| CLOSED / NO_ENTRY / undetermined | 3 / 1 / 0 | 1 / 0 / 0 |
| **Primary result: Σ price_net of CLOSED PRIMARY paths** | **+0.000964 (≈ +9.6 bps, summed over 3 paths)** — complete | **+0.001009 (≈ +10.1 bps, 1 path)** — complete |
| Stress sensitivity (5 bps/leg allowance, not primary) | −0.000837 | +0.000408 |
| total_net | unavailable (PRICE_NET_ONLY) | unavailable (PRICE_NET_ONLY) |

**Conventions:**
- **Unit and costs.** N0 = 1 abstract USDT reporting unit per path, q = 1/E. Fees 5 bps/leg and allowances 2 bps/leg are included; costs are recomputed from the fills and verified.
- **Funding** is not covered (`EMPTY_UNKNOWN`), so PRICE_NET_ONLY.
- **NO_ENTRY and "no call"** are not counted as success.
- **No undetermined path** in either period, so both results are complete.
- **The official report** (`report.json`/`report.md` per period) gives the same PRIMARY sums and counts.

## 3. Limits

**Modelled execution:**
- historical modelled availability, entry at the first qualifying minute open 60 s after issue, exits per the evaluator's collision rules;
- no measured quotes, no slippage beyond the fixed allowance, no funding;
- one-unit paths, not sizing.

**Sample:**
- **5 scored calls in two periods** (4 + 1); 3 more calls fell in the January–April initialization;
- B and C almost absent (1 B call, 0 C);
- one call drives each sign;
- the result is extremely sensitive to single paths and to the cost assumption: the stress allowance flips January–April negative.

**Exposure:**
- September–December 2025 is exposed development data, with earlier results known;
- January–April 2025 exposure is **not completely documented**;
- the v0.6 call lists of both packs were seen (metadata) before registration;
- this is not out-of-sample evidence.

**Same calls as v0.6** (checked). The economic result is therefore a property of the v0.6 entry policy as much as of v0.7.

## 4. Problems and recommendation

**Technical problems (precise):** none in the engine runs. The two verification-script defects in §5 were fixed before any conclusion.

**Methodological observation (not a technical fault, not changed):**
- The complete policy issues very few calls: 4 in four months and 1 in four months.
- The confirmation → entry analysis (`A-CONFIRMATION-OPPORTUNITY-PATHS`) attributes this to the reward/risk, cost and corridor constraints at the confirmation or return price.

**Recommendation on candidate v0.7: inconclusive on economic grounds.**
- Both periods show a small positive determined sum, but on 3 and 1 scored paths. One January–April path is a stop, and the stress sensitivity changes the January–April sign.
- This can neither support nor reject economic usefulness. It does not justify promotion on economic grounds, and no tuning or policy change is suggested here.
- v0.7's technical behaviour on these packs is as documented: identical calls to v0.6, and only explanation and MarketView differences.
- Further evidence would need more opportunities: the Director's choice of method or period, not an adaptation of this study.

## 5. Checks, reproducibility, amendments

**Checks: 10/10 per period** (`<period>/out/results.json`):
- output hashes = run manifest;
- frozen v0.7 identity and registered evaluator, `adviser.core.v7` on every record;
- costs recomputed from the fills;
- PRIMARY entry at/after ceil(issue + 60 s), 60 s profile;
- one PRIMARY path per evaluation-window call and none outside it;
- no tail call;
- the report equals the tabulation;
- calls = closed + no entry + undetermined;
- v0.7 calls identical to the v0.6 calls of the same pack.

**Reproducibility.** The tabulation ran twice per period on the same outputs, with identical hashes:
- January–April: `results.json` `b7292efd…86b6`, `calls.csv` `9074b2e1…0a45`;
- September–December: `results.json` `4dc147b0…ea93`, `calls.csv` `ab916a1d…2b2b`.

**Runs.** Engine outputs are kept outside Git; hashes are in each `run_manifest.json`.
- January–April: 670,695 events, 33,910 journal entries, 2,896 evaluation records, 366 s.
- September–December: 679,335 events, 34,475 journal entries, 2,932 evaluation records, 351 s.

**Targeted product tests:** `test_historical_replication_study` + `test_v07_release`, 34 passed. No full suite.

**Amendments, made with the results visible (tabulation checks only; no engine run, convention or result changed):**
1. **Report section path.** The check read the report's PRIMARY section at `outcomes.PRIMARY`; the report stores it at `outcomes.variants.PRIMARY`. The corrected check passes: paths, no entry and sum are equal.
2. **Call parity key.** Scenario and call ids embed the method's rules hash (`core3`: `sid = …_h(rules_sha256, …)`), so v0.6 and v0.7 ids differ by construction. The parity key became method-independent: issue time, family, direction, origin impulse, target, invalidation, structural area and hard deadline. The corrected check passes.

No pull/fetch. No CI was queried; CI is PENDING / NOT CHECKED.
