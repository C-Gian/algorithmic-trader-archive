# A confirmed direction — fixed-geometry barrier reference: registration before tabulation

**Executor registration, 14 October 2026.** Committed **before** any tabulation; the probe has run only on synthetic cases.
- **Authorization.** Astra authorized this descriptive comparison, relayed by the Owner on 14 October 2026.
- **Design.** [A-CONFIRMED-DIRECTION-REFERENCE-PROPOSAL.md](../../A-CONFIRMED-DIRECTION-REFERENCE-PROPOSAL.md) at `b1237f1`. The authorization's precisions prevail over it, notably difference_i = (Y_A − Y_O)/2 and the bounds over the whole valid population.
- **Nature.** A new standardized price probe on exposed development data. It does not rescore any scenario's native promise.
- **Not:** a significance test, tuning, alternative subgroup, profit figure, method change or v0.7 evaluation.
- **Unchanged.** v0.6 and the studies stay frozen.

## 0. Results already known

- **Population size.** 89 first A confirmations in the evaluation window: 28 on the original formulation, 61 on later ones. Warmup: 24.
- **Native terminals of the confirmed scenarios** (A revisions check, `142d376`; expectation check, `41f9edf`):
  - original: 17 destination, 9 V contact, 1 hard deadline, 1 stalled;
  - later formulations: 37, 19, 3, 2.
- **Why the A orientation is largely known in advance.** Its barriers are exactly **B and V**. The v0.6 confirmed hard deadline is **confirmation + 4h**, the same as this probe's horizon. So Y_A is, for most episodes, a re-expression of the known native terminal. It differs where a native terminal (STALLED, others) ended the scenario before the probe horizon, and where the horizon boundary rules differ.
- **What was not known.** No opposite-orientation outcome was computed or seen by the executor.
- **Other known material.** The E exploration, the a2x comparison and the earlier tables of the same journal.

## 1. Inputs (local, outside the Owner stack)

Unchanged from the A revisions check, re-verified **6/6** by [`verify_inputs.py`](verify_inputs.py) → [`inputs_verification.json`](inputs_verification.json):
- `journal.jsonl.gz` SHA-256 `ea3ce99757af41c96fa154f745e06d29c8a1906508089c7e43a051b2899af0f0`: 34,507 entries, frozen v0.6 identity on every record;
- `trade_bars.csv.gz` SHA-256 `06a1102470dd139a1a4a079220725aabb8fe890cc321df1c517ca8941c745abe`: 226,445 admitted trade 1m bars, 2025-07-28T00:00Z → 2026-01-01T06:04Z, 0 missing.

Coverage of every probe window is a registered check: each [t0, t0 + 4h) wholly inside the bars, with no missing interval. Insufficient coverage would be reported, never replaced by a new replay or Owner access.

**Scripts at registration** (SHA-256 of the committed LF bytes):
- `probe.py`: `ffc9833094347ff8eb910bd6a370859cb15ce6582518a1da58e5f67a092694a0`;
- `verify_inputs.py`: `53abc7ad9f5c63201ae2b667ea41fa379b4ed7f7c7739d5a53caafe688c97e51`.

## 2. Population

- **Episodes.** The first, and in v0.6 the only, CONFIRM of every A scenario: one per scenario, original or later formulation, with no selection on call, destination or revision count.
- **Windows.** Evaluation = BIRTH publication in [2025-09-01, 2026-01-01). Warmup births are tabulated separately; a tail birth fails a check.
- **Denominators:**
  - first confirmations = valid geometry + invalid geometry + not evaluable;
  - valid geometry = determined pairs + unresolved pairs.

## 3. Cutoff, geometry and availability

- **Cutoff t0.** The CONFIRM record's publication `clock_time`.
- **P.** The record's `confirmation_close`: the close of the confirming 1m bar named in the record's reason.
  - Check: the bar's close equals P, and the bar ends at/before t0, so it was admitted under the modeled availability `bar + PT0S`.
  - Otherwise NOT_EVALUABLE, with the reason.
- **Other levels.**
  - d = +1 LONG, −1 SHORT.
  - B = the record's `destination`; V = the record's `invalidation_level`, frozen at confirmation.
  - a = d(B − P), b = d(P − V). Both must be **strictly positive**; otherwise INVALID_GEOMETRY, reported with a and b. There is no instantaneous success and no level adjustment.
- **Barriers.**
  - Selected orientation A: favourable P + d·a (= B), adverse P − d·b (= V).
  - Opposite orientation O: favourable P − d·a, adverse P + d·b.
  - These are the same distances mirrored around P, not B and V with only the side flipped.
