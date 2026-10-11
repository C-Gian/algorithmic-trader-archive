# Live cockpit — second visual proposal IMPLEMENTED (synthetic images and checks)

Base `c7abfb8ea4ef93789ea2ddb95f16e1fb5e638304`. Gian approved the [second proposal](../COCKPIT-VISUAL-PROPOSAL-2/PROPOSAL.md) ("per ora ok"). This step implements it in the product UI.

**Status: implementation complete; the final check with the Owner is still to do.** The technical checks below show that the UI renders the states correctly. They are not evidence that Gian understands the cockpit; that is the short joint check after delivery.

Synthetic engineering inputs only. No real feed, Owner data or economic test. v0.6 and HDP-001 are frozen; the studies are INACTIVE.

## What changed (web only)

Files: `web/src/views/LiveCockpit.tsx`, `web/src/views/LiveProposal.tsx`, `web/src/styles/adviser.css`, `web/src/lib/format.ts`.

1. **The approved draft** ([`draft-ui.patch`](../COCKPIT-VISUAL-PROPOSAL-2/draft-ui.patch)), applied as recorded:
   - chart and market reading on the left (≈ 5/12), decision panel on the right (≈ 7/12);
   - the call strip, the two perspectives as full-width rows, then Approfondimenti;
   - candles in the existing `PriceChart`, from the `chart.minutes` o/h/l/c already received;
   - the whole-cockpit colour map.

   The DRAFT comments became ordinary comments. The old `live-grid` layout rules, now unused, were removed.
2. **Checks before applying it, with two restorations:**
   - **No view.** The draft hid the "Nessuna valutazione in corso" state (`live-no-view`) and the "Direzione attesa: Non disponibile" line. Both are restored, so a stopped cockpit shows what it showed before.
   - **Published contents and values.** The texts and values are the same as before. Only these change: the approved labels ("Origine: call live", "Conclusa — …") and the number notation below.
   - **Update identity.** The concluded call's API reading is still keyed by run + call + terminal time. Call history is still keyed by run + call. Neither moved.
   - **Asynchronous responses.** The guard against a late response showing under another call or run is unchanged.
   - **Entry band.** It is shown only when the backend state is AVAILABLE and current, in both the panel and the chart. This rule is unchanged.
   - **Concluded call vs new expectation.** The concluded call has its own strip and row 2. The market reading sits under the chart with "non è la call". The sentence "La successiva aspettativa (…) non prolunga questa call" stays.
3. **Ordinary corrections included in the assignment:**
   - **Italian price notation.** A new `fmtPrice` is used in the chart labels, the call strip, the band, the concluded target, the market reading, the condition and the panel details. The value is never rounded: up to 8 decimals are kept, and trailing zero decimals are not printed. Examples: 100700.0 → 100.700, 100798.5 → 100.798,5. This matches the approved guidance sentence ("stop 99.700 e target 100.700"). Before, the chart used `fmtNum(…, 1)` with US grouping, which also rounded to one decimal.
   - **Level labels never overlap.** `placeLabels` pushes labels apart downward, then back up from the bottom edge, and keeps them inside the chart. A label that moves keeps a leader to its own line. Labels and the band label have a halo, and the band label is drawn above the candles. The first version, with 13-unit spacing, overlapped; the new test caught it, and the spacing is now 15.
   - **Method badge.** It now wraps instead of being cut (`.badge.method-badge`). At 390 px it takes two lines.

Unchanged: semantics, guidance and its translations, authoritative availability, method, API, persistence, Workbench (its `.live-chart` mini chart is not affected: candle rules are scoped to `.is-candles`), Copy analysis.

## Images (implementation, synthetic states)

1440 × 1000, Chromium, Europe/Rome; each image is the cockpit area, labelled "Dimostrazione sintetica — cockpit implementato".

| # | State | Image |
|---|---|---|
| 1 | Waiting, no call | [1-attesa-senza-call.png](1-attesa-senza-call.png) |
| 2 | LONG available | [desktop](2-long-disponibile.png) · [1024](2-long-disponibile-1024.png) · [390](2-long-disponibile-390.png) |
| 3 | SHORT available | [3-short-disponibile.png](3-short-disponibile.png) |
| 4 | UNVERIFIED (no fresh quote) | [4-non-verificabile.png](4-non-verificabile.png) |
| 5 | Entry CLOSED, thesis ONGOING | [desktop](5-ingresso-chiuso-tesi-aperta.png) · [1024](5-ingresso-chiuso-tesi-aperta-1024.png) · [390](5-ingresso-chiuso-tesi-aperta-390.png) |
| 6 | Call concluded (TARGET_REACHED), new expectation | [6-call-conclusa-nuova-aspettativa.png](6-call-conclusa-nuova-aspettativa.png) |

