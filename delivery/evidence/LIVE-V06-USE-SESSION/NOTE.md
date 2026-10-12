# Live adviser v0.6 — Owner use session (one session, two hours from Start)

**Executor record, not the Director's acceptance.** This is a real use session of the live adviser by the Owner (Gian), authorized by the orchestrator on 12 October 2026. It is not a study, not an economic test and not evidence of market prediction or profit. v0.6 and HDP-001 are frozen; the studies (HDP-001, A v0.6) stay INACTIVE and this session is not part of them.

**Status (2026-10-12):** session held and stopped by the Owner. Executor report delivered (§2–§7); the Director's final acceptance is pending. Exposure register: row 10.

## 1. Preparation (executor, 2026-10-12, before Start)

| Item | Verified value |
|---|---|
| Checkout | `main` at `87322acd4a74f8aa875312c380408f7d09369823`, clean, equal to `origin/main` as already known locally (no pull or fetch) |
| CI on that SHA | green, as reported by the Owner (not queried by the executor) |
| Build served | `/api/health` → `code_version` `87322acd4a74f8aa875312c380408f7d09369823+image`. Before preparation the stack served `eab7d23…+image`; the image was rebuilt from the checkout with the README upgrade procedure (`docker compose build`, `docker compose stop api worker recorder observer corpus adviser`, `docker compose up -d`). Migration exit 0. No volume touched. |
| Services | `db` (unchanged, kept running), `migrate`, `api` (healthy, `127.0.0.1:8000`), `adviser`, plus the ordinary idle `worker`, `recorder`, `observer`, `corpus`. No replay, corpus job or recording queued or running. |
| Method | `v0.6` offered by `/api/adviser/methods`: model `btc.context-action.v0.6`, rules `mp005.rules.v0.6`, rules SHA-256 `57bf2309…2e66`, register SHA-256 `98ef101e…5bda`, implementation `adviser.core.v6`, status ENGINEERING_REVIEW_PENDING, economic usefulness UNVALIDATED. The DELTA file `MP-005-V06-INITIAL-RESPONSE-INCOMPATIBILITY.md` and `MP-005-DIRECTOR-CLOSURE.md` in the checkout hash (LF) to the values the build declares. **The cockpit preselects v0.2: v0.6 must be chosen before Start.** |
| Instrument | Hard-wired in the live adviser: `BTC-USDT-SWAP` (trade and mark 1m candles), index `BTC-USDT` (index 1m candles), public ticker of `BTC-USDT-SWAP`. REST base `https://www.okx.com` (no `ALGOTRADER_OKX_REST_BASE_URL` override in the Owner's environment). One public metadata request (`/api/v5/public/instruments`, `BTC-USDT-SWAP`) answered `code 0`; no market data was requested by the executor. |
| Pre-existing live state | `adviser_live_sessions` 0 rows, `adviser_live_state` 0 rows, `adviser_input_tape` 0 rows, `adviser_alerts` 0 rows, no `live-*` run in `adviser_journal`. Start will therefore open a **new continuity run**: no restore, no consultation of an earlier live run, no recovery of an earlier period. Nothing was deleted and no continuity rule was changed. |

### Initialization interval the ordinary catch-up will read

With no saved state, the session's coverage starts 96 h before Start (`new_epoch(now − 96 h)`), and the bounded catch-up reads exactly the complete minutes **[floor_minute(Start) − 96 h, floor_minute(Start))** for the three candle families, through paged read-only history requests bounded below at the interval start (no page reaches earlier). These minutes are RECONSTRUCTED (modeled availability, never live advice); minutes the archive cannot fill stay explicit MISSING.

Example: Start at 2026-10-12 08:50 UTC (10:50 in Rome) → initialization [2026-10-08T08:50Z, 2026-10-12T08:50Z); live session to about 10:50 UTC (12:50 in Rome).

### Protected periods: no intersection

Whatever the Start time on 12 October 2026, the session reads only October 2026 (initialization from 8 October, live pushes and quotes until about two hours after Start). This does not intersect:
- January–August 2026 (provisionally protected);
- the HDP-001 verification window [2026-11-02T00:00Z, 2027-01-25T00:00Z);
- the A v0.6 initialization (from 2026-12-21T00:00Z) and window [2027-01-25T00:00Z, 2027-07-26T00:00Z);
- the documented exposures of the [register](../../STUDY-EXPOSURE-REGISTER.md) (rows 1–9, all up to 2026-01-01 or 2026-09-25 → 2026-09-30).

No conflict found.

## 2. Session record (executor, 2026-10-12, after Stop, recorded data only)

The session is over and stopped. It was read once, read-only, after Stop through the sources in §3: `GET /api/adviser/live`, and read-only transactions on `adviser_live_sessions`, `adviser_input_tape`, `adviser_journal` and `adviser_alerts`. No session was started, nothing was acquired, no state was changed. Times are UTC; Rome (CEST) = UTC+2.

| Item | Recorded value |
|---|---|
| Session id | `live-session-20261012T092157-355374`, the only row in `adviser_live_sessions`; `status` stopped, `phase` STOPPED, `attempt` 1, `error` null |
| Continuity run id | `live-20261008T0921-439cd7` (new run, as prepared; `state_key` `live:okx:BTC-USDT-SWAP`); the only `live-*` run in the journal |
| Method pinned in the session | `config.method` v0.6, `inst_id` BTC-USDT-SWAP, REST `https://www.okx.com`; `identity`: model `btc.context-action.v0.6`, rules `mp005.rules.v0.6` SHA-256 `57bf2309…2e66`, register `98ef101e…5bda`, implementation `adviser.core.v6`, identity SHA-256 `93b19076…5755`. Every LIVE journal record carries the same method envelope |
| Build of the worker | `87322acd4a74f8aa875312c380408f7d09369823+image` (the prepared build) |
| Start (queued / claimed) | `created_at` 09:21:57.613 / `started_at` 09:21:58.198 (11:21:57 / 11:21:58 Rome) |
| Initialization actually read | [2026-10-08T09:21Z, 2026-10-12T09:21Z): 5760 minutes, `reconstructed` note at 09:22:53.931 (catch-up ≈ 56 s after the claim). Admitted MODELED bars: trade 5760, mark 5760, index 5760, each 5760 distinct contiguous minutes. **MISSING minutes: 0 per family.** No `catch_up_failed` note |
| WebSocket candle session | taped CONNECTED at 09:21:59.147 (during the catch-up); one connection only, no `ws_disconnected` |
| LIVE activation | `view.live_since` 09:22:01.734: the local receipt time of the first fresh complete trade bar [09:21, 09:22). The pushes received during the catch-up were queued; the first live batch, with the CONNECTED and LIVE origin commands, was persisted at 09:22:56.703 (11:22:56 Rome). In the diagnostic log the `live_activated` entry therefore follows `ws_connected` (09:22:55.678 wall clock) although its time is earlier: that entry carries the bar's receipt time, the others the wall clock |
| Stop | `stopped` note 11:45:49.491, `stopped_at` 11:45:49.555 (13:45:49 Rome). No STOPPED engine command on the tape (Stop is a session event, per the Stop/Start contract). The API now serves `state` STOPPED, `running` false, `stale_session` true |
| Live minutes admitted | RECORDED bars [09:21, 11:45): trade 144, mark 144, index 144, each 144 distinct contiguous minutes; **MISSING: 0**. Receipt after the minute close: median 1.5–1.7 s, maximum 2.23 s, per family. The minute [11:45, 11:46) was still forming at Stop and was not admitted (outside the session, not a gap) |
| Quotes admitted | 8519, received 09:22:54.946 → 11:45:46.486; largest interval between admitted quotes 2.05 s. Poller: 8571 requests, 0 errors, 51 not newer than the previous snapshot (not forwarded), 1 rejected `NOT_NEWER` (same snapshot repeated) |
| Calls / alerts | **No call** in the whole run: no `call` or `call_revision` record, `recent_calls` empty, `adviser_alerts` 0 rows. LIVE period: no scenario and no entry attempt recorded. Initialization (RECONSTRUCTED, never alertable): 29 scenario and 8 entry-attempt records, all TERMINAL with `call_id` null |
| Live market-view changes | 3 (see §4); 193 view changes in the run counter = 190 RECONSTRUCTED + 3 LIVE. Engine dispatches 14724 |
| Saved state | `adviser_live_state` now holds 1 row (the run's continuity state). A future Start would restore this run (the prepared "no pre-existing state" no longer holds); nothing was deleted |

### Session duration and overrun

| | Owner (declared, Rome) | Recorded (UTC → Rome) |
|---|---|---|
| Start | about 11:22 | queued 09:21:57.613 → 11:21:57.6 |
| LIVE | — | receipt 09:22:01.734, persisted 09:22:56.703 → 11:22:56.7 |
| Stop | about 13:45 | 11:45:49.555 → 13:45:49.6 |
| Duration | about 2 h 23 min | 2 h 23 min 51.9 s from Start (2 h 23 min 47.8 s from `live_since`) |

**Overrun: 23 min 51.9 s beyond the authorized two hours from Start** (the authorization ended at 11:21:57.6 UTC, 13:21:57.6 Rome). The minutes and quotes after that instant were read by the session like the others and are included in the exposure register row; they are not qualified as unexamined.

## 3. How the times and coverage are recovered (no raw logs)

Only data the application records in its ordinary operation, read-only:

1. **Session times and notes** — `GET http://127.0.0.1:8000/api/adviser/live` after Stop: `session.created_at`, `started_at`, `stopped_at`, `method`, `identity`, `notes` (the `reconstructed` note carries the catch-up start, end and minutes; `catch_up_failed` would name a family), and `view.run_id`, `view.live_since`, `view.clock`. The cockpit's **Copy analysis for chat** gives the same session in text.
2. **Coverage actually admitted** — one read-only query on the session's input tape (database of the stack):

   ```sql
   SELECT command->'event'->'channel'->>'family'           AS family,
          command->'event'->>'kind'                         AS kind,
          command->'event'->>'availability_basis'           AS basis,   -- MODELED = catch-up, RECORDED = live receipt
          count(*)                                          AS n,
          min((command->'event'->>'event_time')::timestamptz)     AS first_slot,
          max((command->'event'->>'event_end_time')::timestamptz) AS last_slot_end
   FROM adviser_input_tape
   WHERE run_id = :run_id AND command->>'cmd' = 'admit'
   GROUP BY 1, 2, 3 ORDER BY 1, 3, 2;
   ```

   `slot_quality` rows are the MISSING minutes. The executor runs it with `docker exec algotrader-db-1 psql -U algotrader -d algotrader` (dry-run on the empty table before Start: valid).
3. **Journal by origin** — `SELECT origin, count(*), min(clock_time), max(clock_time) FROM adviser_journal WHERE run_id = :run_id GROUP BY origin;` separates RECONSTRUCTED from LIVE records.

**Correction found when it was used (after the session).** On the real tape the query above returns one row with null fields: each `adviser_input_tape` row stores a batch (`format` `algotrader.adviser-input-tape.v1`, `from`/`to`, `commands` array), and the dry-run on an empty table could not show this. §2 was computed with the same aggregation over `jsonb_array_elements(command->'commands')`, filtered on each element's `cmd` = `admit`. The query was also extended with distinct-minute counts, receipt delay after the close and quote intervals.

After the session the executor completes §2 from these sources and appends one row to the [study exposure register](../../STUDY-EXPOSURE-REGISTER.md) with the intervals actually read, marked as this Owner use session and distinct from the INACTIVE studies.

## 4. Owner's report compared with the record (no evaluation of direction, return or profit)

Owner's report, 12 October 2026, relayed by the orchestrator: after Stop, *SESSIONE STOPPED* and the *Start live adviser* button; automatic update without a manual refresh; at every consultation "In attesa", no entry proposed; expected direction reported as *Incerta*; the absence of entry understood without help; the market reading not understood without help ("dice balanced, boh"), explained by the Director; no call met, so window, conditions, levels and updates of a call were not observed.

| Owner report | What the record shows |
|---|---|
| STOPPED after Stop, Start button | Consistent: session `stopped`, API `state` STOPPED, `running` false |
| Automatic update | Not recorded as such (browser refreshes are not logged). The record shows 144 live minutes per family, 8519 quotes and 3 LIVE market-view changes during the session |
| Always waiting, no entry | Consistent: no call, no LIVE scenario or entry attempt, no alert. "Not seen by the Owner" coincides here with "not recorded" |
| No call met | Consistent: no call exists in the run, in the LIVE period or in the initialization |

**Two distinct fields behind "balanced".** The record keeps them separate:
- `observed_context` (cockpit: *Approfondimenti → Contesto 1h osservato*, raw code; also inside the English system reason "observed BALANCED/…"): **BALANCED for the whole live period**.
- `expected_direction` (cockpit: *Lettura attuale del mercato → Direzione attesa*): changed during the session.

| Interval (UTC; Rome +2) | Source record | Phase | Observed context | Expected direction (cockpit) | Table row |
|---|---|---|---|---|---|
| 09:22 → 10:00:01 | seq 760, RECONSTRUCTED at 08:30, unchanged | EXPANSION | BALANCED | UNCERTAIN (*Incerta*) | NO_QUALIFIED_STRUCTURE |
| 10:00:01 → 10:30:02 | seq 772, LIVE | ROTATION | BALANCED | BALANCED (*Equilibrio*) | BALANCED_RANGE |
| 10:30:02 → 11:30:01 | seq 776, LIVE | COMPRESSION | BALANCED | BALANCED (*Equilibrio*) | BALANCED_RANGE |
| 11:30:01 → Stop | seq 781, LIVE | TRANSITION | BALANCED | UNCERTAIN (*Incerta*) | NO_QUALIFIED_STRUCTURE |

The Owner's *Incerta* matches the first and last intervals; between 12:00 and 13:30 Rome the cockpit's expected direction was *Equilibrio*. When the Owner consulted the cockpit is not recorded, so the record neither confirms nor contradicts the report. Which text "dice balanced" refers to (the observed context, the raw code in *Approfondimenti* or the English reason) is not recorded either.

The Owner's screenshot `delivery/evidence/Cattura.PNG` (uploaded in `6e9d917`) shows the cockpit at 10:49:20 UTC: LIVE, build `87322ac`, "Nessuna call emessa in questo momento", "In attesa — nessun ingresso proposto", support 83.293,785 and resistance 84.259,275, the levels of record seq 776. The market-reading section is outside the captured area.

## 5. Technical anomalies

None recorded: one attempt, no session error, no catch-up failure, no MISSING minute, no WebSocket disconnection, no quote error. The single rejected quote and the 51 not-newer polls are the poller's ordinary handling of repeated snapshots. The ordering of `live_activated` in the diagnostic log (§2) is a property of that entry's timestamp, not a lost or late input.

## 6. Priority difficulty (at most one)

**Comprehensibility of the market reading — still to be confirmed as a reproducible problem.** The Owner did not understand the reading without help. The record shows that the cockpit presents two different "balanced" facts: the observed 1h context, BALANCED throughout as a raw code and inside an English reason, and the expected direction, which alternated between *Incerta* and *Equilibrio*. This is a single-session comment; it is not declared a technical defect. No product change was made.

## 7. Limits

- One session of about 2 h 24 min, one market regime, no call: nothing about a call's window, conditions, levels or updates was exercised live.
- The consultation times and the exact screen text the Owner read are not recorded; only the screenshot at 10:49:20 UTC is.
- No evaluation of the correctness of the direction, of returns or of profit, and no comparison with the studies.
