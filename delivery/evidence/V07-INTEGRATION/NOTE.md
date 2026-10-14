# Adviser v0.7 — integration of the trigger/destination correction as a product version

13 October 2026, base `57fa14e` (the approved reference). Executor delivery; the Director's review is separate and pending. Release record: [V07-TRIGGER-DESTINATION-RELEASE.md](../../V07-TRIGGER-DESTINATION-RELEASE.md).

**All screenshots and records here are SYNTHETIC.** They are an engineering proof on hand-designed tapes, with offline OKX fakes, a disposable local database and no Owner data. They have no market or economic meaning.

## What changed

**Version.**
- `v0.7` is in the selectable releases, with status "engineering review pending". The default stays v0.2, and v0.6 is unchanged (identity hashes pinned).
- The EXPERIMENTAL v0.6-tdc and v0.6-a2x stay variants. No a2x content.
- `core7` is the approved tdc fold under its own identity: core, state and runtime v7, engine `observe.stream.v8`, report v7, reconciliation 10, Deep 11. Its one inspection-only addition is the engine verdict `trigger_destination` on A scenario rows.

**Contracts.**
- semantic.v2 **revision 6**: values and semantics only; v0.7 emits the revision-5 shapes. observe.v1 **revision 10**: the method value `v0.7`.
- Both baselines were regenerated, with changelog entries.

**App paths, reusing the existing ones.**
- Method list, evaluation launch, pack worker, live session and cockpit Start.
- Report v7: the v0.6 report plus counts of the published compatibility.
- Reconciliation v10: the published statement must equal the record's own levels.
- Deep v11 and the comparison limitation for v0.6/v0.7.

**Cockpit.** It translates into Italian the engine's sentences and its verdict, and computes nothing from prices or levels:
- scenario recognized, but its current condition is incompatible;
- no directional support from it;
- what the published MarketView says beside it, from its row only (see the correction below);
- support restored by a compatible revision, with its publication time.

Actual statuses (WATCH/ARMED) and earlier records are kept. No restyling.

**Restore.**
- A v0.7 state never decodes as v0.6, tdc or a2x, and vice versa.
- A paused v0.7 run resumed under v0.6 fails INCOMPATIBLE_ADVISER_IDENTITY.
- A live session under another method starts a new epoch (METHOD_CHANGED).

## Integrated path (E2E: cockpit → API → live worker → engine → DB → API → cockpit)

| Episode (synthetic tape) | Observed |
|---|---|
| LONG `revision_restores`, started from the cockpit with method v0.7 | 03:45:01 first ARM K 100900 > B: API WATCH_ONLY / UNCERTAIN, scenario ARMED with verdict incompatible (threshold 100900.1, destination 100900). Cockpit: incompatibility, no support, "Nella lettura pubblicata non c'è un'aspettativa direzionale sostenuta" (WATCH_ONLY), the same after reload |
| same, 04:00:01 compatible REVISE | CONDITIONAL / UP; verdict compatible, `restored_by_revision`; cockpit: "La condizione è stata rivista alle … solo da questa nuova pubblicazione" |
| same, operations | CONFIRM 04:06:01 (the 04:00 minute straddles the live REVISE publication). The child state and no call equal an in-process frozen v0.6 live session on the same tape |
| same, Stop then Start v0.7 | same run restored; 240 records before Stop, 252 after the restart, 0 duplicates, earlier records identical |
| same, then Start v0.6 | new run (METHOD_CHANGED v0.7→v0.6); the v0.7 records unchanged; v0.6 publishes no verdict |
| SHORT `hold(H_AT)` | threshold exactly at B (99100.0 = 99100): incompatible, WATCH_ONLY; cockpit "≤ 99.100 … è già alla destinazione" |
| LONG `valid_and_incompatible`, started 07:31 | 07:45:01 incompatible ARMED S2 while the reconstructed confirmed S1 stays principal: CONDITIONAL / UP, S2 among the hypotheses; cockpit "Un altro scenario (LONG A) sostiene la lettura corrente." |

The tick borders before and beyond B are proven by the engine suites and not repeated here.

Screenshots (SYNTHETIC):
- [1 incompatible](v07-1-long-incompatible-no-support.png)
- [2 restored by revision](v07-2-long-restored-by-revision.png)
- [3 after restore](v07-3-long-after-restore.png)
- [4 SHORT at B](v07-4-short-threshold-at-b.png)
- [5 valid scenario present](v07-5-long-valid-scenario-present.png)

Record: [e2e-v07-long-revision.json](e2e-v07-long-revision.json).

## Correction after the static review of `1930a27` (14 October 2026)

