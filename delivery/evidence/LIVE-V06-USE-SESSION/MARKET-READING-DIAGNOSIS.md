# "Lettura attuale del mercato" box of the Owner use session: diagnosis

**Executor diagnosis only (2026-10-12, base `baf9ffa`).** No product change, no correction proposed: the next step waits for Gian's feedback. Only material already recorded was used: the session's saved view, the journal, the frontend of build `87322ac` and `Cattura.PNG`. No session, acquisition or economic evaluation was run. v0.6 and HDP-001 are frozen; the studies are INACTIVE.

## 1. Original screenshots

| Searched | Result |
|---|---|
| Repository: all local and remote refs, untracked and ignored files | One original screenshot: [`../Cattura.PNG`](../Cattura.PNG), uploaded by the Owner in `6e9d917`, showing the cockpit at 10:49:20 UTC (12:49:20 Rome). |
| Other images under `delivery/evidence/` | Synthetic test or proposal captures, not from this session. |
| Owner's personal folders, clipboard, "Copy analysis for chat" | Not searched or not recorded. If Gian has other captures, they are not in the record. |

`Cattura.PNG` does not show the box. In the 87322ac layout the box sits under the chart card, and in the capture that card's legend already reaches the bottom edge. **No original image of the box exists in the record, so the text Gian read is not attested.**

## 2. Recorded state and how faithful the reconstruction is

The box (`MarketReading`, `web/src/views/LiveProposal.tsx`) reads only these fields: `view.market_view.expected_direction`, `conditional`, `table_row` and `principal`. When `principal` is set it also reads the matching `view.scenarios` entry. In all four records of the session `principal` is null, so the box text depends only on the first three fields. `web/` is unchanged between `87322ac` and `baf9ffa`. The rendering used the UI actually served by the Owner stack (build `87322ac`) with the existing E2E technique: Playwright `page.route` on `/api/adviser/live`. Every non-GET request was aborted. Script and inputs: [`reconstruction/`](reconstruction/).

| Class | Variant | Source | Box valid for (UTC) | Attested / not attested |
|---|---|---|---|---|
| Original screenshot | — | none for the box | — | — |
| **Reconstruction from saved state** | `saved` | `GET /api/adviser/live` after Stop, unmodified: the session's saved view (`view_seq` 4181), `market_view` = journal record 781 | 11:30:01.97 → Stop 11:45:49.6 | Box: every input field attested. Record 781 and the served `market_view` are equal on every field except `levels.last_trade_close`, which the box does not show. The page around the box is the stopped state (Stopped notice), not the live page. |
| **Partial reconstruction** | `record-760` | saved view with only `market_view` replaced by journal record 760 (RECONSTRUCTED, 08:30) | 09:22 (LIVE) → 10:00:01.6 | Box: input fields attested by the record. Not attested: that the view served at those instants carried exactly this record (served-view equality checked only at the final instant), and everything outside the box (scenarios, lenses, chart, the *Valutazione (UTC)* time 11:45:46 in *Approfondimenti*), all taken from the saved final view. |
| Partial reconstruction | `record-772` | as above, record 772 | 10:00:01.6 → 10:30:02.5 | as above |
| Partial reconstruction | `record-776` | as above, record 776 | 10:30:02.5 → 11:30:01.97 | as above |
| Partial reconstruction | `record-781` | as above, record 781 | 11:30:01.97 → Stop (cross-check: same box as `saved`) | as above |

No reconstruction is the screen Gian saw. Each image carries a dashed RECONSTRUCTION label added outside the box.

## 3. Full text of the box

Only two distinct texts occur during the session (rendered `innerText`, [`reconstruction/rendered-text.json`](reconstruction/rendered-text.json)).

**Text A**, 09:22 → 10:00:01 and 11:30:01 → Stop UTC (11:22 → 12:00 and 13:30 → 13:45 Rome). Images: [`market-reading-saved.png`](reconstruction/market-reading-saved.png) (saved state), [`market-reading-record-760.png`](reconstruction/market-reading-record-760.png) (partial).

```text
Lettura attuale del mercato
È una valutazione del mercato, non la call: non dice se entrare.
◆ Direzione attesa: Incerta · Nessuna struttura qualificata nelle condizioni attuali
Nessuno scenario principale in questo momento.
Lettura qualitativa, non una probabilità.
```

