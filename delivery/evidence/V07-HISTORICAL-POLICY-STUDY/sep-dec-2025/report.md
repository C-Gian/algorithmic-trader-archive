
## Adviser evaluation — Candidate v0.7 (trigger/destination compatibility over MP-005; engineering review pending; hypothetical, no orders)
- Method `btc.context-action.v0.7` / `tdc.rules.v0.7` · rules `1f3704f4453b` · register `8525ec74e2cc` · profile `7c86833734da` · identity `55d76c99c3a1`
- Pre-confirmation A anchors (owners): lost 111 (warmup-origin 0) · re-armed by a deeper completed reaction 99 · confirmed after replacement 61 · structural end while waiting without replacement 36
- Anchor events: losses 179 (certified V contacts 179, ambiguous 0) · replacements 143 · supersessions without contact 22 · calls after replacement 1
- Scenario transitions: {'A_LONG:ANCHOR_LOST': 96, 'A_LONG:ARM': 89, 'A_LONG:BIRTH': 187, 'A_LONG:CONFIRM': 54, 'A_LONG:OWNER_RELEASE': 21, 'A_LONG:REARM': 80, 'A_LONG:REVISE': 9, 'A_LONG:TERMINAL': 187, 'A_SHORT:ANCHOR_LOST': 83, 'A_SHORT:ARM': 72, 'A_SHORT:BIRTH': 172, 'A_SHORT:CONFIRM': 35, 'A_SHORT:OWNER_RELEASE': 11, 'A_SHORT:REARM': 63, 'A_SHORT:REVISE': 13, 'A_SHORT:TERMINAL': 172, 'B_LONG:ARM': 4, 'B_LONG:BIRTH': 24, 'B_LONG:CONFIRM': 2, 'B_LONG:TERMINAL': 24, 'B_SHORT:ARM': 2, 'B_SHORT:BIRTH': 20, 'B_SHORT:CONFIRM': 2, 'B_SHORT:TERMINAL': 20, 'C_LONG:ARM': 9, 'C_LONG:BIRTH': 16, 'C_LONG:CONFIRM': 6, 'C_LONG:TERMINAL': 16, 'C_SHORT:ARM': 9, 'C_SHORT:BIRTH': 21, 'C_SHORT:CONFIRM': 6, 'C_SHORT:TERMINAL': 21} · warmup-context scenarios 131
- A confirmations 89: D 82 · N 24 · N/D 0.2927 · excluded {'INSIDE_ZONE': 7}
- A routing: {'IMMEDIATE_ISSUED': 1, 'RETURN_WAIT': 57, 'TERMINAL:AT_OPPOSING_AREA': 7, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 22, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 2}
- A destination contacted before confirmation (no call, rules unchanged): 24 — e.g. LONG AL-2025-09-01T18:45:00+00:00-8d300aec6989 at 2025-09-01T19:25:00Z (K 109263.8 · destination 109244.6); LONG AL-2025-09-12T19:15:00+00:00-89c880f34a0e at 2025-09-12T19:54:00Z (K 116499.2 · destination 116520); SHORT AS-2025-09-17T03:45:00+00:00-fc8279a24aa5 at 2025-09-17T04:17:00Z (K 116305.2 · destination 116300.1)
- Waiting for a usable price: opened 57 · usable return observed 12 · endings {'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 4, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 12, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 8, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 16, 'TERMINAL:SCENARIO_TERMINAL': 17} · cap revisions 7
- Issued by family/mode: {'A_IMMEDIATE': 1} · guidance retired by scenario terminal 0
- **A RETURN owners entered at PRIMARY 60 s: 0** (descriptive count; evidence criterion NOT_APPLICABLE to this method - the earlier 20-owner convention does not apply and no substitute is registered)
  - A_IMMEDIATE: calls 1 · entered 1 · target 0 · stop 0 · other exits 1 · no entry 0 · price-net sum 0.001008815215741288428017315836
- Evaluation 2025-09-01T00:00:00+00:00 → 2026-01-01T00:00:00+00:00 · clock end 2026-01-01T06:05:00Z
- Coverage: 175680 of 175680 evaluation minutes assessable (0 unavailable) · calendar NONE_UNKNOWN · funding PRICE_NET_ONLY · quotes NOT_COVERED (historical, MODELED execution)
- **Calls: 1** · 0.06/evaluated week · 0.06/assessable week · by family {'A_LONG': 1} · warmup calls not scored 0
- Entry available (minutes per call): median 17.0000 · max 17.0000 · reopens 4 · longest no-call interval 1584.433333333333333333333333 h
- Thesis outcomes (guidance): {'TIME_EXPIRED': 1}
- Funnel: births {'A_LONG': 187, 'A_SHORT': 172, 'B_LONG': 24, 'B_SHORT': 20, 'C_LONG': 16, 'C_SHORT': 21} · arms {'A_LONG': 89, 'A_SHORT': 72, 'B_LONG': 4, 'B_SHORT': 2, 'C_LONG': 9, 'C_SHORT': 9} · trigger evaluations 105 · issued 1 · slot-occupied 0 · priority 0 · conflicted 0
- Trigger rejections: SCENARIO_TERMINAL 336, NO_ROOM_AFTER_COSTS 53, CLOSE_OUTSIDE_RETURN_CORRIDOR 34, REWARD_RISK_BELOW_MINIMUM 26, INITIAL_RESPONSE_INCOMPATIBLE 12, AT_OPPOSING_AREA 8, PRE_ENTRY_TARGET_CONTACT 5
- Attempt endings: A:EXPIRED:SPENT_HIGH_BEYOND_B_BEFORE_REACTION 188, A:DESTINATION_REACHED:DESTINATION_CONTACT 78, A:WITHDRAWN:CONTEXT_OR_ADVERSE_EXPANSION 42, A:INVALIDATED:V_CONTACT 28, B:WITHDRAWN:RETURNED_INSIDE_BEFORE_RETEST 14, C:WITHDRAWN:CONTEXT_NOT_BALANCED_AT_BIRTH 13, B:EXPIRED:ORIGINAL_SETUP_DEADLINE 13, A:WITHDRAWN:CLOSE_AT_OR_BEYOND_A_PLUS_ZONE 13, B:EXPIRED:BOX_RETIRED 7, C:INVALIDATED:V_CONTACT 7, C:WITHDRAWN:DIRECTIONAL_EXPANSION_AT_BIRTH 6, C:DESTINATION_REACHED:DESTINATION_CONTACT 5
- Condition time (overlapping; of 175680.00 covered min): ANY_COMMON_BLOCKER 22.00 min (4×), CONFIRMED_SCENARIO_ACTIVE 5403.00 min (105×), DISLOCATION_TRADE_INDEX 22.00 min (4×), DISLOCATION_TRADE_MARK 3.00 min (2×), ISSUABLE_IF_TRIGGERED 175418.00 min (0×), NO_ARMED_SCENARIO 170810.00 min (326×), PRIORITY_COMPETITION 3.00 min (1×), SLOT_OCCUPIED 240.00 min (1×), WAITING_FOR_USABLE_PRICE 1287.00 min (57×)
- Slot/priority exposure (min): SLOT_OCCUPIED 240.00, SLOT_OCCUPIED_WITH_ARMED 0.00, PRIORITY_COMPETITION 3.00, CONFLICTED_ARMED 0.00
- Hypothetical PRIMARY (60 s entry delay): 1 paths · entries 1 · NO_ENTRY 0 · target 0 · stop 0 · guidance exits 1 · ambiguous 0 · censored 0 · unresolved 0
  - price-net sum 0.001008815215741288428017315836 (normalized units) · median 10.0882 bps · stress (5 bps/leg allowance) sum 0.0004080920649710268583901716403 · total net UNAVAILABLE (PRICE_NET_ONLY: funding completeness unproven)
- Sensitivity ENTRY_DELAY_0: 1 paths · NO_ENTRY 0 · price-net sum 0.001214226888505138311639015392
- Sensitivity ENTRY_DELAY_120: 1 paths · NO_ENTRY 0 · price-net sum 0.001452085182595853986159006465
- Sensitivity HORIZON_ONLY: 1 paths · NO_ENTRY 0 · price-net sum 0.001008815215741288428017315836 (no stop/target; exits at issue + hard horizon)
- View samples +1h: 153 directional scored, 74 matching sign · abstentions 2775 · unavailable 0 · persistence 1434/2928 · antecedent activated 128/153 (not calibrated)
- View samples +4h: 153 directional scored, 77 matching sign · abstentions 2775 · unavailable 0 · persistence 1416/2928 · antecedent activated 130/153 (not calibrated)
- **Zero-call diagnosis:** A_DESTINATION_BEFORE_CONFIRMATION: 24 armed A scenario(s) ended at the narrative destination before confirmation (no call; closed rule, not relaxed) · NO_LOCAL_RECOVERY_OBSERVED: 12 reference(s) prepared, 0 contradicted, 12 initially incompatible (subset of X), 12 ended by another cause in total (X), 0 still waiting
  - 2025-10-26T23:34:00Z A LONG ref 114599.9 stop 114309.5 target 115739.3 (LANDMARK) → TIME_EXPIRED (HARD_DEADLINE) · entry available 17 min
- Adviser conclusion: **REPORTED_FOR_DIRECTOR_REVIEW** — v0.7 results are reported for Director diagnosis; no registered evidence criterion applies. v0.7 changes the explanation and the market reading only (an A condition that would already reach its destination is not counted as directional support); calls, entries, selection and terminals are those of v0.6, so a v0.6/v0.7 comparison on the same pack must show identical calls.

### Launch pins
- Method v0.7 `btc.context-action.v0.7` / `tdc.rules.v0.7` · rules `1f3704f4453b` · register `8525ec74e2cc` · implementation adviser.core.v7 · identity `55d76c99c3a1` · build `13268640168468c6b30a42140a1e2b81582de2df`
- Profile `7c86833734da` · clock temporal.clock.modeled-complete-prefix.v1 · evaluator algotrader.adviser-evaluation.v1 `85504d5843e1` · PRIMARY entry delay 60 s · fee/leg 0.0005 · allowance/leg 0.0002 · funding PRICE_NET_ONLY
- Pack `pack-1ae7d36c20adbde0a468a7e0f6d8750a9951aa8e` · initialization from 2025-07-28T00:00:00+00:00 (not evaluated) · evaluation 2025-09-01T00:00:00+00:00 → 2026-01-01T00:00:00+00:00 · tail end 2026-01-01T06:05:00+00:00

### Context at the evaluation start (initialization is not evaluated)
- Initialization 2025-07-28T00:00:00+00:00 → 2025-09-01T00:00:00+00:00 (840 h, REGISTERED_EXPLICIT_INITIALIZATION) · trade coverage complete · trade_bar_1m 50400/50400; mark_bar_1m 50400/50400; index_bar_1m 50400/50400
- Readiness at start: {'trade.15m': 'READY', 'trade.1h': 'READY', 'trade.1m': 'READY'}
  - previous_day [2025-08-31T00:00:00+00:00, 2025-09-01T00:00:00+00:00): COVERED
  - previous_week [2025-08-25T00:00:00+00:00, 2025-09-01T00:00:00+00:00): COVERED
  - previous_month [2025-08-01T00:00:00+00:00, 2025-09-01T00:00:00+00:00): COVERED
  - pivot_15m_memory [2025-08-31T00:00:00+00:00, 2025-09-01T00:00:00+00:00): COVERED
  - pivot_1h_memory [2025-08-25T00:00:00+00:00, 2025-09-01T00:00:00+00:00): COVERED
  - PREV_1D_HIGH: BUILT_ACTIVE
  - PREV_1D_LOW: BUILT_ACTIVE
  - PREV_1W_HIGH: BUILT_ACTIVE
  - PREV_1W_LOW: BUILT_ACTIVE
  - PREV_1MO_HIGH: BUILT_ACTIVE
  - PREV_1MO_LOW: BUILT_ACTIVE
  - PIVOTS_15M: BUILT · ever built 888 · active 6 · memory window COVERED · completeness NOT_CERTIFIED
  - PIVOTS_1H: BUILT · ever built 233 · active 13 · memory window COVERED · completeness NOT_CERTIFIED
- Facts at the evaluation start (records published at that dispatch included). 'Never built' and 'insufficient data' are kept apart from levels built and then legitimately broken, expired or retired. Pivot memory completeness is NOT certified: formation, publication, breaking, retirement and the per-horizon cap are not reconstructed. The initialization is never evaluated.

### Continuous run: total and monthly sections (one run, no monthly reset)
- Attribution: calls -> month of issue, followed to their outcome after the month ends (never counted twice); confirmations/scenario transitions -> month of publication; WAITs -> month opened, with their ending wherever it falls; coverage -> minutes inside the month; view samples -> sample time (their 1h/4h endpoint may fall in the next month)
- each section uses its own denominator: evaluation minutes, view samples, A confirmations, opened WAITs and issued calls are different populations
- Hypothetical sums: sum of normalized one-unit hypothetical price-net outcomes (N0=1, q=1/E): not an account return, not compounded, no sizing; funding not covered (PRICE_NET_ONLY)
- paths still open at the clock end are CENSORED/UNRESOLVED and kept visible; tail data are never scored
| Period | Assessable min | A conf. | WAIT | Calls | Resolved later | PRIMARY closed | PRIMARY price-net |
|---|---:|---:|---:|---:|---:|---:|---:|
| TOTAL | 175680/175680 | 89 | 57 | 1 | 0 | 1 | +0.101% over 1 closed |
| 2025-09 | 43200/43200 | 25 | 11 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-10 | 44640/44640 | 19 | 14 | 1 | 0 | 1 | +0.101% over 1 closed |
| 2025-11 | 43200/43200 | 20 | 16 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-12 | 44640/44640 | 25 | 16 | 0 | 0 | 0 | none observed (0 closed) |

Hypothetical outcomes per variant (calls by month of issue; expected = evaluable calls for a pinned variant; 'not yet recorded' = expected pair without a terminal record, nothing inferred for it)
| Period | Variant | Expected | Records | Not yet recorded | CLOSED | with price-net | NO_ENTRY | CENSORED | UNRESOLVED | AMBIGUOUS | Exit after period | Price-net sum (population) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TOTAL | PRIMARY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.101% over 1 closed |
| TOTAL | ENTRY_DELAY_0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.121% over 1 closed |
| TOTAL | ENTRY_DELAY_120 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.145% over 1 closed |
| TOTAL | HORIZON_ONLY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.101% over 1 closed |
| 2025-09 | PRIMARY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-09 | ENTRY_DELAY_0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-09 | ENTRY_DELAY_120 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-09 | HORIZON_ONLY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-10 | PRIMARY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.101% over 1 closed |
| 2025-10 | ENTRY_DELAY_0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.121% over 1 closed |
| 2025-10 | ENTRY_DELAY_120 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.145% over 1 closed |
| 2025-10 | HORIZON_ONLY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.101% over 1 closed |
| 2025-11 | PRIMARY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-11 | ENTRY_DELAY_0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-11 | ENTRY_DELAY_120 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-11 | HORIZON_ONLY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-12 | PRIMARY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-12 | ENTRY_DELAY_0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-12 | ENTRY_DELAY_120 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-12 | HORIZON_ONLY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
- TOTAL MarketView: covered 175680/175680 min · assessable 175680 · unavailable 0 · rows BALANCED_RANGE 37539, CONDITIONAL_SCENARIO 8531, NO_QUALIFIED_STRUCTURE 120112, WATCH_ONLY 9498
- TOTAL samples: 2928 (BALANCED 655, DOWN 64, UNCERTAIN 2120, UP 89) · 1h directional 74/153 matching sign, endpoint unavailable 0 · 4h directional 77/153 matching sign, endpoint unavailable 0
- TOTAL scenarios: A_ANCHOR_LOST 179, A_ARM 161, A_BIRTH 359, A_CONFIRM 89, A_OWNER_RELEASE 32, A_REARM 143, A_REVISE 22, A_TERMINAL 359, B_ARM 6, B_BIRTH 44, B_CONFIRM 4, B_TERMINAL 44, C_ARM 18, C_BIRTH 37, C_CONFIRM 12, C_TERMINAL 37 · A confirmations 89 · D 82 / N 24
- TOTAL calls: guidance {'TIME_EXPIRED': 1} · routing {'IMMEDIATE_ISSUED': 1, 'RETURN_WAIT': 57, 'TERMINAL:AT_OPPOSING_AREA': 7, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 22, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 2} · WAIT endings {'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 4, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 12, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 8, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 16, 'TERMINAL:SCENARIO_TERMINAL': 17}
- 2025-09 MarketView: covered 43200/43200 min · assessable 43200 · unavailable 0 · rows BALANCED_RANGE 8915, CONDITIONAL_SCENARIO 1848, NO_QUALIFIED_STRUCTURE 30251, WATCH_ONLY 2186
- 2025-09 samples: 720 (BALANCED 159, DOWN 10, UNCERTAIN 527, UP 24) · 1h directional 12/34 matching sign, endpoint unavailable 0 · 4h directional 14/34 matching sign, endpoint unavailable 0
- 2025-09 scenarios: A_ANCHOR_LOST 38, A_ARM 37, A_BIRTH 84, A_CONFIRM 25, A_OWNER_RELEASE 6, A_REARM 33, A_REVISE 4, A_TERMINAL 84, B_ARM 3, B_BIRTH 12, B_CONFIRM 1, B_TERMINAL 12, C_ARM 6, C_BIRTH 12, C_CONFIRM 5, C_TERMINAL 12 · A confirmations 25 · D 24 / N 13
- 2025-09 calls: guidance {} · routing {'RETURN_WAIT': 11, 'TERMINAL:AT_OPPOSING_AREA': 1, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 13} · WAIT endings {'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 1, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 3, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 2, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 2, 'TERMINAL:SCENARIO_TERMINAL': 3}
- 2025-10 MarketView: covered 44640/44640 min · assessable 44640 · unavailable 0 · rows BALANCED_RANGE 9383, CONDITIONAL_SCENARIO 2465, NO_QUALIFIED_STRUCTURE 30304, WATCH_ONLY 2488
- 2025-10 samples: 744 (BALANCED 163, DOWN 21, UNCERTAIN 542, UP 18) · 1h directional 24/39 matching sign, endpoint unavailable 0 · 4h directional 27/39 matching sign, endpoint unavailable 0
- 2025-10 scenarios: A_ANCHOR_LOST 55, A_ARM 42, A_BIRTH 89, A_CONFIRM 19, A_OWNER_RELEASE 9, A_REARM 44, A_REVISE 6, A_TERMINAL 89, B_ARM 3, B_BIRTH 13, B_CONFIRM 3, B_TERMINAL 13, C_ARM 5, C_BIRTH 12, C_CONFIRM 2, C_TERMINAL 12 · A confirmations 19 · D 18 / N 3
- 2025-10 calls: guidance {'TIME_EXPIRED': 1} · routing {'IMMEDIATE_ISSUED': 1, 'RETURN_WAIT': 14, 'TERMINAL:AT_OPPOSING_AREA': 1, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 2, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 1} · WAIT endings {'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 3, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 2, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 4, 'TERMINAL:SCENARIO_TERMINAL': 5}
- 2025-11 MarketView: covered 43200/43200 min · assessable 43200 · unavailable 0 · rows BALANCED_RANGE 8750, CONDITIONAL_SCENARIO 1628, NO_QUALIFIED_STRUCTURE 30328, WATCH_ONLY 2494
- 2025-11 samples: 720 (BALANCED 159, DOWN 15, UNCERTAIN 532, UP 14) · 1h directional 13/29 matching sign, endpoint unavailable 0 · 4h directional 13/29 matching sign, endpoint unavailable 0
- 2025-11 scenarios: A_ANCHOR_LOST 37, A_ARM 39, A_BIRTH 94, A_CONFIRM 20, A_OWNER_RELEASE 5, A_REARM 27, A_REVISE 8, A_TERMINAL 94, B_BIRTH 12, B_TERMINAL 12, C_ARM 4, C_BIRTH 7, C_CONFIRM 3, C_TERMINAL 7 · A confirmations 20 · D 19 / N 3
- 2025-11 calls: guidance {} · routing {'RETURN_WAIT': 16, 'TERMINAL:AT_OPPOSING_AREA': 1, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 3} · WAIT endings {'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 2, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 2, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 5, 'TERMINAL:SCENARIO_TERMINAL': 7}
- 2025-12 MarketView: covered 44640/44640 min · assessable 44640 · unavailable 0 · rows BALANCED_RANGE 10491, CONDITIONAL_SCENARIO 2590, NO_QUALIFIED_STRUCTURE 29229, WATCH_ONLY 2330
- 2025-12 samples: 744 (BALANCED 174, DOWN 18, UNCERTAIN 519, UP 33) · 1h directional 25/51 matching sign, endpoint unavailable 0 · 4h directional 23/51 matching sign, endpoint unavailable 0
- 2025-12 scenarios: A_ANCHOR_LOST 49, A_ARM 43, A_BIRTH 92, A_CONFIRM 25, A_OWNER_RELEASE 12, A_REARM 39, A_REVISE 4, A_TERMINAL 92, B_BIRTH 7, B_TERMINAL 7, C_ARM 3, C_BIRTH 6, C_CONFIRM 2, C_TERMINAL 6 · A confirmations 25 · D 21 / N 5
- 2025-12 calls: guidance {} · routing {'RETURN_WAIT': 16, 'TERMINAL:AT_OPPOSING_AREA': 4, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 4, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 1} · WAIT endings {'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 1, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 4, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 4, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 5, 'TERMINAL:SCENARIO_TERMINAL': 2}
- Reconciliation total vs months: PASS (arithmetic of the available records only; it is not outcome completeness)
- Path records: 4 available · 4 admitted · 0 expected missing · 0 extraneous · 0 duplicates
- Outcome completeness: COMPLETE — 4/4 expected call–variant terminal records available · run status completed

### A RETURN response (MP-004 §7 with MP-005 §6; unit = A RETURN child)
- W A RETURN children routed to WAIT_RETURN · P local references prepared · C ended by a local contradiction before any recovery · R first decisive recoveries observed · N first recoveries not issuable · I calls issued · X other endings after the reference · A still waiting for the response at the report cutoff
- Cutoff 2026-01-01T06:05:00+00:00: A = waits still open at the last committed record
- Identities P = C + R + X + A, R = N + I, W = P + endings before a reference + WAIT_RETURN open; a zero denominator is undefined.

| Period | W | P | C | R | N | I | X | A | P/W | C/P | R/P | N/R | I/R | I/P | Identities |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Total | 57 | 12 | 0 | 0 | 0 | 0 | 12 | 0 | 0.2105 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
| 2025-09 | 11 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0.2727 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
| 2025-10 | 14 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0.2143 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
| 2025-11 | 16 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0.1250 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
| 2025-12 | 16 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0.2500 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
- LONG: W 29 · P 6 · C 0 · R 0 · N 0 · I 0 · X 6 · A 0
- SHORT: W 28 · P 6 · C 0 · R 0 · N 0 · I 0 · X 6 · A 0
- Ended before a reference: {'CONTEXT_FORBIDDEN_PREISSUE': 4, 'ORIGINAL_SETUP_DEADLINE': 8, 'PRE_ENTRY_TARGET_CONTACT': 16, 'SCENARIO_TERMINAL': 17} · WAIT_RETURN still open 0
- N primary reason: {} · by class {} · late first recovery 0 · blocker incidence (not summable) {}
- X by priority cause: {'INITIAL_RESPONSE_INCOMPATIBLE': 12}
- Months (child -> calendar month in which its WAIT opened, followed to its ending wherever it falls (never counted twice); no reset at a month boundary): sum to total yes · identities in every month yes
- Warmup (not evaluated): 14 child(ren); cleared at the evaluation start {}; other warmup endings 14
- Cross-checks with the report funnel: W_equals_waits_opened yes · I_equals_A_RETURN_calls_in_window yes
- C/P does not measure real deterioration and R/P does not measure continuation quality; outcomes and later entries belong to the separate economic report. No frequency or profit quota.

#### Initial response incompatibility (MP-005 §6; subset of X)
| Period | INITIAL_RESPONSE_INCOMPATIBLE | base CORRIDOR | base HISTORICAL_ECONOMICS | X | P | ratio over P | subset of X |
|---|---|---|---|---|---|---|---|
| Total | 12 | 3 | 9 | 12 | 12 | 1.0000 | yes |
| 2025-09 | 3 | 1 | 2 | 3 | 3 | 1.0000 | yes |
| 2025-10 | 3 | 1 | 2 | 3 | 3 | 1.0000 | yes |
| 2025-11 | 2 | 1 | 1 | 2 | 2 | 1.0000 | yes |
| 2025-12 | 4 | 0 | 4 | 4 | 4 | 1.0000 | yes |
- By direction: {'LONG': 6, 'SHORT': 6} · concurrent annotations (never a second terminal): {'HISTORICAL_ECONOMICS': 3}
  - LONG AL-2025-09-03T14:30:00+00:00-5252e6a700e8#entry: reference okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-09-03T16:25:00Z H0 112063 L0 111916.9 · F >= 112063.1 · C0 111850..112150 · A0 111850..111947.1 · F∩C0 112063.1..112150 · J0 ∅ → HISTORICAL_ECONOMICS
  - SHORT AS-2025-09-13T16:45:00+00:00-9ec3dc0c608c#entry: reference okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-09-13T18:15:00Z H0 115520 L0 115517.1 · F <= 115517.0 · C0 115469.7..115560.2 · A0 115517.4..115560.2 · F∩C0 115469.7..115517.0 · J0 ∅ → HISTORICAL_ECONOMICS
  - SHORT AS-2025-09-25T23:30:00+00:00-e544db07020e#entry: reference okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-09-26T00:51:00Z H0 109325 L0 109002.8 · F <= 109002.7 · C0 109178.3..109355.2 · A0 109232.8..109355.2 · F∩C0 ∅ · J0 ∅ → CORRIDOR
- INITIAL_RESPONSE_INCOMPATIBLE is a subset of X (never added a second time): P = C + R + X + A still holds; ratio over P, a zero denominator is undefined.
- An INITIAL_RESPONSE_INCOMPATIBLE ending terminates the entry attempt only; the structural scenario is not invalidated and keeps its own lifecycle.
- Declared information loss (MP-005 §6): a child ended INITIAL_RESPONSE_INCOMPATIBLE at its preparation receives no later local classification (C or R) that it might have produced under MP-004 v0.5; no counterfactual classification is reconstructed. Changes of C/P or R/P between v0.5 and v0.6 therefore do not show a better local response.
- Months (WAIT-open cohort, no reset): initial incompatibility sums to total yes

#### Trigger/destination compatibility (published records only)
- Incompatible publications: 28 ({'ARM': 28}) · scenarios concerned: 28
- MarketView publications without support from an armed scenario: 20
- Support restored by a compatible revision: 2
- Counted from the published antecedents and MarketView records only. An incompatible condition would reach its destination before it could confirm; v0.7 states it and does not count the scenario as directional support. Calls, entries, selection and terminals are those of v0.6.
