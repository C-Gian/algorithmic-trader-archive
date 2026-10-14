# A confirmed direction — fixed-geometry barrier reference (v0.6, Sep–Dec 2025)

**Executor delivery, 14 October 2026.** The Director's review is PENDING and separate.
- **Design** at `b1237f1`, with the authorization's precisions prevailing. **Registration** committed before tabulation at `6f3ac03` ([REGISTRATION.md](REGISTRATION.md)). No amendment.
- **Nature.** A standardized directional price probe on exposed development data. It is **not** a scenario success measure.
- **Not:** a significance test, tuning, alternative subgroup, profit figure, method change or v0.7 evaluation.
- **Frozen.** v0.6 and the studies are unchanged.

**Already known before the calculation** (registration §0):
- the population size: 89;
- the native terminals of the confirmed scenarios;
- the A orientation's barriers are B and V over the same 4h as the native confirmed deadline, so Y_A largely re-expresses known terminals.

The opposite orientation had not been computed.

## 1. Inputs and probe

**Inputs.** The local 12 October v0.6 journal and trade 1m bars, re-verified **6/6** ([inputs_verification.json](inputs_verification.json)). Every probe window [t0, t0 + 4h) lies inside the bars with **no missing interval**.

**Geometry** (Decimal, no tolerance):
- **Cutoff t0** = the publication of the scenario's first, and only, CONFIRM.
- **P** = the record's confirmation close, checked equal to the close of the confirming 1m bar, admitted at/before t0.
- **a = d(B − P), b = d(P − V)**, both > 0 required.
- **Barriers.** Selected A: favourable P + d·a (= B), adverse P − d·b (= V). Opposite O: favourable P − d·a, adverse P + d·b.

**Observation.**
- On the complete 1m bars starting at t0, up to and including the bar ending at H = t0 + 4h. H equals each record's `confirmed_deadline`.
- No intrabar order is inferred.
- Straddling and missing intervals are kept undetermined.

## 2. Results, in the registered order

**Population and geometry**

| | Evaluation | Warmup (separate) |
|---|---|---|
| First A confirmations (one per scenario) | **89** (54 LONG, 35 SHORT) | 24 (9 LONG, 15 SHORT) |
| Not evaluable (P / bar / levels) | 0 | 0 |
| Invalid geometry (a ≤ 0 or b ≤ 0) | 0 | 0 |
| **Valid geometry** | **89** | 24 |

**Geometry description** (not an outcome split):
- evaluation a/b: median 0.748, range 0.043–3.994; 58 with a < b, 31 with a > b, none equal;
- warmup: median 1.024.

**Outcomes per orientation** (valid geometry):

| | Selected A | Opposite O | *Warmup A* | *Warmup O* |
|---|---|---|---|---|
| Favourable first (Y = 1) | 55 | 47 | 9 | 17 |
| Adverse first (Y = 0) | 30 | 40 | 14 | 6 |
| Full horizon without favourable contact (Y = 0, own category) | 4 | 2 | 1 | 1 |
| Undetermined (ambiguous / incomplete) | 0 | 0 | 0 | 0 |

**Pairs.** **89 determined, 0 unresolved** (warmup: 24 and 0). No same-interval ambiguity, straddle, missing bar or data-end case occurred. Since no valid pair is unresolved, the bounds over the whole valid population coincide with the determined result and are not reported separately.

**Paired 2×2** (determined pairs, evaluation):

| | Y_O = 1 | Y_O = 0 | Total |
|---|---|---|---|
| **Y_A = 1** | 22 | 33 | 55 |
| **Y_A = 0** | 25 | 9 | 34 |
| **Total** | 47 | 42 | 89 |

Categories inside the cells:
- (1,0): 32 adverse-first and 1 horizon on O.
- (0,1): 25 adverse-first on A.
- (0,0): 5 adverse/adverse, 3 A horizon with O adverse, 1 horizon/horizon.

*Warmup:* (1,1) 5, (1,0) 4, (0,1) 12, (0,0) 3.

