# A revisions — registration before tabulation

**Executor registration, 14 October 2026.** Committed **before** any tabulation of outcomes; the classifier has run only on synthetic cases.
- **Authorization.** Astra authorized registration and one single descriptive tabulation, relayed by the Owner on 14 October 2026.
- **Design reference.** [A-REVISION-HISTORICAL-CHECK-PROPOSAL.md](../../A-REVISION-HISTORICAL-CHECK-PROPOSAL.md) at `91578fc`. Where the authorization is more precise, it prevails.
- **Nature.** A description of how v0.6 updated its published A formulations, on exposed development data.
- **Not:** a forecast evaluation, an economic evaluation, a v0.7 evaluation, or a comparison against a no-revision policy.
- **Unchanged.** v0.6 and HDP-001 are frozen; future studies stay INACTIVE.

## 0. What is already known (not a preregistration on unseen data)

**Earlier studies on the same artifacts.** Their results are already known:
- E exploration (`A-REACTION-EFFICIENCY-EXPLORATION`);
- v0.6 / v0.6-a2x comparison (`A2X-HISTORICAL-COMPARISON`);
- v0.6 A/B/C expectation check (`V06-EXPECTATION-HISTORICAL-CHECK`). Among its A results: 161 first-ARM expectations, 28 original antecedents activated, 89 engine confirmations (28 on the original levels and time, 61 on revised levels), and 179 ANCHOR_LOST / 143 REARM / 22 REVISE after the cutoff.

**Seen by the executor while preparing this registration, on the whole journal including warmup:**
- A scenario record counts by transition: BIRTH 465, TERMINAL 465, ANCHOR_LOST 230, ARM 206, REARM 180, CONFIRM 113, OWNER_RELEASE 41, REVISE 31;
- A terminal-reason counts;
- every ANCHOR_LOST is an INVALIDATED `V_CONTACT` (none ambiguous);
- REVISE always has `LOWER_CLEAN_REACTION_REANCHOR`;
- one call in the whole journal;
- the first ARM of the first warmup scenario has K equal to B.

No per-formulation, per-segment or confirmed-group outcome of this design was computed or seen.

## 1. Question

How does the published A thesis evolve through revisions, and which formulation is actually confirmed? What follows that confirmed formulation within the scenario's actual life?

## 2. Inputs (local, outside the Owner stack; no replay, extraction or acquisition)

| Artifact | SHA-256 | Identity |
|---|---|---|
| `journal.jsonl.gz` (12 October 2026 offline v0.6 processing) | `ea3ce99757af41c96fa154f745e06d29c8a1906508089c7e43a051b2899af0f0` | 34,507 entries, last chain `83c04c2f…551d`, pack `pack-1ae7d36c…`, clock end 2026-01-01T06:05Z |
| `trade_bars.csv.gz` (admitted trade 1m bars of the same processing) | `06a1102470dd139a1a4a079220725aabb8fe890cc321df1c517ca8941c745abe` | 226,445 bars 2025-07-28T00:00Z → 2026-01-01T06:04Z, 0 missing |

- **Manifest.** Both hashes, counts and kinds equal the committed manifest `A-REACTION-EFFICIENCY-EXPLORATION/run_manifest.json`.
- **Identity on every record.** `adviser.core.v6`, rules `57bf2309…2e66`, register `98ef101e…5bda`.
- **Re-verification.** [`verify_inputs.py`](verify_inputs.py) → [`inputs_verification.json`](inputs_verification.json): **6/6**.
- **Local path.** `…\0d87e1fc-…\scratchpad\run`.

**Scripts at registration** (SHA-256 of the committed LF bytes):
- `revisions.py`: `9bdf912d3b876fcf98ceff7cf5d72eb120ed6854e0b05c4ca930608760762719`;
- `verify_inputs.py`: `b24df8c1fe3d98ca2e1e6b3783ab592e38fa3ef64c0c899698ad81495c12659a`.

**Fixed parameters:**
- **Tick 0.1.** The manifest pin.
- **`trigger_offset_ticks` 1.** From the v0.6 register; every antecedent text is checked against it.

## 3. Population and unit

