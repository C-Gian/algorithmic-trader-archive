# Descriptive historical comparison v0.6 / v0.6-a2x, September–December 2025 — design registered before execution

**Registered by the executor on 13 October 2026, base `5b7f00eae0f94be599acf819f39618e1b4c7df4d`, before either engine processing.**
- At this commit no processing of this comparison has run. No variant record on real data exists or has been consulted.
- The only data read so far is the input re-verification of §1, which reads event families, kinds and times only.
- **Authority.** Astra accepted the technical closure at `5b7f00e` and authorized this comparison, relayed by the Owner on 13 October 2026. The assignment is descriptive only: no economic evaluation.
- **Unchanged.** Product, v0.6 and HDP-001 stay frozen. The future studies stay INACTIVE. The variant stays EXPERIMENTAL: not installed or selectable.
- **Review.** Executor delivery; the Director's review is pending.

## 1. Inputs (re-verified; no new copy)

- **Copy reused.** The copy verified on 12 October for the A reaction E exploration: the pack manifest and the feed cache only, made under Astra's bounded derogation (exposure register row 11). It is kept outside Git in that session's scratchpad (`…/0d87e1fc-…/scratchpad/inputs/data`).
- **Not done.** No new copy from the Owner volume, no acquisition, no Owner-stack access.
- **Re-verified now.** [`verify_inputs.py`](verify_inputs.py) is the 12 October script with unchanged logic. It wrote [`inputs_verification.json`](inputs_verification.json): **21/21 checks pass**.

| Item | Value |
|---|---|
| Pack | `pack-1ae7d36c20adbde0a468a7e0f6d8750a9951aa8e`, manifest sha256 `1bec1f1575306d4444969569675e28bfdc9dac60e2d6f461b283871362221f92` |
| Feed cache | `fc-80221b24abf3a50b764cc873f4a70cc709847a6b`, manifest sha256 `95478a50a732dffe5d8c46a6b1ca23288246a3ce01aaf537f0b64e2e7cef76fa`, 679,335 events |
| Feed | content `feedcontent.v1:f2cf8790…f028`; ordered-event hash recomputed and equal; availability `feed.modeled.v1(bar+PT0S,funding+PT0S)` |
| Windows | initialization [2025-07-28, 2025-09-01); evaluation [2025-09-01, 2026-01-01); authorized tail [2026-01-01T00:00Z, 06:05Z) |
| Coverage | trade, mark and index 1m complete in each window, 0 missing, no gap or quality event |

## 2. Engines, rules, registers, scripts

**Policies.** Both use the same build, flow, availability, initialization, windows and clock end. The only difference is the method.

| Policy | Model / rules | Implementation / runtime / engine | Rules sha256 | Register sha256 |
|---|---|---|---|---|
| v0.6 (frozen) | `btc.context-action.v0.6` / `mp005.rules.v0.6` | `adviser.core.v6` / `algotrader.adviser-runtime.v6` / `observe.stream.v7` | `57bf2309…2e66` | `98ef101e…5bda` |
| v0.6-a2x (EXPERIMENTAL) | `btc.context-action.v0.6-a2x` / `a2x.rules.exp1` | `adviser.core.v6-a2x` / `algotrader.adviser-runtime.v6-a2x` / `observe.stream.v7-a2x` | `08e3c268…74e7` | `b4782f7d…1126` |

**Build.**
- The commit holding this registration. Its product tree is identical to `5b7f00e`: `git diff 5b7f00e -- src` is empty.
- The build string pinned in the engine and records is that commit's SHA.

**Construction.** As the app's evaluation job and the 12 October runner: `temporal_config` with the MP-001 dependencies, then `engine_config(fm, pack, build, method)`, then `config_from_engine`, one `Kernel` applying every canonical line, then `finish(2026-01-01T06:05Z)`.
- **Everything ordinary is active:** A/B/C, joint selection, slot, conflicts and protections.
- **No evaluator** (runtime evaluator `None`).
- **The variant** is selected only by `experimental=True` in this offline script.

**Baseline reuse decision (rule fixed here).**
- The existing v0.6 journal (12 October, build `6a0f22a`, journal sha256 `ea3ce997…f0af0`) is complete: 679,335 events, finish 06:05Z, rules and register equal.
- It is **not sufficient for this comparison**. It was produced by a different engine build, and the v0.6 code path changed since then (`core3` hooks `_conf_clocks` and `_a_hard`, engine/harness selection).
- It also lacks the complete source lists (records carry only the last three of seven) and the birth-step state that the registered matching and attribution need.
- Therefore the **single authorized v0.6 processing** is run at the same build as the variant.
- The old journal is used only as a cross-check ([`crosscheck_baseline.py`](crosscheck_baseline.py)). After removing `env.method.build` and the record digest and chain, the new v0.6 records must equal it record by record. A difference is reported, not resolved.

