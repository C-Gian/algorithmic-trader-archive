
## Adviser evaluation — Candidate v0.7 (trigger/destination compatibility over MP-005; engineering review pending; hypothetical, no orders)
- Method `btc.context-action.v0.7` / `tdc.rules.v0.7` · rules `1f3704f4453b` · register `8525ec74e2cc` · profile `7c86833734da` · identity `c7d07273b47c`
- Pre-confirmation A anchors (owners): lost 118 (warmup-origin 0) · re-armed by a deeper completed reaction 99 · confirmed after replacement 56 · structural end while waiting without replacement 47
- Anchor events: losses 200 (certified V contacts 200, ambiguous 0) · replacements 153 · supersessions without contact 25 · calls after replacement 2
- Scenario transitions: {'A_LONG:ANCHOR_LOST': 113, 'A_LONG:ARM': 95, 'A_LONG:BIRTH': 193, 'A_LONG:CONFIRM': 53, 'A_LONG:OWNER_RELEASE': 16, 'A_LONG:REARM': 86, 'A_LONG:REVISE': 14, 'A_LONG:TERMINAL': 193, 'A_SHORT:ANCHOR_LOST': 87, 'A_SHORT:ARM': 72, 'A_SHORT:BIRTH': 183, 'A_SHORT:CONFIRM': 35, 'A_SHORT:OWNER_RELEASE': 9, 'A_SHORT:REARM': 67, 'A_SHORT:REVISE': 11, 'A_SHORT:TERMINAL': 183, 'B_LONG:ARM': 3, 'B_LONG:BIRTH': 20, 'B_LONG:CONFIRM': 2, 'B_LONG:TERMINAL': 20, 'B_SHORT:ARM': 3, 'B_SHORT:BIRTH': 13, 'B_SHORT:CONFIRM': 3, 'B_SHORT:TERMINAL': 13, 'C_LONG:ARM': 7, 'C_LONG:BIRTH': 13, 'C_LONG:CONFIRM': 6, 'C_LONG:TERMINAL': 13, 'C_SHORT:ARM': 12, 'C_SHORT:BIRTH': 19, 'C_SHORT:CONFIRM': 10, 'C_SHORT:TERMINAL': 19} · warmup-context scenarios 110
- A confirmations 88: D 77 · N 14 · N/D 0.1818 · excluded {'INSIDE_ZONE': 11}
- A routing: {'IMMEDIATE_ISSUED': 2, 'RETURN_WAIT': 58, 'TERMINAL:AT_OPPOSING_AREA': 11, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 13, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 4}
- A destination contacted before confirmation (no call, rules unchanged): 22 — e.g. SHORT AS-2025-01-03T07:45:00+00:00-18e568506085 at 2025-01-03T08:31:00Z (K 96339.9 · destination 96298.1); SHORT AS-2025-01-09T06:45:00+00:00-f621bcf9d91c at 2025-01-09T07:18:00Z (K 94052.9 · destination 94023.6); LONG AL-2025-01-10T06:45:00+00:00-b5cc098163b0 at 2025-01-10T07:25:00Z (K 94310 · destination 94338)
- Waiting for a usable price: opened 58 · usable return observed 18 · endings {'ISSUE:call-AL-2025-04-15T06': 1, 'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 3, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 17, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 6, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 18, 'TERMINAL:SCENARIO_TERMINAL': 13} · cap revisions 4
- Issued by family/mode: {'A_IMMEDIATE': 2, 'A_RETURN': 1, 'B_IMMEDIATE': 1} · guidance retired by scenario terminal 0
- **A RETURN owners entered at PRIMARY 60 s: 1** (descriptive count; evidence criterion NOT_APPLICABLE to this method - the earlier 20-owner convention does not apply and no substitute is registered)
  - B_IMMEDIATE: calls 1 · entered 1 · target 0 · stop 1 · other exits 0 · no entry 0 · price-net sum -0.002577777847834562304475892935
  - A_IMMEDIATE: calls 2 · entered 1 · target 0 · stop 0 · other exits 1 · no entry 1 · price-net sum 0.0004911602327260372871278719157
  - A_RETURN: calls 1 · entered 1 · target 1 · stop 0 · other exits 0 · no entry 0 · price-net sum 0.003050398743693877264231812369
- Evaluation 2025-01-01T00:00:00+00:00 → 2025-05-01T00:00:00+00:00 · clock end 2025-05-01T06:05:00Z
- Coverage: 172800 of 172800 evaluation minutes assessable (0 unavailable) · calendar NONE_UNKNOWN · funding PRICE_NET_ONLY · quotes NOT_COVERED (historical, MODELED execution)
- **Calls: 4** · 0.23/evaluated week · 0.23/assessable week · by family {'A_LONG': 1, 'A_SHORT': 2, 'B_SHORT': 1} · warmup calls not scored 3
- Entry available (minutes per call): median 4.0000 · max 82.0000 · reopens 11 · longest no-call interval 1707.466666666666666666666667 h
- Thesis outcomes (guidance): {'INVALIDATED': 1, 'TARGET_REACHED': 2, 'TIME_EXPIRED': 1}
- Funnel: births {'A_LONG': 193, 'A_SHORT': 183, 'B_LONG': 20, 'B_SHORT': 13, 'C_LONG': 13, 'C_SHORT': 19} · arms {'A_LONG': 95, 'A_SHORT': 72, 'B_LONG': 3, 'B_SHORT': 3, 'C_LONG': 7, 'C_SHORT': 12} · trigger evaluations 109 · issued 4 · slot-occupied 0 · priority 0 · conflicted 0
- Trigger rejections: SCENARIO_TERMINAL 333, NO_ROOM_AFTER_COSTS 51, CLOSE_OUTSIDE_RETURN_CORRIDOR 30, REWARD_RISK_BELOW_MINIMUM 23, INITIAL_RESPONSE_INCOMPATIBLE 17, AT_OPPOSING_AREA 12, PRE_ENTRY_TARGET_CONTACT 5
- Attempt endings: A:EXPIRED:SPENT_HIGH_BEYOND_B_BEFORE_REACTION 207, A:DESTINATION_REACHED:DESTINATION_CONTACT 74, A:WITHDRAWN:CONTEXT_OR_ADVERSE_EXPANSION 40, A:INVALIDATED:V_CONTACT 32, B:EXPIRED:ORIGINAL_SETUP_DEADLINE 12, A:WITHDRAWN:CLOSE_AT_OR_BEYOND_A_PLUS_ZONE 12, B:WITHDRAWN:RETURNED_INSIDE_BEFORE_RETEST 11, C:WITHDRAWN:CONTEXT_NOT_BALANCED_AT_BIRTH 10, C:DESTINATION_REACHED:DESTINATION_CONTACT 7, C:INVALIDATED:V_CONTACT 7, A:EXPIRED:ORIGINAL_SETUP_DEADLINE 7, B:INVALIDATED:V_CONTACT 4
- Condition time (overlapping; of 172800.00 covered min): ANY_COMMON_BLOCKER 3.00 min (1×), CONFIRMED_SCENARIO_ACTIVE 4342.00 min (109×), DISLOCATION_TRADE_INDEX 3.00 min (1×), ISSUABLE_IF_TRIGGERED 172522.00 min (0×), NO_ARMED_SCENARIO 167815.00 min (340×), SLOT_OCCUPIED 275.00 min (4×), SLOT_OCCUPIED_WITH_ARMED 22.00 min (3×), WAITING_FOR_LOCAL_RESPONSE 1.00 min (1×), WAITING_FOR_USABLE_PRICE 1101.00 min (58×)
- Slot/priority exposure (min): SLOT_OCCUPIED 275.00, SLOT_OCCUPIED_WITH_ARMED 22.00, PRIORITY_COMPETITION 0.00, CONFLICTED_ARMED 0.00
- Hypothetical PRIMARY (60 s entry delay): 4 paths · entries 3 · NO_ENTRY 1 · target 1 · stop 1 · guidance exits 1 · ambiguous 0 · censored 0 · unresolved 0
  - price-net sum 0.0009637811285853522468837913501 (normalized units) · median 4.9116 bps · stress (5 bps/leg allowance) sum -0.0008373410612661985039845223709 · total net UNAVAILABLE (PRICE_NET_ONLY: funding completeness unproven)
- Sensitivity ENTRY_DELAY_0: 4 paths · NO_ENTRY 0 · price-net sum 0.005970679522671396261529224541
- Sensitivity ENTRY_DELAY_120: 4 paths · NO_ENTRY 2 · price-net sum -0.001659442379615354274616498252
- Sensitivity HORIZON_ONLY: 4 paths · NO_ENTRY 1 · price-net sum 0.01351714530573154587367014799 (no stop/target; exits at issue + hard horizon)
- View samples +1h: 153 directional scored, 72 matching sign · abstentions 2727 · unavailable 0 · persistence 1367/2877 · antecedent activated 120/153 (not calibrated)
- View samples +4h: 153 directional scored, 70 matching sign · abstentions 2727 · unavailable 0 · persistence 1440/2877 · antecedent activated 124/153 (not calibrated)
- **Zero-call diagnosis:** A_DESTINATION_BEFORE_CONFIRMATION: 22 armed A scenario(s) ended at the narrative destination before confirmation (no call; closed rule, not relaxed)
  - 2025-01-08T12:01:00Z B SHORT ref 95135.8 stop 95272.9 target 94433.8 (LANDMARK) → INVALIDATED (CERTIFIED_INVALIDATION_CONTACT:okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-01-08T12:06:00Z) · entry available 4 min
  - 2025-01-23T03:48:00Z A SHORT ref 102844.3 stop 103030.0 target 102177.5 (LANDMARK) → TARGET_REACHED (CERTIFIED_TARGET_CONTACT:okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-01-23T03:51:00Z) · entry available 1 min
  - 2025-02-03T03:31:00Z A SHORT ref 94219.9 stop 94806.5 target 91365.0 (LANDMARK) → TIME_EXPIRED (HARD_DEADLINE) · entry available 82 min
  - 2025-04-15T06:59:00Z A LONG ref 85410 stop 85357.7 target 85773.5 (LANDMARK) → TARGET_REACHED (CERTIFIED_TARGET_CONTACT:okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-04-15T07:23:00Z) · entry available 2 min
- Adviser conclusion: **REPORTED_FOR_DIRECTOR_REVIEW** — v0.7 results are reported for Director diagnosis; no registered evidence criterion applies. v0.7 changes the explanation and the market reading only (an A condition that would already reach its destination is not counted as directional support); calls, entries, selection and terminals are those of v0.6, so a v0.6/v0.7 comparison on the same pack must show identical calls.

### Launch pins
- Method v0.7 `btc.context-action.v0.7` / `tdc.rules.v0.7` · rules `1f3704f4453b` · register `8525ec74e2cc` · implementation adviser.core.v7 · identity `c7d07273b47c` · build `13268640168468c6b30a42140a1e2b81582de2df`
- Profile `7c86833734da` · clock temporal.clock.modeled-complete-prefix.v1 · evaluator algotrader.adviser-evaluation.v1 `85504d5843e1` · PRIMARY entry delay 60 s · fee/leg 0.0005 · allowance/leg 0.0002 · funding PRICE_NET_ONLY
- Pack `pack-ec195b0b4bee44ee5d9c3c564ab8aa9631ed8fd4` · initialization from 2024-11-27T00:00:00+00:00 (not evaluated) · evaluation 2025-01-01T00:00:00+00:00 → 2025-05-01T00:00:00+00:00 · tail end 2025-05-01T06:05:00+00:00

### Context at the evaluation start (initialization is not evaluated)
- Initialization 2024-11-27T00:00:00+00:00 → 2025-01-01T00:00:00+00:00 (840 h, REGISTERED_EXPLICIT_INITIALIZATION) · trade coverage complete · trade_bar_1m 50400/50400; mark_bar_1m 50400/50400; index_bar_1m 50400/50400
- Readiness at start: {'trade.15m': 'READY', 'trade.1h': 'READY', 'trade.1m': 'READY'}
  - previous_day [2024-12-31T00:00:00+00:00, 2025-01-01T00:00:00+00:00): COVERED
  - previous_week [2024-12-23T00:00:00+00:00, 2024-12-30T00:00:00+00:00): COVERED
  - previous_month [2024-12-01T00:00:00+00:00, 2025-01-01T00:00:00+00:00): COVERED
  - pivot_15m_memory [2024-12-31T00:00:00+00:00, 2025-01-01T00:00:00+00:00): COVERED
  - pivot_1h_memory [2024-12-25T00:00:00+00:00, 2025-01-01T00:00:00+00:00): COVERED
  - PREV_1D_HIGH: BUILT_ACTIVE
  - PREV_1D_LOW: BUILT_ACTIVE
  - PREV_1W_HIGH: BUILT_ACTIVE
  - PREV_1W_LOW: BUILT_THEN_BROKEN (15M_CLOSE_BEYOND_FAR_EDGE:okx/BTC-USDT-SWAP/trade_bar_1m/15m/2024-12-30T14:30:00+00:00)
  - PREV_1MO_HIGH: BUILT_ACTIVE
  - PREV_1MO_LOW: BUILT_ACTIVE
  - PIVOTS_15M: BUILT · ever built 891 · active 13 · memory window COVERED · completeness NOT_CERTIFIED
  - PIVOTS_1H: BUILT · ever built 238 · active 8 · memory window COVERED · completeness NOT_CERTIFIED
- Facts at the evaluation start (records published at that dispatch included). 'Never built' and 'insufficient data' are kept apart from levels built and then legitimately broken, expired or retired. Pivot memory completeness is NOT certified: formation, publication, breaking, retirement and the per-horizon cap are not reconstructed. The initialization is never evaluated.

### Continuous run: total and monthly sections (one run, no monthly reset)
- Attribution: calls -> month of issue, followed to their outcome after the month ends (never counted twice); confirmations/scenario transitions -> month of publication; WAITs -> month opened, with their ending wherever it falls; coverage -> minutes inside the month; view samples -> sample time (their 1h/4h endpoint may fall in the next month)
- each section uses its own denominator: evaluation minutes, view samples, A confirmations, opened WAITs and issued calls are different populations
- Hypothetical sums: sum of normalized one-unit hypothetical price-net outcomes (N0=1, q=1/E): not an account return, not compounded, no sizing; funding not covered (PRICE_NET_ONLY)
- paths still open at the clock end are CENSORED/UNRESOLVED and kept visible; tail data are never scored
| Period | Assessable min | A conf. | WAIT | Calls | Resolved later | PRIMARY closed | PRIMARY price-net |
|---|---:|---:|---:|---:|---:|---:|---:|
| TOTAL | 172800/172800 | 88 | 58 | 4 | 0 | 3 | +0.096% over 3 closed |
| 2025-01 | 44640/44640 | 22 | 14 | 2 | 0 | 1 | -0.258% over 1 closed |
| 2025-02 | 40320/40320 | 15 | 9 | 1 | 0 | 1 | +0.049% over 1 closed |
| 2025-03 | 44640/44640 | 26 | 17 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-04 | 43200/43200 | 25 | 18 | 1 | 0 | 1 | +0.305% over 1 closed |

Hypothetical outcomes per variant (calls by month of issue; expected = evaluable calls for a pinned variant; 'not yet recorded' = expected pair without a terminal record, nothing inferred for it)
| Period | Variant | Expected | Records | Not yet recorded | CLOSED | with price-net | NO_ENTRY | CENSORED | UNRESOLVED | AMBIGUOUS | Exit after period | Price-net sum (population) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TOTAL | PRIMARY | 4 | 4 | 0 | 3 | 3 | 1 | 0 | 0 | 0 | 0 | +0.096% over 3 closed |
| TOTAL | ENTRY_DELAY_0 | 4 | 4 | 0 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | +0.597% over 4 closed |
| TOTAL | ENTRY_DELAY_120 | 4 | 4 | 0 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | -0.166% over 2 closed |
| TOTAL | HORIZON_ONLY | 4 | 4 | 0 | 3 | 3 | 1 | 0 | 0 | 0 | 0 | +1.352% over 3 closed |
| 2025-01 | PRIMARY | 2 | 2 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | -0.258% over 1 closed |
| 2025-01 | ENTRY_DELAY_0 | 2 | 2 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | +0.224% over 2 closed |
| 2025-01 | ENTRY_DELAY_120 | 2 | 2 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | -0.258% over 1 closed |
| 2025-01 | HORIZON_ONLY | 2 | 2 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | +1.006% over 1 closed |
| 2025-02 | PRIMARY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.049% over 1 closed |
| 2025-02 | ENTRY_DELAY_0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.087% over 1 closed |
| 2025-02 | ENTRY_DELAY_120 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.092% over 1 closed |
| 2025-02 | HORIZON_ONLY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.049% over 1 closed |
| 2025-03 | PRIMARY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-03 | ENTRY_DELAY_0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-03 | ENTRY_DELAY_120 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-03 | HORIZON_ONLY | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-04 | PRIMARY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.305% over 1 closed |
| 2025-04 | ENTRY_DELAY_0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.285% over 1 closed |
| 2025-04 | ENTRY_DELAY_120 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | none observed (0 closed) |
| 2025-04 | HORIZON_ONLY | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | +0.296% over 1 closed |
- TOTAL MarketView: covered 172800/172800 min · assessable 172800 · unavailable 0 · rows BALANCED_RANGE 37322, CONDITIONAL_SCENARIO 7745, NO_QUALIFIED_STRUCTURE 118134, WATCH_ONLY 9599
- TOTAL samples: 2880 (BALANCED 623, DOWN 61, UNCERTAIN 2104, UP 92) · 1h directional 72/153 matching sign, endpoint unavailable 0 · 4h directional 70/153 matching sign, endpoint unavailable 0
- TOTAL scenarios: A_ANCHOR_LOST 200, A_ARM 167, A_BIRTH 376, A_CONFIRM 88, A_OWNER_RELEASE 25, A_REARM 153, A_REVISE 25, A_TERMINAL 376, B_ARM 6, B_BIRTH 33, B_CONFIRM 5, B_TERMINAL 33, C_ARM 19, C_BIRTH 32, C_CONFIRM 16, C_TERMINAL 32 · A confirmations 88 · D 77 / N 14
- TOTAL calls: guidance {'INVALIDATED': 1, 'TARGET_REACHED': 2, 'TIME_EXPIRED': 1} · routing {'IMMEDIATE_ISSUED': 2, 'RETURN_WAIT': 58, 'TERMINAL:AT_OPPOSING_AREA': 11, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 13, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 4} · WAIT endings {'ISSUE': 1, 'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 3, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 17, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 6, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 18, 'TERMINAL:SCENARIO_TERMINAL': 13}
- 2025-01 MarketView: covered 44640/44640 min · assessable 44640 · unavailable 0 · rows BALANCED_RANGE 9016, CONDITIONAL_SCENARIO 2339, NO_QUALIFIED_STRUCTURE 30579, WATCH_ONLY 2706
- 2025-01 samples: 744 (BALANCED 146, DOWN 17, UNCERTAIN 552, UP 29) · 1h directional 21/46 matching sign, endpoint unavailable 0 · 4h directional 21/46 matching sign, endpoint unavailable 0
- 2025-01 scenarios: A_ANCHOR_LOST 47, A_ARM 47, A_BIRTH 103, A_CONFIRM 22, A_OWNER_RELEASE 6, A_REARM 34, A_REVISE 6, A_TERMINAL 103, B_ARM 2, B_BIRTH 12, B_CONFIRM 2, B_TERMINAL 12, C_ARM 8, C_BIRTH 12, C_CONFIRM 8, C_TERMINAL 12 · A confirmations 22 · D 20 / N 4
- 2025-01 calls: guidance {'INVALIDATED': 1, 'TARGET_REACHED': 1} · routing {'IMMEDIATE_ISSUED': 1, 'RETURN_WAIT': 14, 'TERMINAL:AT_OPPOSING_AREA': 2, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 4, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 1} · WAIT endings {'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 5, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 1, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 5, 'TERMINAL:SCENARIO_TERMINAL': 3}
- 2025-02 MarketView: covered 40320/40320 min · assessable 40320 · unavailable 0 · rows BALANCED_RANGE 9093, CONDITIONAL_SCENARIO 1139, NO_QUALIFIED_STRUCTURE 28410, WATCH_ONLY 1678
- 2025-02 samples: 672 (BALANCED 155, DOWN 14, UNCERTAIN 497, UP 6) · 1h directional 10/20 matching sign, endpoint unavailable 0 · 4h directional 5/20 matching sign, endpoint unavailable 0
- 2025-02 scenarios: A_ANCHOR_LOST 28, A_ARM 33, A_BIRTH 74, A_CONFIRM 15, A_OWNER_RELEASE 4, A_REARM 19, A_REVISE 6, A_TERMINAL 74, B_ARM 2, B_BIRTH 5, B_CONFIRM 1, B_TERMINAL 5, C_ARM 2, C_BIRTH 4, C_CONFIRM 1, C_TERMINAL 4 · A confirmations 15 · D 13 / N 2
- 2025-02 calls: guidance {'TIME_EXPIRED': 1} · routing {'IMMEDIATE_ISSUED': 1, 'RETURN_WAIT': 9, 'TERMINAL:AT_OPPOSING_AREA': 2, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 1, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 2} · WAIT endings {'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 1, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 1, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 2, 'TERMINAL:SCENARIO_TERMINAL': 5}
- 2025-03 MarketView: covered 44640/44640 min · assessable 44640 · unavailable 0 · rows BALANCED_RANGE 9831, CONDITIONAL_SCENARIO 2457, NO_QUALIFIED_STRUCTURE 29272, WATCH_ONLY 3080
- 2025-03 samples: 744 (BALANCED 172, DOWN 23, UNCERTAIN 522, UP 27) · 1h directional 25/50 matching sign, endpoint unavailable 0 · 4h directional 26/50 matching sign, endpoint unavailable 0
- 2025-03 scenarios: A_ANCHOR_LOST 79, A_ARM 52, A_BIRTH 111, A_CONFIRM 26, A_OWNER_RELEASE 8, A_REARM 62, A_REVISE 8, A_TERMINAL 111, B_ARM 1, B_BIRTH 11, B_CONFIRM 1, B_TERMINAL 11, C_ARM 6, C_BIRTH 9, C_CONFIRM 4, C_TERMINAL 9 · A confirmations 26 · D 24 / N 6
- 2025-03 calls: guidance {} · routing {'RETURN_WAIT': 17, 'TERMINAL:AT_OPPOSING_AREA': 2, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 6, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 1} · WAIT endings {'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 1, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 6, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 3, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 5, 'TERMINAL:SCENARIO_TERMINAL': 2}
- 2025-04 MarketView: covered 43200/43200 min · assessable 43200 · unavailable 0 · rows BALANCED_RANGE 9382, CONDITIONAL_SCENARIO 1810, NO_QUALIFIED_STRUCTURE 29873, WATCH_ONLY 2135
- 2025-04 samples: 720 (BALANCED 150, DOWN 7, UNCERTAIN 533, UP 30) · 1h directional 16/37 matching sign, endpoint unavailable 0 · 4h directional 18/37 matching sign, endpoint unavailable 0
- 2025-04 scenarios: A_ANCHOR_LOST 46, A_ARM 35, A_BIRTH 88, A_CONFIRM 25, A_OWNER_RELEASE 7, A_REARM 38, A_REVISE 5, A_TERMINAL 88, B_ARM 1, B_BIRTH 5, B_CONFIRM 1, B_TERMINAL 5, C_ARM 3, C_BIRTH 7, C_CONFIRM 3, C_TERMINAL 7 · A confirmations 25 · D 20 / N 2
- 2025-04 calls: guidance {'TARGET_REACHED': 1} · routing {'RETURN_WAIT': 18, 'TERMINAL:AT_OPPOSING_AREA': 5, 'TERMINAL:NO_ECONOMIC_RETURN_REGION': 2} · WAIT endings {'ISSUE': 1, 'TERMINAL:CONTEXT_FORBIDDEN_PREISSUE': 2, 'TERMINAL:INITIAL_RESPONSE_INCOMPATIBLE': 5, 'TERMINAL:ORIGINAL_SETUP_DEADLINE': 1, 'TERMINAL:PRE_ENTRY_TARGET_CONTACT': 6, 'TERMINAL:SCENARIO_TERMINAL': 3}
- Reconciliation total vs months: PASS (arithmetic of the available records only; it is not outcome completeness)
- Path records: 16 available · 16 admitted · 0 expected missing · 0 extraneous · 0 duplicates
- Outcome completeness: COMPLETE — 16/16 expected call–variant terminal records available · run status completed

### A RETURN response (MP-004 §7 with MP-005 §6; unit = A RETURN child)
- W A RETURN children routed to WAIT_RETURN · P local references prepared · C ended by a local contradiction before any recovery · R first decisive recoveries observed · N first recoveries not issuable · I calls issued · X other endings after the reference · A still waiting for the response at the report cutoff
- Cutoff 2025-05-01T06:05:00+00:00: A = waits still open at the last committed record
- Identities P = C + R + X + A, R = N + I, W = P + endings before a reference + WAIT_RETURN open; a zero denominator is undefined.

| Period | W | P | C | R | N | I | X | A | P/W | C/P | R/P | N/R | I/R | I/P | Identities |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Total | 58 | 18 | 0 | 1 | 0 | 1 | 17 | 0 | 0.3103 | 0.0000 | 0.0556 | 0.0000 | 1.0000 | 0.0556 | yes |
| 2025-01 | 14 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0.3571 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
| 2025-02 | 9 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0.1111 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
| 2025-03 | 17 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | 0.3529 | 0.0000 | 0.0000 | undef. | undef. | 0.0000 | yes |
| 2025-04 | 18 | 6 | 0 | 1 | 0 | 1 | 5 | 0 | 0.3333 | 0.0000 | 0.1667 | 0.0000 | 1.0000 | 0.1667 | yes |
- LONG: W 38 · P 12 · C 0 · R 1 · N 0 · I 1 · X 11 · A 0
- SHORT: W 20 · P 6 · C 0 · R 0 · N 0 · I 0 · X 6 · A 0
- Ended before a reference: {'CONTEXT_FORBIDDEN_PREISSUE': 3, 'ORIGINAL_SETUP_DEADLINE': 6, 'PRE_ENTRY_TARGET_CONTACT': 18, 'SCENARIO_TERMINAL': 13} · WAIT_RETURN still open 0
- N primary reason: {} · by class {} · late first recovery 0 · blocker incidence (not summable) {}
- X by priority cause: {'INITIAL_RESPONSE_INCOMPATIBLE': 17}
- Months (child -> calendar month in which its WAIT opened, followed to its ending wherever it falls (never counted twice); no reset at a month boundary): sum to total yes · identities in every month yes
- Warmup (not evaluated): 19 child(ren); cleared at the evaluation start {}; other warmup endings 19
- Cross-checks with the report funnel: W_equals_waits_opened yes · I_equals_A_RETURN_calls_in_window yes
- C/P does not measure real deterioration and R/P does not measure continuation quality; outcomes and later entries belong to the separate economic report. No frequency or profit quota.

#### Initial response incompatibility (MP-005 §6; subset of X)
| Period | INITIAL_RESPONSE_INCOMPATIBLE | base CORRIDOR | base HISTORICAL_ECONOMICS | X | P | ratio over P | subset of X |
|---|---|---|---|---|---|---|---|
| Total | 17 | 3 | 14 | 17 | 18 | 0.9444 | yes |
| 2025-01 | 5 | 2 | 3 | 5 | 5 | 1.0000 | yes |
| 2025-02 | 1 | 1 | 0 | 1 | 1 | 1.0000 | yes |
| 2025-03 | 6 | 0 | 6 | 6 | 6 | 1.0000 | yes |
| 2025-04 | 5 | 0 | 5 | 5 | 6 | 0.8333 | yes |
- By direction: {'LONG': 11, 'SHORT': 6} · concurrent annotations (never a second terminal): {'HISTORICAL_ECONOMICS': 3}
  - LONG AL-2025-01-01T15:45:00+00:00-ed49e6f73656#entry: reference okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-01-01T17:04:00Z H0 94080 L0 94020 · F >= 94080.1 · C0 93936.7..94121.4 · A0 93936.7..94024.0 · F∩C0 94080.1..94121.4 · J0 ∅ → HISTORICAL_ECONOMICS
  - SHORT AS-2025-01-07T11:45:00+00:00-6a44f587a828#entry: reference okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-01-07T13:26:00Z H0 100955.8 L0 100923 · F <= 100922.9 · C0 100726.9..100992 · A0 100926.2..100992 · F∩C0 100726.9..100922.9 · J0 ∅ → HISTORICAL_ECONOMICS
  - LONG AL-2025-01-10T07:30:00+00:00-496c0bfa6955#entry: reference okx/BTC-USDT-SWAP/trade_bar_1m#obs@2025-01-10T08:38:00Z H0 94538.1 L0 94469.6 · F >= 94538.2 · C0 94380.4..94729.9 · A0 94380.4..94487.6 · F∩C0 94538.2..94729.9 · J0 ∅ → HISTORICAL_ECONOMICS
- INITIAL_RESPONSE_INCOMPATIBLE is a subset of X (never added a second time): P = C + R + X + A still holds; ratio over P, a zero denominator is undefined.
- An INITIAL_RESPONSE_INCOMPATIBLE ending terminates the entry attempt only; the structural scenario is not invalidated and keeps its own lifecycle.
- Declared information loss (MP-005 §6): a child ended INITIAL_RESPONSE_INCOMPATIBLE at its preparation receives no later local classification (C or R) that it might have produced under MP-004 v0.5; no counterfactual classification is reconstructed. Changes of C/P or R/P between v0.5 and v0.6 therefore do not show a better local response.
- Months (WAIT-open cohort, no reset): initial incompatibility sums to total yes

#### Trigger/destination compatibility (published records only)
- Incompatible publications: 22 ({'ARM': 22}) · scenarios concerned: 22
- MarketView publications without support from an armed scenario: 19
- Support restored by a compatible revision: 0
- Counted from the published antecedents and MarketView records only. An incompatible condition would reach its destination before it could confirm; v0.7 states it and does not count the scenario as directional support. Calls, entries, selection and terminals are those of v0.6.
