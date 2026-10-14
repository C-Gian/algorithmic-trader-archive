# Price–volume semantics at a range exit — documentary feasibility

**Executor delivery, 14 October 2026.** The Director's review is separate and PENDING. Astra's authorization, relayed by the Owner. Documentary only.

**Not done:** no implementation, acquisition, Owner extraction, historical processing, quantitative test or backtest. A, RETURN, E and a2x are not reopened. v0.7 is unchanged; v0.6 and the registered studies stay frozen.

**Question.** Which observable relation between participation and price progress can justifiably change the reading of continuation or re-entry, before the sequel is known? The scope is the exit from a pre-existing range and the immediately following response.

**Conventions.**
- **Citation** = the source's verbatim words, checked in the original.
- **Paraphrase** = the source's content restated.
- **Interpretation** = ours, with every discretionary choice marked **[D]**.

## 1. Professional source

### Consultation record

**Corpus.**
- `ANALISI_EVOLUTA` (Marini). Its volume formula is not published, so it is not reconstructible (as already recorded in that note). Not used.
- LIB-005, *Market Wizards: The Next Generation* (Schwager), interview with Kristjan Kullamägi. Original PDF in the Owner corpus, pp. 29–30. **Chosen.**
- Other LIB-005 passages, not chosen:
  - a one-sentence mention of a "high-volume breakout above a prior consolidation";
  - mentor patterns whose "volume patterns" are not specified;
  - a VWAP parabolic short, which is not a range exit.

**Additional primary sources (limit 2, reached).** Two posts by Pradeep Bonde, the originator Kullamägi names, on his own site. Each was downloaded once and its body text read in full:
1. "How to Identify good momentum burst and make millions", 4 January 2014, <https://stockbee.blogspot.com/2014/01/how-to-identify-good-momentum-burst-and.html>. Downloaded HTML sha256 `e58893ac…87e2`.
2. "How to identify the A quality setup", 14 January 2014, <https://stockbee.blogspot.com/2014/01/how-to-identify-a-quality-setup.html>. Downloaded HTML sha256 `aca4cc7a…494e`.

**Seen while locating them, not used as evidence:**
- two web-search result pages listing third-party indicator descriptions (LuxAlgo, TradingView scripts, Substack posts);
- the blog's own search listing.

Snippets from other Bonde posts on that listing were not verified in the original and are not used. For example: volume "significantly higher than volume in preceding 8 to 10 days"; "immediate follow through". No general review was made.

### The explanation, verified in the original

**Kullamägi (LIB-005, p. 29), citations:**
- "You look for a stock in an uptrend that then goes into a sideways consolidation, preferably on reduced volume. You then buy the stock when it breaks out of the consolidation and hold it for three to five days."
- Entry: "above the opening range or above the high of the first 5-, 30-, or 60-minute bars. The longer the time range used for the entry signal, the worse the entry price, but the lower the risk of entering on a false breakout."
- On false breakouts (p. 30): "They are. […] the success rate will be well below 50%."

**Bonde, post 1, citations:**
- "The stock will have 3 to 20 days consolidation prior to range expansion day";
- "The stock will have series of narrow range days prior to breakout";
- "On breakout day volume is higher than previous day";
- "On breakout day stock closes at or near its high for the day (preferred)".

Learning is by practice: "Automaticity or procedural memory is developed through solved examples and practice."

**Bonde, post 2, citations:**
- the guideline list: "stock should have range expansion on breakout day"; "volume on breakout day should be higher"; "day before breakout should be narrow range day or negative day"; "volume during consolidation should be preferably orderly"; "stock should close near high on breakout day";
- the example: "a 4% breakout on high volume";
- on quality: "Better quality setups allow us to put logical and tight stop and they work instantly."

**Paraphrase.** A breakout from a short, narrow, orderly consolidation is an **A-quality** setup when the breakout bar jointly shows:
- range expansion;
- a close near its high;
- higher volume than the bar before it.

Missing elements make it **marginal**. The setup is not invalidated. Volume is one item of a joint, discretionary checklist ("guidelines"), learned as a skill and not as a rule.

**What the source does not contain (essential gaps):**
- no volume reading of the **response** after the exit: no retest, re-entry or failed exit;
- no statement that lower volume predicts re-entry;
- no volume reading for a short side, except that bearish setups exist;
- no reference for "high" other than "previous day";
- no definition of "orderly".

The empirical frame is US equities on daily bars, leading or low-float stocks, and 3–5 day holds. It does not transfer to BTC 15m and is not claimed to. "Buying frenzy" is narrative wording. No intention, institutional participation or absorption is attributed here to aggregate volume.

## 2. Comparison with the current B/C rules

Rules from MP-001 §B/§C and the shared box.