The review found that the sentence beside an incompatible scenario was deduced from an absent principal. Without a principal, the cockpit said "Nessun altro scenario sostiene ora una direzione", which the MarketView does not state: an absent principal also occurs with OPPOSING_SCENARIOS or REQUIRED_CONTEXT_UNAVAILABLE.

The fix is presentation only (`web/src/views/LiveProposal.tsx`). The engine, the contracts and the operating policy are unchanged, and there is no geometric computation in the frontend. The sentence now repeats only the published `table_row` and `principal`:

| Published MarketView | Sentence beside the incompatible scenario |
|---|---|
| CONDITIONAL_SCENARIO with a principal (not the incompatible scenario itself) | "Un altro scenario (LONG A) sostiene la lettura corrente." |
| OPPOSING_SCENARIOS | "Esistono sostegni direzionali opposti: la lettura non indica una direzione unica." |
| REQUIRED_CONTEXT_UNAVAILABLE | "Il sistema non può pubblicare una lettura direzionale corrente." |
| WATCH_ONLY | "Nella lettura pubblicata non c'è un'aspettativa direzionale sostenuta." |
| any other row, or CONDITIONAL_SCENARIO without a principal | no added sentence |

**Checks for the correction.**
- Integrated episodes 1 and 3 (real path) now assert the WATCH_ONLY and CONDITIONAL_SCENARIO sentences, and that "Nessun altro scenario" no longer appears.
- New test `test_v07_incompatible_note_translates_only_the_published_reading`. **This is a TRANSLATION TEST, not an integrated engine proof.**
  - Its base is the real v0.7 live view of the SHORT `hold(H_AT)` tape at 03:45 (WATCH_ONLY).
  - The worker is then stopped, and the cockpit is served PREPARED variants that change only `table_row`, `expected_direction` and `principal`. These cover CONDITIONAL_SCENARIO with a principal, OPPOSING_SCENARIOS, REQUIRED_CONTEXT_UNAVAILABLE and CONDITIONAL_SCENARIO without a principal.
  - For each, it asserts the expected sentence, the absence of the other sentences and the absence of "Nessun altro scenario".
  - It does not claim that the engine publishes these combinations on this tape; the opposing case is still only a white-box supplement for the engine.
- `tests/e2e/test_v07_live_e2e.py` only: **4 passed**, on a disposable PostgreSQL 18 cluster (scratchpad, port 55433). It was run twice: once plainly, and once with `ALGOTRADER_EVIDENCE_DIR` to regenerate the five SYNTHETIC screenshots and the record. In the record only the random run ids changed.
- `npm run typecheck` and `npm run build` pass; the chunk-size warning is pre-existing.
- The full suite and the other E2E files were **not** rerun, as instructed. CI: PENDING / NOT CHECKED.

## Checks

Run on a disposable local PostgreSQL 18 cluster (scratchpad, port 55432), never the Owner stack.

- **Full suite without e2e, DB suites included** (`ALGOTRADER_REQUIRE_DB=1`, 6 shards): 1701 passed, 6 failed, 0 skipped.
  - Five of the failures were pins of the new revisions and release list, or tests using `v0.7` as their "unknown method" example. They were updated, as WP-015 did for v0.6, and every affected file was rerun: 132 passed.
  - The sixth, `test_lifecycle::test_cancel_during_validation_at_full_cursor_is_incomplete_not_pass`, is **pre-existing**. It fails identically on an untouched worktree of `57fa14e` (the cancel lands in GENERATING_REPORT instead of VALIDATING, local timing; observation-only path). It is reported and not modified.
- **New tests:** `test_v07_release.py` 28 passed; `test_v07_db.py` 9 passed; `tests/e2e/test_v07_live_e2e.py` 3 passed.
- **E2E suite:** 36 passed, the 3 new episodes included.
- **Web:** `npm run typecheck` and `npm run build` pass. The chunk-size warning is pre-existing.
- **tdc suite:** `test_tdc_trigger_destination.py` included in the full run. The release-set pin was updated.
- **Not run:** lint (none configured) and CI (Owner-operated: PENDING / NOT CHECKED).

## Limits

- **Synthetic only.** No real data, replay, acquisition, tuning, economic study, Owner installation or CI query.
- **Live call path.** On the live path the frozen v0.6 child on this tape keeps waiting (WAIT_RETURN) and no call is issued. The equality with v0.6 is shown on that path; a call itself is compared in the DB pack evaluations (one identical call in v0.6 and v0.7).
- **Wording.**
  - The cockpit row label for WATCH_ONLY ("Solo ipotesi in osservazione") is shared with v0.6. The incompatible scenario is shown with its actual state, armato.
  - The explanation appears in the reason and in the waiting step as well as in the dedicated note, so it is repeated.
- **The opposing case** (a valid scenario plus an incompatible one in the opposite direction) remains only a white-box supplement.