**Text B**, 10:00:01 → 11:30:01 UTC (12:00 → 13:30 Rome). Images: [`market-reading-record-772.png`](reconstruction/market-reading-record-772.png) and [`-776.png`](reconstruction/market-reading-record-776.png) (partial).

```text
Lettura attuale del mercato
È una valutazione del mercato, non la call: non dice se entrare.
◆ Direzione attesa: Equilibrio · Mercato in equilibrio (range)
Nessuno scenario principale in questo momento.
Lettura qualitativa, non una probabilità.
```

The box contains no "BALANCED". The raw code appears elsewhere on the page:
- In the lens card *Momentum (1h context)*, visible without expanding: result `BALANCED`; the saved lens reports it since 2026-10-12T00:00Z. The role text also reads "C needs BALANCED".
- In the collapsed *Approfondimenti* of the right panel: *Contesto 1h osservato* `BALANCED`; *Lettura* `BALANCED · BALANCED_RANGE` during text B; *Motivazioni* "observed BALANCED/…" or "balanced 1h context…".

Which of these Gian read is not recorded and is not deduced here.

## 4. Observation → expectation → current operational meaning

| | Text A (records 760, 781) | Text B (records 772, 776) | Where it is shown |
|---|---|---|---|
| **Observation** | `observed_context` BALANCED; `phase` EXPANSION (760) / TRANSITION (781) | `observed_context` BALANCED; `phase` ROTATION (772) / COMPRESSION (776) | Not in the box. Raw codes only, in *Approfondimenti* and the Momentum lens card |
| **Reason** (`reasons`) | "observed BALANCED/TRANSITION; missing antecedent: no born A impulse or compression box scenario" | "balanced 1h context in rotation; no qualified box" (compression in 776) | Not in the box. English system text in the collapsed *Approfondimenti* |
| **Expectation** | `expected_direction` UNCERTAIN, `table_row` NO_QUALIFIED_STRUCTURE | `expected_direction` BALANCED, `table_row` BALANCED_RANGE | Box: *Incerta* / *Equilibrio* plus the row text |
| **Scenario / horizon** | `principal` null, `horizon_minutes` null | same | Box: "Nessuno scenario principale in questo momento." |
| **What would change it** | `watch`, `alternatives`, `counterevidence`, `blockers` all empty | same | Nothing to show |
| **Current operational meaning** | `call` null, no LIVE scenario or entry attempt | same | Not in the box ("non dice se entrare"). The right panel shows "In attesa — nessun ingresso proposto" |

### Missing links (reported, not filled in)

1. **Observation absent from the box.** The box gives the conclusion (*Incerta* / *Equilibrio*) but not what was observed: the 1h context BALANCED and the phase. They appear only as raw codes, in a collapsed section of another panel and in a lens card.
2. **Reason not presented as an explanation.** The `reasons` field exists, but only as English system text in the collapsed *Approfondimenti*. It uses internal terms ("born A impulse", "compression box", "qualified box") without plain wording.
3. **Incerta vs Equilibrio not explained.** The observed context is BALANCED in both. In the record the difference is the table row and its reason: no qualified structure or antecedent scenario, versus a balanced range in rotation or compression. The box shows the two labels but not what separates them.
4. **"What would change it" is empty in the data.** `watch`, `alternatives`, `counterevidence` and `blockers` are empty and `horizon_minutes` is null in all four records. The frontend has nothing to present. Whether the method should fill these in this state is a Director question; nothing is invented here.
5. **No link from the reading to the waiting state inside the box.** The box disclaims the call. The reason for the waiting state ("no principal scenario, so no call") is spread across the box's "Nessuno scenario principale" and the other panel's "In attesa". No recorded field states that link as text.

## 5. Status

- **Next step.** Waiting for Gian's feedback on what he read and found unclear before any correction is proposed. Layout, palette, method and rules are unchanged.
- **CI before Start.** On the exact SHA `87322acd4a74f8aa875312c380408f7d09369823`, the Owner answered "ci verde, va bene farlo ora". The attestation is the Owner's. CI was not verified by the Director and not queried by the executor ([NOTE](NOTE.md) §1).