The states are the proposal's own, from `states()` in [its generator](../COCKPIT-VISUAL-PROPOSAL-2/generate_proposal.py). They are real v0.6 engine states from three **independent** sessions (LONG, mirrored SHORT, the call-updates episode), not one sequence. Facts: [implementation-states.json](implementation-states.json). Generator: [generate_implementation.py](generate_implementation.py).

## Checks run

- **Typecheck and build:** `npm run build` passed.
- **Per-state checks in the generator.** All six states are checked at 1440, 1024 and 390 px: 18 checks, all passed. Each check waits until that state's own view is rendered (clock and last minute), then verifies:
  - the panel matches the served view;
  - the ▲/▼ chip and its green/red fill;
  - blue only for AVAILABLE and amber for UNVERIFIED;
  - the band in the panel and chart only when AVAILABLE;
  - target, stop and band equal to the published values in Italian notation;
  - the approved CLOSED sentence;
  - state 6 shows the concluded call, TARGET_REACHED guidance, the separation sentence and the current reading "Rialzo";
  - candles equal to `chart.minutes` (OHLC and time order);
  - no overlapping level labels;
  - no horizontal overflow and the method badge not cut;
  - the chart left of the panel at 1440, and the panel above the chart at 1024 and 390.
- **New E2E** `tests/e2e/test_live_cockpit_layout_e2e.py`, covering only the introduced risks, at 1440, 1024 and 390:
  - SHORT available (filled red chip, filled blue ✓ availability) vs an action error (the notice is `tone-warn` with an amber icon; the Stop button is not red);
  - concluded LONG (transparent, dashed chip, "Conclusa — target raggiunto", no availability block or band) vs available LONG;
  - candle OHLC, time order and body inside the wick; levels at the published values, merged when equal, ordered by price;
  - level labels that are close together (stop 99,700 and support 99,712; target 100,700, resistance 100,700 and box 100,690) not overlapping and inside the chart;
  - computed contrast of at least 4.5:1 for the state block, the chip, the session and method badges and the expected direction, in four states;
  - one symbol (svg) in every state block.
- **Updated existing E2E** for the new notation and layout:
  - `test_live_proposal_e2e`: scenario levels "100.900" and "99.700", "oltre 99.500", the call identity in the strip, row 2 containing the concluded call, the market reading under the chart;
  - `test_adviser_e2e`: "▲ LONG", "100.798,5";
  - `test_live_call_history_e2e`: "▲ LONG";
  - `test_live_continuity_e2e`: the band via `it_price`.

  `it_price` in `test_ui_smoke.py` mirrors `fmtPrice`.
- **E2E:** 24 passed, in 612.9 s, on a disposable PostgreSQL container (removed afterwards). The suites: `test_adviser_e2e`, `test_live_call_history_e2e`, `test_live_cockpit_layout_e2e`, `test_live_continuity_e2e`, `test_live_presentation_e2e`, `test_live_proposal_e2e`, `test_mp002_e2e` to `test_mp005_e2e`, and `test_ui_smoke`. One SyntaxWarning in `test_live_continuity_e2e.py:49` predates this change.
- **Contrast.** The proposal's table ([contrast.py](../COCKPIT-VISUAL-PROPOSAL-2/contrast.py), 26 pairs) still applies: the colours are those of the draft. The new E2E also measures the rendered contrast.

## Limits

- The tapes are synthetic step series: many minutes are flat, so many candles look like ticks.
- At 390 px the SVG chart is scaled down (≈ 0.75×), so its labels are small. They do not overlap, and the values are repeated in the panel.
- At 1440 px, when the panel is shorter than the left column, some empty space remains under it (as in the proposal).
- Lens and timeline texts, the recorded system texts and the call history keep their original form, mostly English with raw numbers. Only the chart and the decision panel use the Italian notation.
- No second chart: the 15-minute context stays a candidate, as in the proposal.
- Remote CI is Owner-operated: PENDING / NOT CHECKED.
