# Complete professional breakout setup (Bonde checklist, Kullamägi passages) — translatability check

**Executor delivery, 14 October 2026.** The Director's review is separate and PENDING. Astra's authorization, relayed by the Owner. Documentary only.

**Not done:** no implementation, acquisition, historical processing, backtest, new tabulation or product suite. v0.7 and the frozen studies are unchanged. The conclusions of [PRICE-VOLUME-SEMANTIC-FEASIBILITY.md](PRICE-VOLUME-SEMANTIC-FEASIBILITY.md) §7 stand: this check concerns the joint setup, not the single volume measure.

**Question.** Does the complete checklist let one recognize a situation, form an expectation, and distinguish entry, wait and renunciation with the information available at that moment?

**Labels:**
- **[S]** rule attributable to the source;
- **[I]** our interpretation;
- **[C]** additional choice that would be indispensable;
- **[U]** not specified.

## 0. Sources and verification

Only the sources already identified were used, and no new search was made.

| Source | Original | Verified |
|---|---|---|
| **K** — Kullamägi interview, Schwager, *Market Wizards: The Next Generation* (LIB-005) | Owner corpus PDF, sha256 `079c451f…3568` | pdftotext of PDF pp. 27–32, read in full: momentum-burst section pp. 29–31, the market filter pp. 31–32, the PTON example p. 30 |
| **B1** — Bonde, "How to Identify good momentum burst and make millions", 4 Jan 2014 | Copy downloaded during the price–volume step (14 Oct 2026, 15:07 CEST) from the URL recorded there; sha256 `e58893ac…87e2` | Post body text, read in full |
| **B2** — Bonde, "How to identify the A quality setup", 14 Jan 2014 | As above; sha256 `aca4cc7a…494e` | Post body text, read in full |

**Limits of the verification:**
- **Bonde copies.** They are not re-downloaded. They are kept in the session scratchpad only, not in the repository: the text is third-party, and `source_notes/` stays unchanged.
- **Charts not examined.** The posts' charts (images) and the PTON chart in K are not used.
- **Sidebar links not read.** Bonde posts listed in the sidebar (e.g. "Right entry for swing trade", "How to swing trade using momentum burst") were not read. They are outside the authorized sources.
- **Editorial note.** The bracketed ADTR definition in K (p. 30) is the author's (Schwager's) editorial note, not Kullamägi's words.

## 1. Original market, scale and universe

| | K | B1/B2 |
|---|---|---|
| Market | US equities ("especially small caps and mid-caps", p. 29) | US equities (float, price in dollars, "8000 stocks … in Worden universe") |
| Universe and selection | **Leading stocks:** "scan for the 1% or 2% stocks with the largest upmoves in the past one, three, and six months" (p. 29), a cross-sectional rank | Scans ("4% scan or $ breakout scan") over a broad universe, narrowed to a watchlist of "50 or 200 stocks". Low float (<25M, <10M) and low price (<$5) favoured |
| Scale | Daily structure: consolidation 1–3 weeks, hold 3–5 days, ADTR, 10/20-day averages. The entry is intraday on the breakout day (opening range, first 5/30/60-min bar) | Daily bars throughout ("day", "breakout day", "3 to 20 days") |
| Market regime | **Required:** no breakout trades when "the market" is in a downtrend. Kullamägi's filter is the 10-day and 20-day moving averages; Bonde uses a breadth model (p. 31) | Not in B1/B2 |

## 2. Reconstructed decision chain (one), step by step

**Concordance** is marked =, **difference** ≠, and a link that would be **ours** →.

### Step 1. Context and formation before the break

**Kullamägi:**
- [S] a stock in an uptrend, then a sideways consolidation (p. 29);
- [S] a leading stock: top 1–2% of movers over 1, 3 and 6 months;
- [S] preferably shorter consolidations, about 1–3 weeks;
- [S] the market not in a downtrend (10/20-day averages; p. 31).

**Bonde:**
- [S] "3 to 20 days consolidation", with a "series of narrow range days" (B1);
- [S] a burst "preceded by a 3 plus days of period where there was no momentum burst" (B2);
- [S] "pre breakout there should not be many 4% breakdowns", "linearity in prior action", an orderly correction (B2);
- [S] "Stock is not extended. First or second breakout at start of an up trend is preferred"; avoid "drunken man walk" volatility (B1).

**Concordance and differences:**
- = a short sideways consolidation within an uptrend.
- ≠ K selects the strongest recent movers; B prefers an early, not extended trend.
- → reconciling "leading" with "not extended" would be ours.

**Not specified:**
- [U] the definitions of uptrend, sideways consolidation and its bounds, narrow-range day, orderly, linear and extended;
- [U] which index or market K's filter uses;
- [U] B's "4% breakdown" outside the scan names.

### Step 2. Joint conditions (price, volume, others)

**Kullamägi:**
- [S] the price breaks above the consolidation;
- [S] consolidation "preferably on reduced volume";
- [S] the stop distance condition (step 5).
- Nothing on breakout-day volume or the close.

