# "Lettura attuale del mercato" box: presentation in three linked steps

**Executor delivery (2026-10-12, base `0619e5f`).** This is a presentation change to the box only, per the orchestrator's decision: explain the present state faithfully and declare when no condition is published. No new engine information and no trigger derived in the frontend. Engine, method, API, persistence and guidance are unchanged. The general layout, the palette and the right-hand panel (with its *Approfondimenti*) are unchanged. **The Director's review and the Owner's guided check are still pending; comprehension is not verified.** v0.6 and HDP-001 are frozen; the studies are INACTIVE.

## 1. Review: source → displayed text

Producers checked:
- `core.py` `_derive_1h` / `_derive_15m` (context and phase classes, shared by every method);
- `compute_view` in `core.py` (v0.2) and `core3.py` (v0.3–v0.6, inherited by `adviser.core.v6`);
- `scenarios_view` / `inspect`, which publish the scenario lists;
- the session records 760, 772, 776 and 781 and the saved view.

| Group | Source (field ← producer) | Text in the box | Missing / unknown |
|---|---|---|---|
| **Observed context** | `market_view.observed_context` ← `_derive_1h`. UP/DOWN when the 1h displacement and efficiency both pass their thresholds; otherwise BALANCED; UNAVAILABLE if 1h is not ready | "Contesto a 1 ora: **in rialzo / in ribasso / in equilibrio / non disponibile**" plus a short description of that class, without numbers | Missing: "non indicato dal sistema". Unknown: "valore non riconosciuto (X)" |
| **Phase** | `market_view.phase` ← `_derive_15m`, checked in order: EXPANSION, COMPRESSION, (UNAVAILABLE), REACTION, ROTATION, otherwise TRANSITION | "Fase a 15 minuti: **espansione / compressione / reazione / rotazione / transizione / non disponibile**" plus a short description of that class. TRANSITION is described as "non corrisponde a nessuna delle altre fasi riconosciute" (the residual class) | as above |
| **MarketView conclusion** | `expected_direction`, `conditional`, `table_row` ← `compute_view` | "Direzione attesa: *Rialzo / Ribasso / Equilibrio / Incerta / Non disponibile*" (unchanged), "(condizionale)", the Italian row text, and one sentence per direction. UNCERTAIN: "Il sistema non indica una direzione: la lettura resta incerta." BALANCED: "Il sistema legge il mercato in equilibrio: non indica né un rialzo né un ribasso." | Unknown direction: "Lettura non riconosciuta (X)." The row label BALANCED_RANGE changed from "Mercato in equilibrio (range)" to "Equilibrio in fase di compressione o rotazione", which is the row's own condition, with no future range |
| **Recorded reason** | `market_view.reasons` ← `compute_view` (the exact texts of both producers) | "Perché: …", an Italian rendering of each recognized text. Session cases: "Manca il presupposto: non è nato nessuno scenario di impulso (famiglia A) o di box di compressione." and "Contesto a 1 ora in equilibrio con fase di rotazione/compressione; nessun box qualificato, quindi nessun limite di prezzo indicato." With a box: "il prezzo ruota dentro il box L – U" (values kept, Italian grouping) | Empty: "Il sistema non ha registrato una motivazione testuale". Unrecognized: "registrata solo come testo tecnico", raw text in *Termini tecnici*. A mix of both adds "Altre motivazioni…". The raw reasons are always in *Termini tecnici* |
| **Published entry condition** | principal: `market_view.principal` plus its `view.scenarios` entry; existing `condition()`: trigger, return corridor, local recovery, observation, ended attempt | "Che cosa sta aspettando": the existing scenario table (destination, invalidation, horizon) and "Condizione ancora necessaria", with **texts and values unchanged** | Principal without a condition: "il sistema non ha pubblicato una condizione specifica per questo scenario" (no "nessuno scenario") |
| | Other published scenarios: `alternatives`, `watch` (v0.3+), `view.scenarios` (v0.3+), `view.attempts` (v0.2) | One line per scenario: "Scenario DIR FAM (stato): condition, or no published condition" | — |
| | Call: `view.call` or `market_view.ongoing_call_id` | "È in corso una call: ingresso e aggiornamenti sono nel pannello «Che cosa propone il sistema adesso»." | — |
| | No principal and **every list present and empty**, no call | "Non c'è ancora uno scenario attivo. Il sistema non ha pubblicato una condizione specifica da attendere per un ingresso." | A list absent from the payload is unknown: only "Il sistema non ha pubblicato una condizione specifica da attendere per un ingresso." The absence of a call is never used to say there is no scenario |
| **Event that would change the reading** | No MarketView field publishes one. `counterevidence` and `blockers` are shown raw | In *Termini tecnici*, when there is no published scenario: "Non è indicato un evento specifico che farebbe cambiare questa lettura. È un limite della spiegazione disponibile: non significa che la lettura non possa cambiare." | When scenarios exist the sentence is not shown: their levels appear in step 3 and are not presented as reading-revision events |