**What price already recognizes:**
- **Prior contraction:** COMPRESSION phase, CR ≤ 0.75, ER6 and ER16 ≤ 0.35, width 2–6 S15, two touches on each edge.
- **Exit:** first complete 15m close beyond U+z (or L−z).
- **Response:** B does not issue on the break bar and requires a retest inside [U−z, U+z] within four bars, with close > U and low > L. A close back below U−z cancels the attempt.
- **Failed exit:** C covers a wick beyond L−z with a close back above L+z.

**What volume would add.** Only one observation not contained in OHLC: whether the **traded quantity of the break bar** exceeds that of the bar before it. That is the source's "breakout day" relation.

| Source element | B/C counterpart | Classification |
|---|---|---|
| Consolidation "preferably on reduced volume" / "orderly" volume | COMPRESSION, CR, ER, width, touches (price only) | **Not interpretable**: "orderly" is undefined and no reference is given. Partly **redundant** in intent with the price contraction already required. Not used. |
| Range expansion on the break bar | Not required (a minimal close beyond U+z qualifies) | A price element the source pairs with volume. B has no counterpart; defining one would be our own choice **[D]**. |
| Close near the high | Not required | As above. |
| Break-bar volume higher than the previous bar | None (the participation ratio is descriptive only, vs a 20-bar median) | **The only addable relation** (§4). |
| Volume during the retest / response | B's retest and cancellation rules (price only) | **Not reconstructible**: the source is silent. |
| Volume at a failed exit / reclaim (C) | C's reclaim geometry | **Not interpretable**: the source is silent. |
| Lower volume → re-entry | — | **Not in the source.** Its contrary of "A-quality" is "marginal", not "will re-enter". |

**When volume would be contrary or not interpretable:**
- **Contrary.** The break bar closes beyond U+z but trades less than the bar before it. In source terms the setup is "marginal". This weakens the A-quality reading; it does not predict re-entry.
- **Ambiguous:**
  - the previous bar is itself part of the move (a failed push at U with already high volume);
  - the two bars sit across a change in the clock-time activity profile of 24/7 trading, which is absent from equity daily bars;
  - higher volume comes with a close far from the high: the source's checklist items disagree.
- **Not interpretable:** either 15m aggregate is not COMPLETE.

Higher volume is **not** assumed to confirm a breakout. The source asserts an association with setup quality and gives no evidence here; Kullamägi states that false breakouts are common.

## 3. Representable data (from schema, connector and docs; nothing acquired)

**Market and instrument.** OKX `BTC-USDT-SWAP`, one venue, linear perpetual. Trade candles 1m. No spot or other-venue volume, so not the consolidated volume of the source's equity tape.

**Fields** (`marketdata/okx.py` row mapping; `marketdata/contracts.py`):
- `volume_contracts` = OKX `vol`;
- `volume_base` = `volCcy`, in BTC;
- `volume_quote` = `volCcyQuote`, in USDT.

They are kept separate with their currencies. The contract value `ct_val` (BTC per contract) comes from the instrument snapshot. Mark and index candles have no volume. Funding is unrelated.

**Conversions.**
- Contracts and base are proportional through the fixed `ct_val`.
- Quote volume also moves with price. Between two adjacent 15m bars the difference is small but not nil.
- Base volume is the closest analogue of share volume and is the measure the engine already uses (`Bar.vol = volume_base`). **[D]** base volume.

**Causal availability.**
- Only confirmed bars are normalized (`confirm=1`).
- `available_time` = bar close (`okx.completed_1m_bar_available_at_close.v1`).
- A 15m aggregate sums the 1m volumes exactly **only when COMPLETE** (`temporal/engine.py`; README "Records"). An INCOMPLETE aggregate carries only a partial diagnostic.
- So the break bar's and the previous bar's volumes are known at the break-bar close, the same instant B observes the break. Never earlier.

**Aggregation.** A sum over the fifteen 1m trade bars of the 15m interval. The existing participation ratio (latest complete 15m base volume / median of the previous 20) is **descriptive only and never confirms a call** (MP-001 §3, `adviser/core.py`).

**Not available:**
- aggressor side or taker buy/sell volume;
- trade-level classified prints;
- order book depth or changes;
- open-interest changes.

The chosen source needs none of these: it uses aggregate volume only. Sources that need them (delta, absorption, footprint) were not chosen and are not replaced by aggregate volume.

## 4. Candidate (one), reconstructed

**Scope.** B attempts only, at the break bar. Not the retest, not C. The definition is symmetric for B_SHORT **[D]**: the source describes the long side.

