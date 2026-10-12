# Live adviser v0.6 — integrated synthetic acceptance check (one episode, real path)

Base `115b9b5c9f8b684da9e07855979296635c682844`. **Executor delivery — READY FOR DIRECTOR REVIEW; not the Director's final acceptance.**

**Technical proof with no economic meaning.** The synthetic tape was designed to satisfy the frozen v0.6 rules. It shows that the parts of the product work together. It is not evidence of market prediction, profit or general usability. There is no real feed, no Owner data, no acquisition and no economic test. v0.6 and HDP-001 are frozen; the studies are INACTIVE.

Test: [`tests/e2e/test_live_episode_e2e.py`](../../../tests/e2e/test_live_episode_e2e.py). Record: [`e2e-live-episode-v06.json`](e2e-live-episode-v06.json). Six screenshots, listed below.

## Answer

Yes, within this synthetic episode. Starting from the cockpit's ordinary Start (method v0.6), the product does three things:
- It builds its conditional expectation from the admitted live observations.
- It keeps waiting while a necessary v0.6 condition is unmet, and it issues the call in the dispatch where that condition is met.
- It serves and shows the same call's updates and conclusion consistently in the engine, the journal, the API and the cockpit.

## Coverage reused and the gap completed

**Tests that prepare operational states directly** (they do not prove the path from the data):
- The [call-updates episode generator](../LIVE-CALL-UPDATES-EPISODE/generate_episode.py) and the cockpit generators feed in-memory views to `live_status` through a fake connection, and they insert the journal directly.
- `test_live_proposal_e2e`, `test_live_cockpit_layout_e2e` and `test_live_continuity_e2e` present states that are prepared in advance.

**Tests that generate the episode from the data through the normal entry point:**
- `test_adviser_live_db` uses the real `LiveAdviserWorker` with the offline OKX fakes, on the v0.2 tape.
- `test_live_restart_e2e` uses the same worker with the v0.6 tape, then the API and the cockpit. It covers Start → AVAILABLE, then Stop/Start. Its only conclusion is the restart gap.

**Missing:**
- the expectation phase and the waiting phase before availability (the discriminating check);
- an ordinary update of the call;
- a method conclusion of the same call;
- all of these through the worker, the API and the cockpit.

**Completed in the existing framework:**
- One test reuses the stack, the browser, `_run_worker`, `FakeClock`, `ws_messages` and the MP-005 tape.
- `FakeWS` gains one optional `until` hold, which only controls when scripted pushes are released. It defaults to no hold, so existing tests are unchanged.
- The tape is the restart test's tape plus the three minutes of the call-updates episode.

**Not done:**
- No state, call or guidance is injected.
- No gate, readiness or timestamp is altered.
- No new engine, environment or infrastructure is added.
- No product code is changed.

## Discriminating condition (one check, same episode)

v0.6 keeps the MP-004 RETURN response. After the return reference is prepared (04:04:01; reference bar [04:03,04:04), H0 100008, L0 99990), a call is possible only on **"a later complete 1m close >= 100008.1 with low >= 99990"** (local recovery).

| Moment (UTC) | Bar decided | Condition | Served (API) | Cockpit |
|---|---|---|---|---|
| 04:06:01 | [04:05,04:06): close 100000, low 99990 | not met | `call: null`, scenario A CONFIRMED, `WAIT_RESPONSE`, `bars_checked` 2; MarketView UP **conditional** | WAITING "In attesa — nessun ingresso proposto"; "Rialzo (condizionale)"; "serve una ripresa locale del prezzo"; no band |
| 04:07:01 | [04:06,04:07): close 100012, low 99992 | met | call r0 **AVAILABLE**, admissible 99900–100014.4, target 100700.0, stop 99700.0; MarketView still conditional | AVAILABLE, band 99.900 – 100.014,4 |

The call record's `issue_reference` is 100012 (the VALID close). Its `trade.1m` dependency is `obs@04:06:00Z`, known at or before 04:07:01. The journal has no `call` before 04:07:01.

## Evidence chain (data → decisions → persistence → API → UI)

- **Start and readiness.**
  - The cockpit selects v0.6 and clicks Start. The API queues the session (`config.method` v0.6), and the worker claims it.
  - The 96 h catch-up writes only RECONSTRUCTED records: no `call` or `entry_attempt`, and no conditional MarketView.
  - The API serves WARMING_UP, not current. The cockpit shows WAITING with "Sessione non corrente".
  - LIVE activation comes at 03:17:01.
- **Expectation.**
  - Scenario A LONG is born at 03:30:01 and armed at 03:45:01.
  - The first conditional MarketView (UP, principal = A) is LIVE at the ARM instant (03:45:01). A is confirmed at 04:02:01.
  - Every `market_view`, `scenario` and `entry_attempt` record has its dependencies known at or before its own clock time.
