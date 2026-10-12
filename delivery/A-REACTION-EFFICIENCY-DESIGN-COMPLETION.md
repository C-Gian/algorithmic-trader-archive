# A reaction directional efficiency: design completion (synthetic feasibility)

**Executor delivery, 12 October 2026, base `16d03a6`. Director review PENDING.** One synthetic step, separate from the product. No change to engine, method, API, persistence or UI. No Owner extraction, acquisition, backtest, economic result, protected period or CI query. **No real exploration is authorized.** v0.6 and HDP-001 frozen; studies INACTIVE.

**Supersession.** This note, with the authoritative rectification relayed on 12 October 2026, replaces §2 (candidate) and §4 (comparison) of [A-REACTION-CHARACTER-DESIGN.md](A-REACTION-CHARACTER-DESIGN.md) wherever they differ. That design is kept byte-identical as history (sha256 `0fa9f69e…e599`, received as `A_REACTION_CHARACTER_DESIGN.md`). Its §1, §3 and §5 remain history only.

Evidence: [`feasibility.py`](evidence/A-REACTION-EFFICIENCY-FEASIBILITY/feasibility.py) and [`results.json`](evidence/A-REACTION-EFFICIENCY-FEASIBILITY/results.json) (deterministic: two runs give the same sha256; about 30 s).

## 1. Final decisions and rectifications

- **Candidate: the reaction's directional efficiency E.** The time profile is descriptive only. A result on E does not validate speed, temporal order or overall professional quality.
- **Oriented domain.** q = d × price (d = +1 LONG, −1 SHORT). From the A source window (the 7 complete 15m bars ending at the birth close): Aq = minimum of the transformed lows, Bq = maximum of the transformed highs, Iq = Bq − Aq > 0. For SHORT, high_q = −low and low_q = −high. In every episode, Aq and Bq equal the engine's `impulse_A`/`impulse_B` × d in the BIRTH record.
- **Origin and q0.** The origin is the market end of the source bar (the 15m bar whose close fired the birth); q0 is its transformed close. In historical runs the birth is published at the origin (03:30:00). In the live run it is published at 03:30:01.5, while the origin stays at 03:30:00.
- **Admitted bars.** Complete 1m trade bars with start ≥ origin, end ≤ t and known_at ≤ t. A bar crossing the origin is excluded. On the 1m grid none can cross it, because the origin is a 15m boundary. In live, [03:30,03:31) lies wholly after the origin and is known at 03:31:01, after the birth.
- **E = (q0 − qn) / Σ|qj − q(j−1)|** over the admitted prefix. It has four statuses:
  - INSUFFICIENT_DATA: no bar yet;
  - UNDEFINED_ZERO_DENOMINATOR: never reported as 0;
  - INCOMPLETE_MISSING_MINUTE: no fill;
  - VALUE.

  The existing `measures.efficiency` is not reused: it is unsigned and returns 0 for a zero path. At the first ARM, a complete prefix always has a non-zero denominator, because the ARM requires a lower 15m close.
- **Changes from the design.**
  - E is the candidate; the curve is descriptive.
  - A/B are renamed Aq/Bq.
  - The open "fixed age" is replaced by the first-ARM cutoff (§3).
  - A horizon observed without B is a known outcome, not censoring.
  - The comparison is reduced to four quantities, and R/I is no longer matched (§4).

## 2. Synthetic paths and results (ordinary entry paths)

**Ordinary entry paths.** The historical episodes go through the pure kernel order (`harness.run_pure`, v0.6, from the first warm-up minute, including temporal readiness). The live episode goes through `LiveSession` (catch-up start at 03:16, then recorded receipts, dispatch at +1.5 s), reusing the existing test helper. Nothing is injected and no gate or timestamp is touched.

**Base geometry.** The existing `a3_base` A LONG fixture:
- Aq 97000, Bq 100900, Iq 3900, S15 2000, z 200;
- birth 03:30 with q0 100700;
- first ARM 03:45 (R 100000, K 100700, V 99800);
- original expiry 05:30.

Only the minutes inside the reaction bar [03:30,03:45) vary, always with the same 15m OHLC (100700 / 100700 / 100000 / 100049.9). The BIRTH and ARM record contents (envelope excluded) are identical across the prefixes. No transition occurs between birth and cutoff.