**Observations at the break-bar close t_b.** All inputs are COMPLETE 15m trade aggregates known at t_b:
- `vol_b` = base volume of the break bar (the first complete 15m close > U+z);
- `vol_p` = base volume of the complete 15m bar immediately before it.

**Participation reference.** `vol_p`, the source's "previous day" translated to "previous complete 15m bar" **[D: daily → 15m time-scale translation]**.
- The comparison is the source's strict "higher than". No multiplier or threshold is introduced.
- An alternative reference, the box's own bars, matches the "consolidation" narrative but not the explicit text. It is noted as a Director choice point and is not a second candidate.

**Order of events.**
1. The box is frozen.
2. The break bar closes beyond U+z, and B's attempt starts (no issue on the break bar).
3. At the same t_b, compare `vol_b` with `vol_p`.
4. B's retest window, arm, trigger and cancellation run unchanged.

The reading is updated once, at t_b, and never revised by later bars.

**What it may change.** The expectation held during B's wait for the retest:
- **support:** `vol_b > vol_p`, both COMPLETE → the exit has the source's "A-quality" participation item;
- **contradict:** `vol_b ≤ vol_p` → the exit is "marginal" on that item. This is not a re-entry reading;
- **ambiguous / not interpretable:**
  - either aggregate INCOMPLETE;
  - `vol_p` belongs to the move itself (the previous bar touched or penetrated U intrabar);
  - a known clock-time change in activity profile falls between the two bars;
  - the break bar closes far from its high, so the source's price item disagrees.

The last three need definitions **[D]** before they could be operational. They are listed, not defined here.

**What it does not change.** B's predicates, arm, trigger, target, stops, cancellation and C. The response itself stays read by price alone.

## 5. Hand-built examples

Hypothetical numbers, not data. The box is L = 100.00, U = 101.00, M = 100.50, z = 0.10, so U+z = 101.10. Volumes are in BTC; both bars are COMPLETE unless stated otherwise. Only information known at the break-bar close is used.

| | Previous bar (O/H/L/C, vol) | Break bar (O/H/L/C, vol) | Reading at t_b |
|---|---|---|---|
| **Coherent** | 100.70 / 100.95 / 100.60 / 100.90, 120 | 100.90 / 101.42 / 100.88 / 101.38, 310 | Close > U+z, `vol_b > vol_p`. The participation item is supported (and the close is near the high). Expectation: the source's A-quality exit. B still waits for its retest; nothing is issued. |
| **Contrary** | 100.80 / 100.98 / 100.70 / 100.95, 140 | 100.95 / 101.25 / 100.93 / 101.18, 90 | Close > U+z, `vol_b ≤ vol_p`. The item is contradicted: "marginal" in source terms. No re-entry is inferred; B's rules are unchanged. |
| **Ambiguous** | 100.85 / 101.06 / 100.80 / 100.98, 400 (pushed into [U−z, U+z] intrabar, closed inside) | 100.98 / 101.30 / 100.95 / 101.22, 380 | Close > U+z, `vol_b ≤ vol_p`. But the previous bar is already part of the push and both volumes are high against the box bars. The literal reference says "not higher"; a box reference would say "higher". The reference choice decides, so this is **ambiguous**. |

## 6. Conclusion

**Fidelity.**
- Faithful to the source's explicit text: break-bar volume higher than the previous bar, read on the breakout bar.
- Not faithful to:
  - its joint checklist: range expansion and close near the high are left out of B;
  - its time scale and market: equity daily vs BTC 15m perpetual;
  - its practice-based discretionary judgement.
- The consolidation-volume item is not interpretable ("orderly" undefined) and partly redundant with COMPRESSION.

**Possible decisional role.** Only **expectation (aspettativa)**: a quality qualifier of the continuation reading between the break and B's retest.
- Not the wait (attesa): B's window is unchanged.
- Not the opportunity (opportunità): the trigger is unchanged.
- Not a re-entry reading.
- Any decisional use would change MP-001's "descriptive only" participation statement. That is a Director method decision, not taken here.

**Efficacy: not evaluated.** No data was processed. Redundancy with the break bar's own range, and the size and direction of any effect, are unknown.

**Choice.** **The candidate is defined well enough to discuss as development**, limited to the B break bar and the expectation role, with the explicit choices **[D]**:
- daily → 15m translation;
- previous-bar reference;
- base volume;
- symmetric short side;
- the ambiguity definitions.

**Precise blocks for the rest of the question:**
- **response after the exit (retest / re-entry):** procedure not reconstructible, because the source is silent;
- **failed exit / C:** not interpretable, because the source is silent;
- **consolidation volume:** not interpretable, and redundant in intent with the price contraction;
- **ANALISI_EVOLUTA volume:** not reconstructible;
- **anything needing aggressor or order-book data:** data inadequate. Not substituted.