The box introduces no trigger, wait, "rottura", "conferme", sideways movement or availability wording. MarketView, call and current availability stay apart: the box still opens with "non è la call: non dice se entrare", and the waiting state stays in the right-hand panel.

## 2. Diff (circumscribed)

- `web/src/views/LiveProposal.tsx`:
  - `MarketReading` reorganized into three steps;
  - local tables `CONTEXT_IT`, `PHASE_IT`, `CONCLUSION_IT`, `STATUS_IT`;
  - `readingReasonIt` (exact reason patterns), `ScenarioWait`, the *Termini tecnici* `details`;
  - the BALANCED_RANGE row label.
- `web/src/adviser.ts`: optional `watch` in the frontend `MarketViewDoc` type (already served by the API).
- `web/src/styles/adviser.css`: five local `.mr-*` rules using existing tokens.
- `tests/e2e/test_live_market_reading_e2e.py`: new, see §3.

## 3. Checks actually run

- `npm --prefix web run build` (TypeScript typecheck plus Vite build): pass.
- New E2E `test_live_market_reading_e2e.py` (3 tests). It runs against the served build on a disposable PostgreSQL 18.6 container, which was removed afterwards; the Owner stack was untouched. It covers:
  - the four session states (saved view, records 760/772/776): observation, conclusion, reason, the no-scenario sentence, the no-event sentence, no forbidden wording, call panel unchanged;
  - field distinction (UP context with an Incerta reading);
  - missing and unknown values, an unknown reason, an absent scenario list;
  - a scenario without a published condition;
  - the existing published-condition cases from `test_live_proposal_e2e` (`waiting_view`, `armed_v02_view`) with values unchanged, and a box boundary kept exactly.
- Regression E2E, same disposable database: **26 passed** in 370 s. Suites: market reading (new), proposal, episode, cockpit layout, presentation, call history, continuity, restart, adviser, MP-005, UI smoke.
- After that run, the UNAVAILABLE descriptions were corrected: phase UNAVAILABLE can also come from the 1h context, so both now read "dati … insufficienti o non aggiornati". The build was rebuilt and the new test plus the proposal main-panel test were re-run: **4 passed**. The other 22 regression tests were not re-run after this text-only correction.
- Not run: the full non-E2E suite (no backend file changed) and compose smoke.

## 4. Images (RECONSTRUCTION)

Produced by the new test against the updated build; each image carries its label. None is the Owner's screen.

| Image | Source | Valid for (Rome) |
|---|---|---|
| [`market-reading-v2-saved.png`](reconstruction/market-reading-v2-saved.png) | saved view after Stop (record 781): reconstruction from saved state | 13:30–13:45 |
| [`market-reading-v2-record-760.png`](reconstruction/market-reading-v2-record-760.png) | saved view + record 760: partial | 11:22–12:00 |
| [`market-reading-v2-record-772.png`](reconstruction/market-reading-v2-record-772.png) | saved view + record 772: partial | 12:00–12:30 |
| [`market-reading-v2-record-776.png`](reconstruction/market-reading-v2-record-776.png) | saved view + record 776: partial | 12:30–13:30 |

The images show the box with *Termini tecnici* open; in the cockpit that section is collapsed by default.

## 5. Limits

- The descriptions of context and phase paraphrase the engine's classification conditions, without thresholds. The Director should check the wording.
- Reasons are translated only for the exact texts the engines write today. A changed engine text falls back to technical display (tested), never to a guessed paraphrase.
- The right-hand panel's *Approfondimenti* still shows raw codes (outside this scope).
- The Owner's running stack still serves `87322ac`: the change is not deployed there. It needs the README upgrade procedure, which is the Owner's decision.
- Gian's comprehension is not verified: the Director's review and the guided check remain pending.