**Primary result**, on the 89 determined pairs:
- selected favourable-first: **55**;
- opposite favourable-first: **47**;
- reference total Σ(Y_A + Y_O)/2 = **51** (mean reference 51/89 = 57.30%);
- **mean difference Σ(Y_A − Y_O)/2 / 89 = 4/89 = +4.49 percentage points.**

These are the 33 − 25 discordant pairs, halved and averaged.

*Warmup, separate:* 24 pairs; 9 against 17; mean difference −1/6 = **−16.67 points**.

## 3. How to read it, and what it is not

**What the number says.** Under this fixed probe, on these 89 dependent observations, the orientation A selected reached its favourable barrier first a little more often than the uninformed 50/50 reference built at the same moments and distances. The warmup sample points the other way. No significance or interval is computed, by design.

**Why it is not independent evidence:**
- **The reference includes A and uses the moments A chose.** It does not evaluate the choice of moments, only the orientation at them.
- **Y_A was largely known in advance.** Native terminal markers against the A category:

  | A category | Native terminal | Episodes |
  |---|---|---|
  | Favourable | DESTINATION_REACHED | 54 |
  | Favourable | STALLED | 1 |
  | Adverse | INVALIDATED (V) | 28 |
  | Adverse | STALLED | 2 |
  | Horizon | TIME_EXPIRED | 4 |

  The only new element is the opposite orientation.
- **Geometry.** The probe fixes a and b per episode, but the a/b mix (mostly a < b) is the one A's levels produced. A pair's outcome depends strongly on it, for both orientations alike.

**What it is not:**
- not a scenario success rate;
- not a profit, a calibrated probability or a call or entry evaluation;
- not a generalization beyond Sep–Dec 2025;
- not evidence for v0.7;
- it must not be mixed with the native-lifecycle counts of earlier studies.

**Dependence.** Successive and overlapping windows are not independent experiments (§4).

## 4. Overlap and temporal concentration (evaluation)

- **Overlap.** 17 of 89 windows overlap at least one other: 16 overlap one other, 1 overlaps two. **None** overlaps an opposite-direction window. That gives 80 clusters of overlapping windows: 72 single, 7 pairs, 1 of three.
- **Calendar spread.** Cutoffs by month: September 25, October 19, November 20, December 25. They fall on 66 distinct days, at most 3 per day, and 3 days have 3.
- **Warmup.** 24 cutoffs in August on 17 days; 4 overlapping windows.

Per-episode detail: [`out/episodes.csv`](out/episodes.csv). It has one row per first confirmation with:
- cutoff, cursor and horizon;
- P and its bar, B, V, a, b;
- both orientations' barriers, Y, category and resolving interval;
- the pair, reference, difference and jointly feasible differences;
- the overlap count and the native terminal marker.

## 5. Checks and reproducibility

- **Checks: 7/7 pass** in `results.json`:
  - one episode per confirmed scenario;
  - no tail birth;
  - P = the confirming bar's close, admitted at/before t0;
  - H = t0 + 4h = `confirmed_deadline`;
  - full window coverage with no missing interval;
  - every determined outcome resolved inside its window or by the horizon;
  - A barriers = B/V, with O as their mirror around P.
- **Reconciliations:** 5/5 per window.
- **Synthetic cases:** **32/32** ([selftest.json](selftest.json)).
- **Reproducibility.** A second run on the same inputs, without the engine, gave identical hashes:
  - `results.json` `36c0d7bd…6fa9`;
  - `episodes.csv` `db3933f4…9936`.
- **Script.** `probe.py` SHA-256 `ffc98330…94a0`, unchanged since registration.

**Not run:** product suites and CI (Owner-operated: PENDING / NOT CHECKED).


## Later annotation — branch closed (14 October 2026)

The text above is the original delivery, unchanged. Astra's instruction relayed by the Owner on 14 October 2026 (assignment "A confirmations → entry opportunities") states that the E exploration, the a2x branch and the confirmed-direction comparison are **closed**. No further execution, adaptation or follow-up study is authorized from this branch; v0.6 stays unchanged and future studies stay INACTIVE.