- **Population:** every A scenario, LONG and SHORT, whose BIRTH record has a publication `clock_time` in [2025-09-01T00:00Z, 2026-01-01T00:00Z).
  - It includes never-armed and never-confirmed scenarios.
  - Warmup births (before 2025-09-01) are tabulated separately.
  - A tail birth fails a check.
- **Unit.** One scenario is one summary row, linked to its complete ordered sequence. Formulations and gaps are descriptive segments; they are reported as "publications, not independent scenarios".

## 4. Reconstruction (journal-first; bars only corroborate)

**Chain.** The scenario's own records, ordered by journal sequence, never by market time alone:
- BIRTH → ARM → any REVISE / ANCHOR_LOST (→ WATCH) / REARM → at most one CONFIRM → TERMINAL;
- OWNER_RELEASE is an event that ends nothing.

**Formulation.** Each ARM, REVISE or REARM record is a new, immutable formulation, kept with its own data.
- *Levels:* K (`trigger_level`), R, V, B, T = K + tick × 1 in q = direction × price, premise and original expiry.
- *Observed moment:* the source 15m bar named by `anchor_source`.
- *Publication:* the record's `clock_time`, together with its admitted `factual_cursor` and journal sequence.

**Checks on every formulation** (otherwise linkage failure):
- publication at or after the end of its source bar;
- K = source high, R = source low and V = R − birth z, all in q;
- antecedent threshold = T and V;
- `anchor_published_at` and cursor equal to the envelope;
- epochs 1..n.

**Domain.**
- A formulation is active from its publication until its ending record.
- A new condition is valid only from its own publication: only a complete 1m interval with start at or after the publication can confirm it, so the source bar is never reused.
- Superseding records end the earlier formulation prospectively and never rewrite it.

**Ends of a formulation:**
- `CONFIRMED_ON_THIS_FORMULATION`: a CONFIRM on its own epoch. The confirming minute (from the record) must:
  - start at or after the publication;
  - end at or before the confirmation dispatch;
  - close at or beyond T and keep V;
  - equal the record's `confirmation_close`;
  - keep K, V and B unchanged.
- `SUPERSEDED_BY_REVISION`: a REVISE whose previous anchor is this epoch, status SUPERSEDED.
- `ANCHOR_LOST_CERTIFIED` / `ANCHOR_LOST_AMBIGUOUS`: an ANCHOR_LOST with anchor status INVALIDATED / UNASSESSABLE.
  - A certified contact needs its minute: starting inside the domain, admitted by the loss and reaching V.
  - This starts an **observation gap** (WATCH).
- A scenario TERMINAL while the formulation is active:
  - `DESTINATION_BEFORE_CONFIRMATION`: the minute must reach B and start at or after the first ARM;
  - `ORIGINAL_SETUP_EXPIRY`;
  - `STRUCTURAL_OR_CONTEXT_TERMINAL`: context or adverse-expansion withdrawal, A+z withdrawal, other expiry;
  - `AMBIGUOUS`;
  - `DATA_LOSS`;
  - `OPEN_AT_DATA_END`: no terminal by 2026-01-01T06:05Z.

**Ends of an observation gap:**
- `REARM`, with the previous anchor = the lost epoch;
- `DESTINATION_IN_OBSERVATION_GAP`: not a continuation following an activated condition;
- the terminal categories above.

**After the first confirmation.** The confirmed formulation is frozen. Its follow-up is the scenario's actual terminal:
- destination;
- V contact;
- hard deadline;
- STALLED;
- context or other;
- AMBIGUOUS / DATA_LOSS;
- open.

A destination or V terminal needs a minute that reaches the level, starts at or after the confirmation, and is admitted by the terminal.

**Not reconstructable.** A record order, link, level or minute that contradicts these rules makes the scenario `NOT_RECONSTRUCTABLE`, with its reason. It stays in every count; nothing is rebuilt by a new execution. Examples: a REVISE not linked to the active epoch, a CONFIRM on another epoch, a claimed contact its minute does not show, or a bar unavailable.

