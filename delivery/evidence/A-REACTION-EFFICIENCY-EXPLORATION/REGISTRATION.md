# A reaction directional efficiency: descriptive exploration of E, September–December 2025 — registration of conventions

**Registered by the executor on 12 October 2026, base `6a0f22ad93fb230f00869c8b6846ede9a77edbc1`, before any outcome existed.** At this commit the v0.6 processing has not been run. No journal, E value, outcome or pair has been produced or consulted. The only data read is listed in §1.

- **Authority.** The orchestrator's assignment, relayed by the Owner on 12 October 2026, authorizes this single descriptive exploration (delivery `6a0f22a` and its completion note). Astra's bounded derogation, relayed by the Owner the same day, authorizes copying the two input artifacts.
- **Unchanged.** Product, v0.6 and HDP-001 stay frozen. The two future studies stay INACTIVE.
- **Review.** Executor registration; the Director's review is pending.

## 1. Inputs, provenance and verification

| Item | Value |
|---|---|
| Pack | `pack-1ae7d36c20adbde0a468a7e0f6d8750a9951aa8e`, preset `btc-2025-09-to-2025-12-continuous-init35d-v1` (preset sha256 `fabd1c55…2dbc`) |
| Pack manifest sha256 | `1bec1f1575306d4444969569675e28bfdc9dac60e2d6f461b283871362221f92` (= the hash registered by Astra) |
| Feed cache | `fc-80221b24abf3a50b764cc873f4a70cc709847a6b`, manifest sha256 `95478a50a732dffe5d8c46a6b1ca23288246a3ce01aaf537f0b64e2e7cef76fa`; 136 partitions, 679,335 events |
| Feed identities | content `feedcontent.v1:f2cf8790b5f12a11c550f707d5f3c25f96358f92febf09db246e8f261de2f028`; ordered-event hash `3bf8e47b018058808d2aafbf397c74cd01880f3a182ce4f6148f07f422ee393d`; availability `feed.modeled.v1(bar+PT0S,funding+PT0S)` |
| Coverage used | trade, mark and index 1m. Initialization [2025-07-28, 2025-09-01): 50,400 minutes. Evaluation [2025-09-01, 2026-01-01): 175,680. Authorized tail [2026-01-01T00:00Z, 06:05Z): 365. Each family complete, 0 missing. No funding events. |
| Provenance | `docker cp` from the Owner volume (`/data/market` in `algotrader-api-1`), source unchanged, at 2026-10-12T15:41:53Z. Copied: the pack manifest and the cache directory only, into the session scratchpad outside Git. No DB, run record, other volume file, acquisition or service change. |
| Verification | [`verify_inputs.py`](verify_inputs.py) → [`inputs_verification.json`](inputs_verification.json): **21/21 checks pass** (see the list below) |

The 21 checks cover:
- manifest hash, id re-hash and schema;
- the cache named by the pack, and its pinned manifest hash;
- the cache identity, re-derived;
- each partition's sha256, size, count and rolling commitment;
- the ordered-event hash, recomputed over every line;
- per-minute coverage of the three windows;
- no gap, quality or out-of-window event;
- agreement with the pack's own coverage rows.

**Prior consultation, declared.** Earlier on 12 October 2026, before the derogation, the executor ran `docker exec` on `algotrader-api-1`:
- It listed `/data/market` and `/data/market/packs`.
- It hashed the pack manifest and printed its metadata: capabilities, coverage counts, windows, identities and sources.
- It listed the cache directory and printed the feed `cache_id` and the cache manifest hash.

No price, run record or DB was read. The verification script reads event families, kinds and times only, and prints or summarizes no price.

## 2. Engine and rules

- **Build.** `6a0f22ad93fb230f00869c8b6846ede9a77edbc1`. Against the frozen v0.6 reference `b47b997ee93513c7a358b49e961020705e4fbb85`, the only difference in `src/algotrader/adviser`, `temporal`, `feed`, `observe/kernel.py`, `observe/feedcache.py`, `observe/state.py` and `corpus/pack.py` is `adviser/live.py` (the live session, not used here). The `temporal` tree is identical (`feb4265a…`).
- **Method.** `btc.context-action.v0.6` / `mp005.rules.v0.6`, implementation `adviser.core.v6`, runtime `algotrader.adviser-runtime.v6`, engine `observe.stream.v7`.
  - Rules sha256 `57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66` and register (canonical) `98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda` are equal to the frozen references in `A-V06-OPERATIONAL-EVALUATION-REFERENCES.md`.
  - Profile sha256 `7c868337…0220296` (PRICE_NET_ONLY, dislocation enabled). Temporal fingerprint `ae8e7ee8…3ecf`. Composite identity sha256 `32356a2521648652e1a65cdecd3a11ec51175d8c560950ed03a8d9f6b554e873`.
- **Processing.** [`run_v06_offline.py`](run_v06_offline.py) runs once, offline. It uses the worker's construction: `temporal_config` with the MP-001 dependencies, `engine_config(…, "v0.6")`, `config_from_engine` (which refuses any other release) and one `Kernel` applying every line, then `Kernel.finish(2026-01-01T06:05Z)`.
  - Initialization and tail are those of the pack (one continuous run, no monthly reset).
  - **No evaluator is instantiated** (runtime evaluator `None`). The existing tests assert professional records digest-identical with and without it. No path or economic record exists.
- **No existing v0.6 record is reused.** None exists locally. Owner DB records are excluded.

## 3. Scripts (sha256 at registration)