| Prefix (minute closes in [03:30,03:45)) | E at the cutoff | Profile (descriptive) |
|---|---|---|
| BASE: the existing fixture, flat 5 minutes, down 5, up 5 | 0.86692 (650.1 / 749.9) | UNDEFINED ×5, then 1.0, falling to 0.867 |
| FRONT: down in 2 minutes, flat 12, up 1 | 0.86692 (650.1 / 749.9) | 1.0 from the first minute, then 0.867 |
| ALT: 15 alternating closes | 0.11713 (650.1 / 5550.1) | oscillating |
| GAP: BASE with [03:37,03:38) MISSING | none: INCOMPLETE from 03:38 | the engine ends it UNASSESSABLE `REQUIRED_GAP_15m` at 03:45: no ARM, so outside the population |

- **Different E at the same geometry and duration:** BASE vs ALT (same comparison key).
- **Same E, different temporal order:** BASE vs FRONT.

| Continuation after the cutoff (BASE prefix) | Observation outcome | Engine, for comparison |
|---|---|---|
| B: the existing `a3_return_long` | B_BEFORE_PREMISE_FAILURE at 04:47 (1m high 100910) | REVISE 04:00, CONFIRM 04:01, DESTINATION_REACHED 04:47 |
| F: anchor lost, REARM, decline, then rally | PREMISE_FAILURE_BEFORE_B at 05:00 (15m close 97100 ≤ 97200). A B contact at 05:25 is not counted | REVISE 04:00; ANCHOR_LOST 04:09; REARM 04:15; ANCHOR_LOST 04:20; REARM 04:30; ANCHOR_LOST 04:34; WITHDRAWN (context) 04:45 |
| H: flat around 100050 | HORIZON_OBSERVED_NO_B at 05:30 | CONFIRM 04:01, OWNER_RELEASE 05:30, STALLED 06:01 |
| G: H with [04:30,04:31) MISSING | INCOMPLETE_CENSORED at 04:30 | UNASSESSABLE `REQUIRED_MONITORING_GAP` 04:31 |
| X, historical: [03:45,03:46) reaches 100900 | B_BEFORE_PREMISE_FAILURE at 03:46 (the minute is wholly after the cutoff 03:45:00) | DESTINATION_REACHED 03:46 |
| X, live: same OHLC | AMBIGUOUS: the minute straddles the cutoff 03:45:01.5 | UNASSESSABLE `FIRST_ARM_DESTINATION_CONTACT_TIME_AMBIGUOUS` |

FRONT+B and ALT+B both give B_BEFORE at 04:47.

**Reflection.** Every path is mirrored about 100000 for SHORT, in 9 of 9 pairs. E, its status, the comparison key, the outcome class, the birth and cutoff times and Iq are all identical.

**History.** E is computed on a single profile at each published transition of BASE+F. Neither REVISE nor REARM resets it:

| Transition | Time | E | Bars |
|---|---|---|---|
| ARM | 03:45 | 0.86692 | 15 |
| REVISE | 04:00 | 0.78964 | 30 |
| ANCHOR_LOST | 04:09 | 0.82385 | 39 |
| REARM | 04:15 | 0.76654 | 45 |
| ANCHOR_LOST | 04:20 | 0.80655 | 50 |
| REARM | 04:30 | 0.85593 | 60 |

The value at the cutoff is never rewritten.

## 3. Single cutoff: the first ARM publication

The cutoff is the first ARM publication (v0.4+ `first_arm_at`, immutable, equal to `destination_monitoring_from`).
- **Why this event.** It is where A recognizes a qualified reaction before confirmation. It is also where the existing contract starts monitoring B, so the outcome window starts exactly there. There is one per scenario, and no anchor is chosen afterwards.
- **Causal.** E at the cutoff uses only bars known at the publication: [03:44,03:45), known at 03:45:00 in historical runs and at 03:45:01 in live (publication 03:45:01.5).
- **Variation.** The pairs above vary at the cutoff with an identical key.
- **No alternatives tried.** No other cutoff was tested.

## 4. Essential comparison

**One relation.** Y = 1 for B_BEFORE_PREMISE_FAILURE; Y = 0 for PREMISE_FAILURE_BEFORE_B or HORIZON_OBSERVED_NO_B. Inside each stratum, every pair with E_i > E_j is classified:
- concordant (C) if Y_i < Y_j;
- discordant (D) if Y_i > Y_j;
- uninformative (U) if Y_i = Y_j.

Report C, D and U and the stratified **(C − D)/(C + D + U)**, i.e. Somers' D of Y on E over the pairs untied in E. This uses no model, no threshold and no minimum quota.

**Stratum key: four quantities, orientation-free, with S15 frozen at birth.**
1. Age at the cutoff in 15m bars (exact, 1–8). It also fixes the remaining horizon, 120 − 15·age minutes.
2. Phase at the cutoff (exact).
3. dB = (Bq − qc)/S15, in bins of 0.25 S15.
4. dP = (qc − (Aq + z))/S15, in bins of 0.25 S15.

