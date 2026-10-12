# Live adviser v0.6 — Owner use session (one session, two hours from Start)

**Executor record, not the Director's acceptance.** This is a real use session of the live adviser by the Owner (Gian), authorized by the orchestrator on 12 October 2026. It is not a study, not an economic test and not evidence of market prediction or profit. v0.6 and HDP-001 are frozen; the studies (HDP-001, A v0.6) stay INACTIVE and this session is not part of them.

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

## 2. Session record (to complete after the session from recorded data)

| Item | Value |
|---|---|
| Session id | *to complete* |
| Continuity run id | *to complete* |
| Method pinned in the session | *to complete* (`session.method`, `config.method`) |
| Build of the worker | *to complete* (`session.identity`) |
| Start (queued / claimed) | *to complete* (`created_at` / `started_at`, UTC) |
| Initialization actually read | *to complete* (note `reconstructed`: start, end, minutes; per-family MISSING counts) |
| LIVE activation | *to complete* (`view.live_since`) |
| Stop | *to complete* (`stopped_at`, UTC) |
| Live minutes admitted | *to complete* (first and last live slot per family) |
| Calls / alerts | *to complete* (count and identities only; no evaluation) |

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

After the session the executor completes §2 from these sources and appends one row to the [study exposure register](../../STUDY-EXPOSURE-REGISTER.md) with the intervals actually read, marked as this Owner use session and distinct from the INACTIVE studies.