**Passive trace ([`instrument.py`](instrument.py)), installed on the core instance in both runs.**
- Wrappers call the original methods with the same arguments and return their results unchanged.
- At each scenario's first record they capture the frozen facts held by the core: family, direction, the **complete ordered source list**, S15, zone, impulse A/B, attempt/impulse, and the box geometry.
- At each birth step they capture every Q_A with the direction's latch and discovery owner, read before the latch update.
- In the variant they also capture every deferral of an ordinary birth: direction, reserving token, impulse and source close.
- The self-test proves the instrumented journals digest-identical to uninstrumented harness runs. The v0.6 cross-check above repeats this on the pack.

| Script | sha256 at registration |
|---|---|
| `verify_inputs.py` | `97a4bd50e69e4af5fa82140a8e11c8ae197809c36a52bf128f9992081ac38863` |
| `instrument.py` | `17c30b24feed6a4e1a95a3614cdd457309c8cfecd21757a7649d488ac055fcd8` |
| `run_offline.py` | `4f9f54d6fcf84a1ec58da64482b3dad74fc0b7fe7a24f93ec95fd221067559bf` |
| `compare.py` | `0b7f00b2e3aad36f2bd0855544e1fd4910196a507d0ccddccbe6d9eec929772c` |
| `crosscheck_baseline.py` | `82cf3d3638d555adaf480d0e7a8500623030dc48b670b19f1b8447d55c0d6221` |
| `inputs_verification.json` (output of §1) | `fce0ef7cb74c9023fbd7a98f5d6c63952de159b32d78939759e91fcecc484780` |

Hashes are of the LF bytes as committed. A Windows checkout may present CRLF.

`compare.py --selftest` passes **21/21** before registration, on synthetic tapes through the harness, LONG and SHORT:
- instrumentation is passive;
- a successor is added and linked to its matched impulse;
- a deferred ordinary birth is linked by record, with the next birth not claimed as the same impulse;
- a review not opened;
- id normalization, reason codes, and a non-unique key that matches nothing.

**Processing.**
- One run per policy: `run_offline.py <data_root> <out> <build> v0.6`, then `… v0.6-a2x`. The runner refuses a second run into the same output.
- Outputs `journal.jsonl.gz` and `trace.jsonl.gz` stay outside Git. Their sha256 go in the committed `run_manifest_<method>.json`.
- No parameter or script changes after results. Any later change is appended below as an amendment, stating whether results had been seen.

## 3. Population, windows, warmup

- **Population.** Every A impulse whose BIRTH record falls in [2025-09-01T00:00Z, 2026-01-01T00:00Z), separately in each policy.
  - A **successor** (`setup.attempt` "2") is not a birth. It is an attempt of its impulse, reached through lineage.
  - B and C births are tabulated the same way.
- **Warmup.**
  - Scenarios born before 2025-09-01 are reported **separately**, with the same tables: births, flow, reviews and successors during the initialization.
  - They are not part of the population.
  - Divergences during or caused in the warmup are dated and visible.
- **Tail.** No birth can occur in the tail (TAIL window). A tail birth fails a check.
- **Boundaries.** The window is decided by the BIRTH record's clock time. Later records of a population scenario are followed to its last record, tail included.

## 4. Counts (per policy, evaluation and warmup separately)

**Flow of A first attempts:**
- impulses → never armed / armed not confirmed / confirmed, each by terminal state:code;
- confirmed → terminal by state:code;
- V failures after confirmation (TERMINAL INVALIDATED, code V_CONTACT);
- in the variant: admissible (REVIEW_OPEN) / excluded (REVIEW_NOT_OPENED by reason);
- reviews → closed without successor (state:code), or successor armed;
- successors → not confirmed (terminal state:code, including the recorded insufficient-residual exclusions) / confirmed (terminal);
- confirmations of first attempts and of successors **separately** → child: issued (call) / not issued (child terminal code) / open at end.

v0.6 shows its V failures with "not applicable" for admissibility.

**Rules for reading the counts:**
- Reason code = the leading upper-case segments of the reason (ids, bars and levels removed).
- A **published call is not an executed entry.** No call outcome, path or P&L is tabulated.
- Every table states its reconciliation identities, and they are checked.

## 5. Matching and attribution (fixed before any result)

**Primary key, from the trace facts at the scenario's first record:**
- **A:** direction + the complete ordered source list + original impulse A and B + birth S15 + zone.
- **B/C:** family + direction + complete ordered sources + S15 + zone + box low/up/mid.

**Rules:**
- Identifiers, time proximity and outcomes are **never** evidence of identity.
- Only the rules-identity suffix of ids (12 hex) is normalized, and only to compare record content.
- A match must be **one-to-one**. A key held by more than one scenario in either policy matches nothing; those episodes stay distinct (NON_UNIQUE). A scenario without trace facts has no key.