- **Arithmetic.** Decimal throughout, with the journal and bar precision; no tolerance. A level above P is touched by high ≥ level; a level below P by low ≤ level. These are the engine's inclusive contact rules.

## 4. Time and outcomes

- **First future observable interval.** The trade 1m bar starting at t0. It is complete and admitted at t0 + 1m.
- **Before the cutoff.** A bar ending at/before t0, including the confirming bar, is never an outcome.
- **A bar straddling t0** (start < t0 < end; not expected, because publications are on minute boundaries):
  - each level it touches may lie before or after the cutoff;
  - both possibilities are kept, so this is an ambiguity, never skipped.
- **Horizon.** H = t0 + 4h, fixed, even when the scenario ended earlier; native terminals are kept only as descriptive markers.
  - Bars with end ≤ H are inside. The bar [H − 1m, H) counts, since its contact occurred before H.
  - A bar starting at/after H never counts.
  - A bar straddling H keeps the same two-way ambiguity.
  - Check: H equals the record's `confirmed_deadline`.
- **Intrabar order.** Never inferred. When several levels are touched in one bar, every order of those levels is feasible (equal levels are one event).
- **Unavailable data.**
  - A missing bar lets every still-open orientation become favourable, adverse or stay open.
  - If the data end before H, every open orientation may become favourable, adverse or horizon.

**Per orientation:**

| Outcome | Y |
|---|---|
| Favourable first, inside the horizon | Y = 1 |
| Adverse first | Y = 0 |
| Full horizon observed without favourable contact (adverse also untouched) | Y = 0, category HORIZON_NO_FAVOURABLE_CONTACT, reported separately |
| Ambiguous or incomplete | Y undetermined; reason `AMBIGUOUS_SAME_INTERVAL` / `AMBIGUOUS_STRADDLING_INTERVAL` / `INCOMPLETE_MISSING_INTERVAL` / `INCOMPLETE_DATA_END` |

This is a standardized directional probe. Its result is **not** called a scenario success.

## 5. Single primary result

- **Per pair.** Reference_i = (Y_A + Y_O)/2; Difference_i = (Y_A − Y_O)/2.
- **Shown first:**
  - the population;
  - valid and invalid geometries, with reasons;
  - the categories per orientation;
  - determined and unresolved pairs (A only, O only, both, with reasons);
  - the paired 2×2 table of determined pairs, with categories.
- **Then:** the selected favourable-first count, the opposite favourable-first count, the reference total, and the **mean difference over determined pairs**, exact fraction and percentage points.
- **Bounds.** If valid-geometry pairs remain unresolved, the bounds of the mean difference over the **whole valid population** (denominator = valid geometry) are also reported. Each pair contributes the minimum or maximum of (Y_A − Y_O)/2 over its **jointly feasible** outcomes. These come from a joint walk of both orientations on the same bars, keeping every available constraint: determined values, inter-bar order and shared or equal levels. There is no imputation.
- **What the reference is not.** It includes A and uses the moments A chose. It is not independent and does not evaluate the choice of moments.
- **Descriptive context.** Overlap of the probe windows (counts, opposite-direction overlaps, clusters) and temporal concentration (by month, day, maximum per day). Native terminals are markers only.

## 6. Checks, synthetic cases, execution, amendments

**Checks:**
- one episode per confirmed A scenario;
- no tail birth;
- P = the confirming bar's close, admitted at/before t0;
- H = cutoff + 4h = `confirmed_deadline`;
- every window inside the data, with no missing interval;
- each determined orientation resolved inside its window, or by the horizon;
- the selected barriers are B/V and the opposite barriers are their mirror around P;
- the reconciliations of §2 and of per-orientation sums.

**Synthetic cases.** [`selftest.json`](selftest.json): **32/32**, hand-derived, LONG/SHORT mirrored, with different a and b:
- favourable first; adverse first;
- no contact (horizon);
- two contacts in one bar, including the joint constraint when a = b;
- contacts before the cutoff;
- a straddling cutoff;
- the horizon edge, and a contact after it;
- a missing interval before and after resolution;
- data ending before H;
- a partially determined pair;
- invalid geometries (a = 0, b = 0, a < 0) and P not equal to its bar;
- bounds over the valid population with a partially determined pair;
- overlap.

No product suite.

**Execution.**
- `python probe.py run <run_dir> out/` writes `results.json` and `episodes.csv` (one row per episode with every level, outcome, interval, reason, joint feasible differences, overlap and native terminal marker).
- It is run **once**; reproducibility is then checked by a second run on the same inputs, without the engine.
- Any later correction is an explicit amendment that states which results were visible.