Here qc is the transformed close at the cutoff. The 0.25 S15 bin is the method's own `reaction_min_scale` unit. It is a matching convention, not a "good reaction" threshold.

**Already determined by the key (not matched separately).**
- Iq/S15 = dB + dP + z/S15, and the close retracement x = dB/(Iq/S15).
- z/S15 = 0.1 by the register (the 2-tick floor applies only at very small scales).
- The distances to B and to the premise.
- The remaining horizon.
- The context: UP relative to d by the ARM gate. EXPANSION can only be in the same direction.
- The anchor state: epoch 1 ACTIVE at the first ARM.

**R/I is not matched.** The overshoot below the cutoff close is part of the path that E measures. Matching on it would partly condition on the exposure. It is reported descriptively.

**Not comparable** (counted, never imputed):
- E not VALUE;
- outcome AMBIGUOUS or INCOMPLETE_CENSORED;
- strata with a single eligible episode, or with no variation in E or Y.

No overlap at all means the relation is not estimable. It does not mean there is no relation. Episodes overlapping in time, including LONG and SHORT, are dependent; how to handle that is left to the future exploration, as is the sufficiency of the real comparisons.

**Synthetic check.** Every armed episode falls in key (1, TRANSITION, bin dB 1, bin dP 5), with dB 0.425 and dP 1.425. BASE vs ALT shows E varying inside one stratum. No statistic is computed: the synthetic outcomes are designed continuations of shared prefixes, not independent episodes.

## 5. Outcome taxonomy

**Frozen at the cutoff:**
- Bq;
- the premise as a complete 15m close_q ≤ Aq + z (the pre-confirmation contract `CLOSE_AT_OR_BEYOND_A_PLUS_ZONE`);
- the horizon H = `original_expiry` (birth publication + 120 min).

Later engine management does not change them: confirmation (premise "beyond A", deadline confirmation + 4 h), REVISE/REARM, the call.

**Contacts, closes and precedence.**
- **B contact:** a complete 1m bar wholly after the cutoff with high_q ≥ Bq, as in v0.4 destination monitoring.
- **Premise failure:** a complete 15m close after the cutoff.
- **Order:** by the market time of the interval ends.
- **B touched and the premise failed in the same minute:** B comes first by definition. The close is the last price and Bq > Pq, so the high cannot be the close. No intrabar order is inferred.
- **Horizon:** an event counts only if it becomes known before H. This follows the engine order, where timers precede the intervals and closes admitted at the same instant.

**Classes:**
1. **B_BEFORE_PREMISE_FAILURE** (Y = 1).
2. **PREMISE_FAILURE_BEFORE_B** (Y = 0). A later B stays an annotation.
3. **HORIZON_OBSERVED_NO_B:** known outcome, B not reached within the horizon (Y = 0).
4. **AMBIGUOUS:** a B contact in a bar straddling the cutoff (= `FIRST_ARM_DESTINATION_CONTACT_TIME_AMBIGUOUS`). Excluded and counted.
5. **INCOMPLETE_CENSORED:** a missing or stale minute, or an interrupted observation, before resolution. Excluded and counted.
6. **Other concurrent engine terminals** are annotations only, and the price observation continues. They are not called censoring or failure:
   - context withdrawal;
   - anchor loss or REARM;
   - confirmation, call and its terminals;
   - STALLED;
   - owner release;
   - V-level UNASSESSABLE.

   Coverage-loss terminals coincide with class 5 through the missing data itself.

## 6. Checks run and limits

**Checks (in the script):**
- Aq/Bq against the BIRTH records;
- the horizon against `original_expiry`;
- no transition before the cutoff;
- identical BIRTH/ARM records across the prefixes;
- known_at ≤ cutoff for every bar in E at the cutoff;
- 9/9 reflection;
- determinism.

No product code or test changed, so no product suite was run. Ruff is not installed in `.venv`, so no lint ran.

**Limits.**
- Synthetic engineering inputs, not market data.
- One geometry: age 1 bar, phase TRANSITION.
- The horizon-straddle ambiguity and stale (rather than missing) data are not exercised through the engine.
- The comparison statistic is defined, not computed.
- By construction, E loses the temporal order (BASE = FRONT).
- No evidence of predictive or economic value.

## 7. Verdict

**FEASIBLE, on synthetic evidence only; no impediment found.** E is computable causally at one cutoff through the ordinary paths. It varies at a fixed comparison key, and outcomes are classifiable with the existing contracts.

Before any real exploration, a separate authorization is needed for:
- this note's review;
- the period and data;
- the evidence, uncertainty and dependence conventions.