**Divergence register:**
1. **Common events.** Matched scenarios whose whole chain is identical: scenario, child, calls and revisions, with envelopes removed except the clock time and ids normalized. Otherwise MATCHED_CHAIN_DIFFERS, with the first differing record of each side.
2. **Variant review records,** per impulse through `values.impulse_id`: REVIEW_NOT_OPENED (reason), REVIEW_CLOSED_WITHOUT_SUCCESSOR (state:reason), SUCCESSOR_ADDED (successor id from SUCCESSOR_ARMED). A successor is linked to its impulse by lineage only: `setup.impulse_id` = `setup.parent_scenario_id` = `env.lineage[1]` = the trace impulse. It is checked against the review records.
3. **Unmatched births,** each with the **other policy's traced birth-step state at the same dispatch and direction**:
   - **SLOT_RESERVED_BY_SECOND_ATTEMPT**: the other side's owner is a review token or a successor; its impulse is named and its match status given.
   - **SLOT_OCCUPIED_BY_ORDINARY_SCENARIO**: the occupant, its birth and match status.
   - **LATCH_NOT_READY**: NEED_FALSE with no owner, plus the last traced owner before it.
   - **QA_DIFFERS** or **UNEXPLAINED**, reported as such.
   - **NO_QA_TRACE.**

   A v0.6 birth absent from the variant is **BIRTH_DEFERRED only with a demonstrated link**: a variant deferral in the same direction at the same 15m source close as the v0.6 birth's last source.
   - **RECORD**: the published `ORDINARY_BIRTH_DEFERRED` observation (published once per reservation).
   - **TRACE**: the registered deferral trace only.
   - Otherwise it stays **BIRTH_ONLY_IN_V06**. The next same-direction variant birth is reported, with whether it is itself matched; it is **never claimed to be the same impulse**.
   - Causes after a divergence are taken from the state at each dispatch. A difference is not attributed to the reservation unless the slot was held by a review or successor there. An occupant that is itself an unmatched ordinary scenario is named as such (a cascade).
4. **Calls in one policy only.** The call key is the scenario key, or "successor of the impulse key", plus the issue time. The scenario and attempt are given.
5. **B/C and other records.** B/C matched or unmatched, and chain differences, are observed without any diagnosis of their rules. Views, landmarks, material changes and ordinary observations in the evaluation window get one-sided counts and the first time of difference.

## 6. Illustrative sequences (criterion fixed now)

- **Selection.** For each divergence type, only the **first chronological occurrence**, by the time of its first divergent record.
- **Content.** The records of the scenarios involved in both policies, up to those scenarios' own last records: the matched counterparts, the impulse of a successor, and the occupant or reserving impulse.
- **Excluded.** No choice by outcome, no other examples, no search for later recoveries.

## 7. Checks

- Both runs applied 679,335 events and finished at 2026-01-01T06:05Z, with equal input and temporal commitments (the same market flow).
- The trace facts are consistent with every first record (last three sources, A/B, S15, zone, first transition), and trace scenario ids equal journal scenario ids.
- There is one traced birth step per 15m close of the evaluation window, per direction.
- v0.6 has no variant record.
- Lineage and review consistency, at most one successor per impulse, and every V failure with a review record in the variant.
- Matching is one-to-one, with the counts of matched, unmatched, non-unique and keyless births reconciled to the births of each policy.
- Flow reconciliations; the v0.6 cross-check against the 12 October journal.
- **Reproducibility.** The tabulation runs twice from the saved journals and traces only, without the engine, with identical output hashes.

## 8. Limits declared in advance

- **Prior exposure.** September–December 2025 is exposed development data (register rows 1–5 and 11–13), including the v0.6 processing of this pack. This is a description, not a test.
- **Excluded.** No economic or call outcome, no tuning, no minimum number of calls; more calls do not mean improvement.
- **Attribution.**
  - Attribution uses the registered state trace where records are silent. A trace-only link is labelled TRACE.
  - Differences after a first divergence can have several concurrent causes.
- **Exposure and provenance.** Recorded in the exposure register at delivery.

## Amendments

1. **`crosscheck_baseline.py`, 13 October 2026, after both engine processings and before any tabulation.**
   - **Defect.** The first cross-check stopped at entry 19,673, the one v0.6 call record. The only differing field was `record.actionability.env.method.build`: a call carries a nested envelope with the build, which the script did not remove.
   - **Change.** The script now removes the `build` of every envelope's `method`, nested ones included. Nothing else changed.
   - **Result.** 34,507 entries identical.
   - **What had been seen.** Only that difference report: no comparison result, variant record or tabulation.
   - **New sha256:** `6f212b6ecf62d8a289482a3fc4c362a341ba95034e8ec8a5c9488aa78b109927`.
2. **`post_hoc.py`, 13 October 2026, AFTER the registered tabulation had been seen.**
   - **Why.** That tabulation showed two effects it does not characterize: 40 market-view dispatches that differ, and no birth difference at all.
   - **What it adds.** Post-hoc descriptions only, from the saved journals and traces:
     - whether each differing view dispatch lies inside a variant reservation interval, and which view fields differ;
     - at which 15m closes the two policies' traced latch or slot state differs, and whether Q_A was true there.
   - **Status.** It is not part of the registered design, changes no registered output, and is labelled post-hoc wherever it is cited.
   - **sha256:** `fcec466289fd6a3b4e2c7bbd528509684c7f846124b3070408f5ef8d23b46d41`.