| Script | sha256 |
|---|---|
| `verify_inputs.py` | `2ee38bb0c810ee2b826bf28f33a62189c53d3334821d6e2def23783045159ee8` |
| `run_v06_offline.py` | `db1ba15a3483be16658d8d27989bb1b169fef73f680fdcc594edeae259cec56b` |
| `explore_e.py` | `6267e15a9e18fb89ef38c0984a50296777d384312884ee67c78a6b2c595d314e` |
| `../A-REACTION-EFFICIENCY-FEASIBILITY/feasibility.py` (imported, unchanged: `Bar1`, `tq`, `agg15`, `prefix_at`, `outcome`) | `b8df58da3873e46b05d4b4b515116aa4b641e9220fcb51c1d829da45de4bdd14` (commit `6a0f22a`) |

`explore_e.py --selftest` passes 65/65 before registration:
- the 16 feasibility engine paths reproduce E, key and outcome;
- hand-computed Somers' D cases: the worked example, ties, strata never mixed, aggregation before the ratio, non-estimable;
- class edges.

## 4. Conventions (fixed now; not changed after outcomes)

**Population.**
- Every A owner (scenario id `AL-` LONG, `AS-` SHORT) whose BIRTH is published in [2025-09-01T00:00Z, 2026-01-01T00:00Z).
- One observation per owner, at its first ARM.
- No selection by later confirmation, call or entry. REVISE and REARM create no observation.
- Reported:
  - owners never reaching ARM, with their terminal or open state;
  - E not computable, with its status;
  - every later exclusion.

**Cutoff.** The single cutoff is the first ARM publication (`first_arm_at` = `destination_monitoring_from`). It replaced the design's open "fixed age" in the design completion (`25d4bd3`, note §1 and §3), before this exploration. No other cutoff is tried.

**E.**
- **Domain.** q = d × price (d = +1 LONG, −1 SHORT). The origin is the end of the source 15m bar (the bar whose close fired the birth). q0 is its transformed close.
- **Admitted prefix.** Complete 1m trade bars with start ≥ origin, end ≤ cutoff and known_at ≤ cutoff.
- **Formula.** E = (q0 − qn) / Σ|qj − q(j−1)|.
- **Statuses.** VALUE, UNDEFINED_ZERO_DENOMINATOR, INSUFFICIENT_DATA, INCOMPLETE_MISSING_MINUTE (no fill).
- **Precision.** E is kept as an exact rational. Ties are exact equality only; display rounding never creates one.
- **Checks.** Aq and Bq are checked against the BIRTH record.

**Stratum (four fields only; scale S15 frozen at birth).**
1. **Age:** the age at the cutoff in 15m bars.
2. **Phase:** the `phase` of the latest `market_view` published at or before the cutoff clock time, including the ARM dispatch itself (the feasibility convention).
3. **Class of dB/S15**, with dB = Bq − qc.
4. **Class of dP/S15**, with dP = qc − (Aq + z).

qc is the transformed last admitted close at the cutoff.

**Classes:**
- k = floor(x / 0.25), the mathematical floor, so k may be negative;
- class k = [0.25·k, 0.25·(k+1)): lower edge included, upper edge excluded, anchored at zero;
- exact arithmetic;
- no quantiles, no widening, no added control.

**Outcome.** The corrected classifier of `6a0f22a` (`outcome()`). Bq, the premise (complete 15m close_q ≤ Aq + z) and the horizon H = birth publication + 120 min are frozen at the cutoff. Observation starts after the cutoff: no earlier contact is recovered, and the call's own outcome is not used.

| Class | Y |
|---|---|
| B_BEFORE_PREMISE_FAILURE | 1 |
| PREMISE_FAILURE_BEFORE_B | 0 |
| HORIZON_OBSERVED_NO_B (complete coverage) | 0 |
| AMBIGUOUS (CUTOFF / HORIZON) | excluded, counted |
| INCOMPLETE_CENSORED (INTERRUPTED / DELAYED) | excluded, counted |

Engine terminals (context, anchor, confirmation, call, STALLED, release) are annotations: the geometric observation continues. Coverage loss stays incomplete, never a failure.

**Single analysis: Somers' D of Y on E, standard sign.**
- Pairs are formed only within a stratum. Pairs tied in E are excluded and counted. Pairs tied in Y enter the denominator.
- **d = (ΣC − ΣD)/(ΣC + ΣD + ΣT)**, with C, D and T aggregated over strata before the ratio. No mean of per-stratum indices.
- **d < 0 means higher E is associated with less B attainment.**
- No pair with different E means NOT_ESTIMABLE, not zero.

**Reported before the main value:**
- the full population flow, with reconciliation;
- contributing episodes, and episodes without usable comparison;
- C, D, T and the weight of each stratum, including strata without Y variation (their pairs are ties) and strata without E variation;
- temporal concentration (by birth month and ISO week, pairs per episode, the top-5 strata share);
- overlap of observation windows [birth, H), by pair type and side.

The number of pairs is not a number of independent observations.

**Excluded:** significance tests, confidence intervals, economic results, other summaries of the curve, sufficiency thresholds, and any design change after the result.

**Conclusion categories (one, motivated):**
- informative comparison with a descriptive relation;
- comparison scarce or concentrated;
- relation not observed, or opposite to the hypothesis.

Declared limits: R uncontrolled, approximate geometry, dependence and overlap, prior exposure of these months (exposure register rows 1–7 and 9).

**Amendments.** Any change to a script or convention after this registration is appended below, with its time, its reason and whether any output had been consulted. Nothing above is edited.

## Amendments

None at registration.
