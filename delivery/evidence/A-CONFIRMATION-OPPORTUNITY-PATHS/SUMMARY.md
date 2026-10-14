# From A confirmation to entry opportunity — v0.6, September–December 2025

**Executor delivery, 14 October 2026.** Astra's authorization, relayed by the Owner. The Director's review is separate and PENDING.
- **Nature.** A bounded reconstruction from records that already exist. No replay, extraction, acquisition, evaluator, alternative entry, a-posteriori better price, or judgement of a block by later B contacts.
- **Unchanged.** v0.6 is frozen; future studies stay INACTIVE.

**Question.** At confirmation, is there still room for an entry under the v0.6 policy, and how does the path toward issuance end?

## 1. Sources: reused and new

**Already tabulated, reused and reconciled.** The 89 first-attempt children and their **end reasons** (A2X comparison, `A2X-HISTORICAL-COMPARISON/SUMMARY.md`; the same journal); the revision chains (`A-REVISION-HISTORICAL-CHECK`); the one call. This reconstruction reproduces the earlier end-reason table exactly; the reconciliation check passes:
- 1 issued;
- 22 no economic region;
- 18 target contact before entry;
- 15 scenario destination;
- 9 + 3 initial response incompatible;
- 8 setup expiry;
- 7 opposing area;
- 4 context;
- 2 scenario invalidated.

**New processing, on the same records only.** [`paths.py`](paths.py) reads the 12 October v0.6 journal (SHA-256 = committed manifest) and links each confirmation to its child records in journal order:
- the routing record of the confirmation dispatch, with the levels and conditions at confirmation, diagnostics D/N and **every computed blocker**;
- the WAIT records: temporary blockers at each change, cap revisions, the RETURN reference, the MP-005 initial check;
- the end, with its reason, time, sequence and recorded blockers.

The routing precedence is the code's (`core3._route_a`): opposing area/no target → target reached by the confirming bar → unavailable geometry → non-selection gates → IMMEDIATE → non-routable immediate → empty corridor → no economic region → WAIT_RETURN. A check verifies every routing terminal against it.

## 2. Reconciled path: 89 confirmations → initial routes → waits/blocks → issuance or terminals

**Initial routes, at the confirmation dispatch** (89):

| Route | Count | Recorded reason (all blockers kept) |
|---|---|---|
| IMMEDIATE, issued | **1** | `call-AL-2025-10-26T23:34…`, no blocker |
| Child terminal **at confirmation** | **31** | 22 `NO_ECONOMIC_RETURN_REGION` (blockers also recorded: 20 `NO_ROOM_AFTER_COSTS`, 4 `REWARD_RISK_BELOW_MINIMUM`); 7 `AT_OPPOSING_AREA` (target inside an opposing area); 2 `PRE_ENTRY_TARGET_CONTACT` (the confirming bar already reached the target; `NO_ROOM_AFTER_COSTS` also recorded) |
| RETURN wait opened (`IMMEDIATE_ECONOMIC_FAILURE_RETURN_CORRIDOR_USABLE`) | **57** | the immediate entry failed on cost/geometry: 45 `REWARD_RISK_BELOW_MINIMUM`, 12 `NO_ROOM_AFTER_COSTS` |

- **Room for an immediate entry at confirmation** existed in **1 of 89** cases.
- **Diagnostic at confirmation:** 82 in D, 7 excluded inside an opposing zone. Of the 82, 24 were in N: an empty corridor or economic region at the fixed historical cost.

**The 57 waits (temporary blocks).**
- **Blockers seen** at any time: `CLOSE_OUTSIDE_RETURN_CORRIDOR` in 50, `REWARD_RISK_BELOW_MINIMUM` in 50, `NO_ROOM_AFTER_COSTS` in 39, `BLOCKED_BY_ZONE` in 1. No selection or non-selection gate ever appeared while waiting.
- **Timing.** Median time from confirmation to the end of the child: 15 minutes.
- **A usable return occurred in only 12 waits.** It prepared the RETURN reference, and in **all 12** the MP-005 initial check ended the child **in the same dispatch**: 9 historical economics, 3 corridor. No local response was ever observed, and no recovery reached the issuance gates or selection.

**Ends, in the four requested categories:**