- **Call.**
  - One `call` record: `call-AL-2025-09-01T04:07:01+00:00-05a41e24819a`, run `live-20250828T0316-…` (same run and session throughout).
  - Its subject is `<scenario>#entry`, and `scenario_id` is A.
  - `issued_at` = `published_at` = journal clock time = 04:07:01.
- **Update (same call).**
  - r1 UNVERIFIED `QUOTE_STALE` at 04:07:05.750001. This is the 5 s quote-freshness timer, because the fakes send one quote per minute.
  - r2 CLOSED (`PRICE_OUTSIDE_STRUCTURAL_AREA`, `REWARD_RISK_BELOW_MINIMUM`) at 04:08:00.5, thesis ONGOING.
  - The API at 04:08:01 serves r2. The cockpit shows CLOSED, the reasons in Italian, "Tesi: ancora valida", no band.
- **Conclusion (same call).**
  - r3–r6 alternate between UNVERIFIED (stale quote) and CLOSED.
  - r7 is TARGET_REACHED at 04:10:01, reason `CERTIFIED_TARGET_CONTACT:…obs@04:09:00Z` (bar high 100720 ≥ target 100700.0). It is the only terminal.
  - Revisions are contiguous (1–7), their times never decrease, `published_at` equals the journal time, and no revision after r0 is AVAILABLE.
  - Journal seqs are contiguous, and there is one run.
- **API.**
  - At the end: `call: null`, with `recent_calls` holding TARGET_REACHED at 04:10:01.
  - The call-detail route returns exactly the 7 journal revisions.
  - Alerts: NEW_CALL, ENTRY_UNVERIFIED, TERMINAL, all for this call.
- **Cockpit.**
  - "Conclusa — target raggiunto", "100.700 — raggiunto", and "La successiva aspettativa (rialzo) non prolunga questa call".
  - The history opened from *What changed* shows the same call and run, terminal.

**Expectation vs availability.**
- The conditional expectation (UP) exists from 03:45:01.
- Entry is AVAILABLE only from 04:07:01 to 04:07:05.75.
- The expectation is unchanged after the conclusion, and the cockpit says it does not extend the call.

## Screens actually produced (1440×1000, Europe/Rome = UTC+2)

| File | Phase | Identity | Time (UTC) |
|---|---|---|---|
| `episode-0-warming-up.png` | WARMING_UP, catch-up, not current | session, run | fake clock 03:16:30 |
| `episode-1-expectation-waiting.png` | conditional expectation, WAITING (condition not met) | run, scenario A | 04:06:01 |
| `episode-2-entry-available.png` | call r0 AVAILABLE | call id | 04:07:01 |
| `episode-3-update-entry-closed.png` | same call r2 CLOSED, thesis ongoing | call id | 04:08:01 |
| `episode-4-conclusion.png` | same call TARGET_REACHED | call id | 04:10:01 |
| `episode-5-call-history.png` | recorded history of the call | call id, run | — |

## Checks actually run

Disposable PostgreSQL 18.6 container on port 55439, removed afterwards. The Owner stack was untouched. UI rebuilt with `npm --prefix web run build`.
- The new E2E took about 21 s per run.
  - The final version passed twice: the evidence run and the regression run.
  - Three earlier passes ran a version identical except for the JSON evidence record.
- Regression run, **57 passed**:
  - `test_adviser_live_db`, `test_live_call_history_db`, `test_adviser_correction_live_db`;
  - `test_mp005_live`, `test_mp004_live`, `test_adviser_live`, `test_adviser_correction_live`;
  - E2E `test_live_restart_e2e`, `test_live_episode_e2e`, `test_mp005_e2e`, `test_live_proposal_e2e`, `test_live_continuity_e2e`.
- No full suite was run. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Observed, not changed (outside the authorized integration scope)

- **Alert and timeline times.** They come from the database's wall clock, not the synthetic clock. This was already reported.
- **Condition line after issue.** Once the call is issued, and after its conclusion, "Condizione ancora necessaria" reads "non indicata dal sistema", because the scenario has no waiting state.
- **Market reading after the conclusion.** After TARGET_REACHED the scenario stays the principal one, and the reading stays "Rialzo (condizionale)". This is engine semantics, unchanged. The cockpit separates it from the concluded call.
- **Band after CLOSED.** After CLOSED, the API still serves the call's last `admissible_bounds`. The cockpit shows them only in the details, as "Ultima fascia calcolata (non utilizzabile ora)", never as the band.
- **Stale-quote revisions.** The one-quote-per-minute fakes produce UNVERIFIED (stale quote) revisions between closes. This is engine behaviour under that feed density, not a defect.

No problem was found in the frozen rules, and no integration correction was needed.

## Limits

- One synthetic LONG episode. There are no SHORT or variant batteries, by assignment.
- Mocked OKX services.
- Worker takeover is not exercised.
- The `until` hold controls only when scripted pushes are released, not processing.