**Bar audits** (descriptive, they never reclassify). Inside each domain, before its ending dispatch, the bars are scanned for:
- `UNRECORDED_V_CONTACT`, `UNRECORDED_DESTINATION_CONTACT` or `UNRECORDED_QUALIFYING_MINUTE`, which the journal should have recorded;
- after a confirmation, unrecorded V/B contacts before the terminal.

A minute that qualifies for the old formulation but is admitted **in** the ending dispatch is reported as `QUALIFYING_MINUTE_IN_ENDING_DISPATCH`. That is the v0.6 dispatch order: timers, interval contacts, 15m revisions, then confirmations. Such a minute is never credited to either formulation.

**Trigger/destination compatibility.** DERIVED for every formulation with the criterion formalized later (Tq < Bq compatible, Tq ≥ Bq incompatible). It is not a verdict that v0.6 published, and it says nothing about a v0.7 MarketView.

**Child and call.** The A entry attempt (child) final state and the call ids are reported in separate columns. They are never merged with scenario outcomes.

## 5. Outcomes and tables

**Scenario categories** (mutually exclusive, reconciled):
- `NEVER_ARMED`, with its terminal;
- `ARMED_NEVER_CONFIRMED`, by the end of its last segment. This includes destination before confirmation, while armed or in an observation gap;
- `CONFIRMED_ON_ORIGINAL_FORMULATION` (epoch 1, the first ARM);
- `CONFIRMED_ON_REVISED_FORMULATION` / `CONFIRMED_ON_REARMED_FORMULATION` (epoch > 1, by the confirmed formulation's own transition);
- `NOT_RECONSTRUCTABLE`.

**Tables** (evaluation; warmup separate):
- the category reconciliation;
- the category details;
- confirmed group (original vs revised/rearmed) × actual terminal. This is descriptive and selected by confirmation;
- the paths of non-original confirmations (with or without an anchor loss);
- formulation ends by transition, and gap ends ("publications, not independent scenarios");
- derived compatibility × transition × end;
- the fate of the first formulation, and whether a later formulation was confirmed. This is what the earlier first-formulation study represented and what it left out;
- children and calls, separately.

**No interpretation of group differences:**
- No percentage of one group is compared with another as evidence of an advantage of revisions: paths, geometry and the selection by confirmation differ.
- No result after a revision is attributed to the first formulation.
- No accuracy score, significance test, subgroup search, economic figure or parameter change.

**Illustrations.** Chosen by **type**, never by outcome: the first evaluation-window scenario, in birth order, of each of these types:
- revision while armed;
- loss → WATCH → REARM;
- revised or rearmed formulation never confirmed;
- destination before confirmation;
- derived-incompatible formulation.

Each shows its publications (source, publication and cursor), the first later eligible interval, and each segment's end.

## 6. Checks, reproducibility, amendments

**Checks:**
- every A scenario once, one BIRTH each;
- journal sequence strictly increasing and record ids unique;
- segments ordered and non-overlapping;
- epochs 1..n;
- at most one confirmation per scenario, on its last formulation and linked to its epoch, derived-compatible;
- no tail birth;
- every reconciliation in `results.json`.

**Synthetic discriminating cases.** `python revisions.py selftest` → [`selftest.json`](selftest.json): **34/34**. Each is run in LONG and SHORT:
- REVISE before confirmation, with the earlier qualifying minute never credited;
- ANCHOR_LOST → WATCH → REARM, then V after confirmation;
- B contact before confirmation, while armed and in the gap;
- publication and contact in the same dispatch: a zero-length gap, a confirmation on a pre-publication or source minute rejected, and a qualifying minute in the superseding dispatch reported but not credited;
- an ambiguous anchor contact and insufficient linkage;
- incompatibility including the tick: T = B and T beyond B are incompatible, T one tick before B is compatible.

Plus the whole tabulation path on a two-scenario synthetic journal.

**Execution.**
- `python revisions.py run <run_dir> out/` writes `results.json`, `scenarios.csv` (one row per scenario), `formulations.csv` (every formulation and gap) and `sequences.json` (each full chain with its records).
- It is run **once** for the tabulation.
- Reproducibility is then checked by a second run on the same artifacts: identical hashes, no engine.

**Amendments.** Any correction after this registration is an explicit amendment that states which results were already visible.

No product, engine, v0.6, v0.7 or study change.