| Category | Sub-class (source: child record reason + recorded blockers) | Count |
|---|---|---|
| **ISSUED** | IMMEDIATE at confirmation | **1** |
| **1. Incompatibility already present at confirmation** | COST: no economic return region at the fixed historical cost | 22 |
| | GEOMETRY: target inside an opposing area | 7 |
| | GEOMETRY: target already reached by the confirming bar | 2 |
| **2. Temporary restriction still active when the child's timer ran out** | TIMER: original setup expiry while blocked. Last blockers: `REWARD_RISK_BELOW_MINIMUM` 4; `CLOSE_OUTSIDE_RETURN_CORRIDOR`+`REWARD_RISK_BELOW_MINIMUM` 2; `CLOSE_OUTSIDE_RETURN_CORRIDOR`+`NO_ROOM_AFTER_COSTS` 2 | 8 |
| **3. Unavailability arising during the wait** | NEW PRICE EVIDENCE: the target or cap was reached before any entry | 16 |
| | COST: the prepared RETURN reference was incompatible with the economic region (MP-005) | 9 |
| | GEOMETRY: the prepared reference was incompatible with the corridor (MP-005) | 3 |
| | CONTEXT: withdrawn before issue | 4 |
| **4. Scenario terminal that also closed the child** | scenario DESTINATION_REACHED while waiting | 15 |
| | scenario INVALIDATED (V) while waiting | 2 |
| **Total** | | **89** |

- **Category 4.** In 16 of the 17 scenario terminals, the waiting child was still blocked by `CLOSE_OUTSIDE_RETURN_CORRIDOR` and/or `NO_ROOM_AFTER_COSTS` (14 both), as recorded before the terminal. A child closed by a scenario terminal is never relabelled as a cost or geometry end.
- **Not observed among the 89:** selection or conflict blocks (slot, conflict, priority), non-selection gates, ambiguity or data loss.

Per-scenario detail: [`out/paths.csv`](out/paths.csv), one row per scenario. It carries the levels at confirmation (close, T, V, K, R, I0, corridor, economic region, K_cost, G/Q/margin, D/N), the route, every routing blocker, the waits (changes, caps, blockers seen, last blockers), the reference, the end (transition, reason, time, seq, recorded blockers), the category, the scenario terminal and the call. Every child record in order: [`out/sequences.json`](out/sequences.json). Checks and tables: [`out/results.json`](out/results.json).

## 3. Conclusion

**The records support a recurring tension between confirmation and practicability under the v0.6 entry policy in this period:**
- Only **1 of 89** confirmations had an immediately admissible entry at the confirmation close.
- **31** ended at confirmation on an incompatibility already present: 22 cost, 9 target geometry.
- The remaining **57** waited for a return under cost/geometry blockers. **None** reached issuance:
  - 12 reached a usable return, and all were found incompatible at reference preparation;
  - the others ended by the target being reached first (16), timer expiry under blockers (8), context (4) or the scenario's own terminal (17).
- The dominant recorded constraints are the reward/risk minimum and room after the fixed costs at the confirmation or return price, together with closes outside the return corridor. They are not selection, conflict or data problems.

**What this does not establish.** A directional confirmation does not automatically promise a usable entry, and here it rarely did. This is a description of v0.6 rules on one exposed development period, with dependent observations. It does **not** show:
- that the blocks were wrong;
- that another entry, price or cost would have done better;
- anything about later B contacts as a justification.

The scenario-terminal and target-contact ends are the engine's own records, not judgements of missed value.

## 4. Checks and reproducibility

- **Checks: 6/6:**
  - 89 rows, one per scenario;
  - every child linked, with its first record in the confirmation dispatch;
  - no child record before the confirmation;
  - exactly one end per child;
  - every end classified;
  - routing reasons follow the code precedence.
- **Reconciliations: 5/5:**
  - routes and categories sum to 89;
  - wait ends sum to 57;
  - issued = calls;
  - end reasons = the earlier tabulation.
- **Reproducibility.** Two runs give identical hashes:
  - `results.json` `80239aac…8b6c`;
  - `paths.csv` `77000fcd…5f0b`;
  - `sequences.json` `77584d45…bd1a`.
- **No essential information was missing.** Every end has its contemporaneous record and blockers. For scenario terminals, the child's terminal record carries no blockers of its own; the last blockers recorded before it are reported as such.

**Not run:** product suites and CI (PENDING / NOT CHECKED).