**Bonde (B2's guideline list; B1's "characters"):**
- range expansion on the breakout day;
- higher breakout-day volume (B1: "higher than previous day");
- the day before narrow-range or negative;
- few 4% breakdowns;
- linearity;
- an orderly correction;
- "preferably orderly" consolidation volume;
- a close near the high.

B1 marks the close near the high "(preferred)". B2 says "should": the two posts differ on its status.

**Concordance and differences:**
- = consolidation volume should be subdued or orderly.
- ≠ B adds breakout-day items that K does not mention.
- → joining K's entry with B's breakout-day items would be ours.

**Not specified:**
- [U] the measure and reference of "range expansion" (B2's example "4% breakout" is a scan name; its definition is not in B1/B2);
- [U] "near high";
- [U] "orderly".

### Step 3. Status of each element

**Required:**
- **K:** the leading stock ("one of the conditions for the trade", p. 30); the uptrend, consolidation and breakout; the market filter ("You need some kind of filter that will keep you out of the market when it is in a downtrend", p. 31); the stop at the day's low within ADTR (step 5).
- **B:** no item is individually required. They are guidelines of an overall "A quality" judgement, with "slight variation of this basic setup idea" admitted (B2).

**Qualifiers:**
- **K:** none stated.
- **B:** all the guideline items, judged jointly.

**Preferences:**
- **K:** reduced volume; 1–3 weeks; small and mid caps.
- **B:** a close near the high (B1); orderly volume; the first or second breakout; low float; low price.

**Discretion:**
- **K:** the entry window ("opening range or … first 5-, 30-, or 60-minute bars", with a stated trade-off); 10- or 20-day averages; the partial-profit amount.
- **B:** trained recognition ("procedural memory"; "don't settle for marginal setups").

The composite decision is the source's **holistic judgement**. No source gives weights or compensation between items, and none is introduced here.

### Step 4. Expectation formable before the sequel

**Kullamägi:**
- [S] "most of the move is over in three to five days" (Bonde's finding, as reported, p. 29);
- [S] "the success rate will be well below 50%. The trading strategy works on balance because the gains on winning trades will be far larger than the losses" (p. 30).

**Bonde:**
- [S] "Stocks move in 8 to 40% bursts" over "3-5 days" (B1);
- [S] better setups "work instantly" and allow a "logical and tight stop" (B2).

**What can be formed:**
- [I] An expectation of **payoff shape**: frequent small losses, rare quick bursts within 3–5 days.
- It is not a probability of continuation for one case.
- = both sources share the 3–5 day horizon.

### Step 5. Entry, wait, renunciation

**Entry:**
- **K** [S]: "a price move above the opening range or above the high of the first 5-, 30-, or 60-minute bars". Intraday, on the breakout day.
- **B2** [S]: "enter in anticipation or put an alert and enter as soon as price exceeds certain level". Intraday.
- [U] K does not say how the opening-range trigger relates to the consolidation high.
- [U] B does not define the "certain level".

**Wait:**
- **K** [S]: a longer entry window means a "worse … entry price, but the lower the risk of entering on a false breakout". This is an explicit trade-off left to choice [C].
- **B** [S]: an anticipation watchlist.
- [U] Neither source sets an expiry of the setup while the stock keeps consolidating.

**Renunciation:**
- **K** [S]: "If the low is more than the ADTR below the current price, then I wouldn't take the trade" (p. 30). He also stays out when the market is in a downtrend.
- **B** [S]: "Do not get into the habit of buying marginal setups. Wait for a A quality setup" (B2). Marginal is a holistic judgement [U as a rule].

### Step 6. Invalidation, destination, exit, time validity

**Kullamägi:**
- [S] stop at "the low of the day", no wider than ADTR;
- [S] "take a partial profit during the first three to five days and move the stop up to break even on the remainder … a close below either a 10-day or 20-day moving average as a trailing stop" (p. 30).
- [U] the amount and trigger of the partial profit.
- [C] 10 or 20 days.
- [U] the ADTR period: only the editor's examples.

**Bonde:**
- B1/B2 give no stop location, target or exit.
- The 3–5 day horizon is descriptive.

**Differences:** ≠ K's exit is the only documented one.

## 3. Causal order

**At an intraday entry** (K's window, or B's alert), the following can be known:
- **Pre-open** (prior close or earlier): leadership rank, uptrend, consolidation, prior-day narrow or negative, prior 4% breakdowns, linearity, consolidation volume, ADTR, market filter.
- **Intraday:** the price crossing the entry level; the day's low and range **so far**; the cumulative volume so far.

**Known only at the daily close:**
- the **close near the high**;
- the final **range expansion**, if measured on the daily bar;
- a breakout-day volume that is **not** higher than the previous day's.

"Higher" can be known intraday once the cumulative volume exceeds the prior day's total, because volume only accumulates. "Not higher" cannot be known before the close.

**Consequence.** Bonde's breakout-day items qualify the **completed** breakout day. A day that satisfies them at the close cannot justify an earlier intraday entry.
- The consulted texts do not say whether the entry should:
  - wait for the close;
  - be taken the next day (B2's morning scans could mean either);
  - be taken intraday, with the breakout-day items then used later, for example to hold or exit (not stated).
- K's chain is causal (pre-open context + intraday trigger + ADTR check), but it does not use Bonde's breakout-day items.
- **[U] decisive:** the moment at which the complete checklist is applied, relative to the entry.

## 4. Transfer to BTC intraday

What the transfer would require, and why it is not justified by the sources:
- **Cross-sectional leadership.** K's leading-stock rank (top 1–2% of a stock universe) and B's scans and watchlist select **among many instruments**. One instrument, BTC-USDT-SWAP, has no such universe. Replacing this with a BTC momentum or strength measure would substitute a required condition. **Not justified.**
- **Market regime.** K's filter applies to "the market" (equities), separate from the traded stock. With BTC there is no stated separate market. Using BTC's own averages would be our substitution [C, not justified].
- **Scale.** The structure is daily: weeks of consolidation, days of holding, daily ADTR and averages. Only the entry timing is intraday. Rescaling to 15m bars (hours instead of weeks) has no basis in the sources. Keeping the daily scale makes "intraday" apply to the entry only.
- **Session.** The opening range, the first 5/30/60-min bar and "low of the day" presuppose an exchange session. BTC trades 24/7; a day boundary (e.g. 00:00 UTC) would be our choice [C, not justified].
- **Equity attributes.** Float, share price below $5 and "Worden universe" have no BTC meaning. Dropping them changes the setup the authors judged.
- **Breakout-day volume.** On BTC this would be single-venue perpetual volume (price–volume step §3), not consolidated equity volume.

## 5. Manual joint examples

Original market and scale (a hypothetical US stock XYZ, daily structure, intraday entry), because the transfer is not justified (§4). The decision moment is 10:31 ET, just after XYZ trades above its first 60-minute bar high. Only information known then is used.

**Shared pre-open context, all hypothetical:**
- XYZ in the top 1% of 3-month movers;
- the market's 10-day and 20-day averages both rising;
- a 12-day sideways consolidation between 18.40 and 20.00 on declining volume;
- the prior day narrow range;
- ADTR 0.90;
- prior-day volume 0.8M.

**A. Checklist satisfied as far as knowable.**
- At 10:31: open 20.10, first-hour high 20.60, low so far 19.95, cumulative volume 1.1M.
- K: entry above 20.60 (60-min window chosen [C]); stop 19.95, distance ≈ 0.66 < ADTR, so **entry reconstructible**.
- B: volume is already higher than the prior day (known). The close near the high and the final range are **unknown**.
- At 10:31 the setup is "satisfied" only on the pre-open and known intraday items. Whether it is A quality cannot be established before the close, so the entry is K's, not the complete checklist's.

**B. One item missing.** As in A, but the prior day was a wide-range up day: neither narrow nor negative, known pre-open.
- K: unaffected; **entry** as in A.
- B: one guideline is unmet. Whether this is a tolerated "slight variation" or a "marginal" setup to skip is the author's holistic judgement. **Entry versus renunciation is not reconstructible from B.**

**C. Elements in contrast.**
- At 10:31: price above the first-hour high 20.85, low so far 19.70 (distance ≈ 1.15 > ADTR 0.90), cumulative volume 1.4M, range so far 1.15.
- B's known items look favourable: higher volume and a wide range.
- K: **renunciation** (stop distance > ADTR; p. 30), documented and causal.
- B gives no stop rule, so no B decision.
- K says nothing about re-entry later the same day [U]. Any joint resolution would be ours.

## 6. Decision

**The decisive step is missing.** The complete checklist cannot be turned into a causal chain of entry, wait and renunciation from the consulted sources. This holds in the original market; the transfer would be a separate, independent block.

1. **Main block: when the checklist applies relative to the entry.**
   - Bonde's breakout-day items (close near the high, range expansion, a volume that is not higher) are known only at the daily close.
   - Both consulted entries (K's opening-range / first-bar trigger, B2's price alert) are intraday and earlier.
   - B1/B2 do not state whether the entry waits for the close or the next day, or whether those items act after an intraday entry.
   - Whether one missing item means renunciation is left to trained judgement.
   - K's chain is causal and documented (context, trigger, ADTR renunciation, stop, partial exit and trailing), but it is **not** the complete checklist. It still leaves undefined the consolidation, uptrend, the trigger-to-consolidation relation, the partial-profit rule and the market index.
2. **Independent block for BTC intraday.** Two required conditions have no representation for a single 24/7 instrument without substitution: the cross-sectional leading-stock selection, and the separate market-regime filter. The daily scale and session-based entry also have no source-justified translation.

**Material that would be needed:**
- **For block 1:** Bonde's own written entry procedure for momentum bursts. This means when the entry is taken relative to the breakout-day close, and how the breakout-day items are applied (e.g. his posts on entry, not read here), or the author's clarification. Also Kullamägi's definition of how the opening-range trigger relates to the consolidation high.
- **For block 2:** a professional description of the setup applied to a single continuously traded instrument, without cross-sectional leadership and on an intraday scale. Neither consulted source provides one.

**No candidate is proposed and no gap is filled with our formulas.** v0.7 is unchanged. **This step is concluded.**
