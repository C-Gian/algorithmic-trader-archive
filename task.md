# Current task — Owner use session of the live adviser v0.6 (preparation)
Date: 2026-10-12. Status: ENVIRONMENT PREPARED (build `87322ac` served, method v0.6 available, no pre-existing live state); the session is started by the Owner, not by the executor ([record](delivery/evidence/LIVE-V06-USE-SESSION/NOTE.md)). Executor record; the Director's acceptance is separate. Studies INACTIVE; v0.6 and HDP-001 frozen.

## Assignment (orchestrator authorization, relayed by the Owner, 12 October 2026; build `87322ac`, CI green as reported by the Owner)

Prepare the Owner's ordinary environment for one live use session of v0.6, two hours from Start.
- Verify the checkout, the build actually served and method v0.6. No pull or fetch: a mismatching checkout is reported to the Owner.
- Before Start: verify the configured OKX instrument, the interval the ordinary catch-up will read for initialization and that it does not intersect protected periods; check whether a pre-existing live state would cause a restore, a consultation or a recovery of protected periods. No state deleted, no continuity rule changed; a conflict stops the work. Only the ordinary services needed.
- The executor does not start the session: the Owner presses Start. No extra acquisition, account link, economic evaluator or product change, before or during the session.
- Minimal documentary record: SHA, method, instrument, actual session interval and actual initialization coverage. The study exposure register receives the intervals actually read once available, distinct from the INACTIVE studies.
- Excluded: CI queries.

## Previous task — Integrated synthetic acceptance check of the adviser v0.6
Date: 2026-10-12. Status: DELIVERED — READY FOR DIRECTOR REVIEW — V0.6 INTEGRATED EPISODE ONLY ([note](delivery/evidence/LIVE-V06-INTEGRATED-EPISODE/NOTE.md)). Executor delivery; the Director's final acceptance is pending. Studies INACTIVE; v0.6 and HDP-001 frozen. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (orchestrator authorization, relayed by the Owner, 12 October 2026; expected base `115b9b5`)

One integrated synthetic v0.6 check, from the ordinary Start to the formation of the expectation, and to the issue and update of the call, through engine, persistence, API and cockpit.
- **Question.** Does the product build its expectation from the data, issue a call when the rules allow it, and present its updates correctly?
- **Coverage first.** Reuse an existing test that already covers the path. Complete only the missing part, in the existing framework.
- **One episode A.** Synthetic inputs through the existing entry point. The fixture may satisfy the frozen rules deliberately; it is declared a technical proof with no economic meaning.
  - Not allowed: injected scenario, call or guidance state; altered gates, readiness or timestamps; a parallel engine or new infrastructure.
- **One discriminating check.** Before a necessary v0.6 condition is met, the product waits and proposes no available entry. Name the condition and the moment it is met. No battery of variants.
- **Chain.** Expectation derived from admitted observations; call identity; times; API state, direction and levels; cockpit; update and conclusion of the same call; no early availability. Keep the conditional expectation distinct from entry availability.
- **Corrections.** Bounded integration fixes only, with a regression. A problem in the frozen rules is documented and work stops before changing them.
- **Excluded.** Owner access, real feed, acquisition, economic tests, CI queries.

## Previous task — Closing the Stop/Start contract (orchestrator decision)
Date: 2026-10-12. Status: DELIVERED — READY FOR DIRECTOR REVIEW — LIVE STOP/START CONTRACT ONLY. Studies INACTIVE; v0.6 and HDP-001 frozen. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (relayed by the Owner, 11 October 2026; expected base `bcf34ea`)

**Orchestrator decision (Astra), authoritative.** UNVERIFIED during a Stop is an availability condition served by the API, not a revision imposed on the engine.
- Stop keeps the last assessment and its timestamp. A kept AVAILABLE is historical: the API serves UNVERIFIED, the stopped / not-current reason and no usable band as a current proposal.
- STOPPED is a session event at its actual time. It never becomes a call revision and is never backdated to the last processed instant.
- The journal may go from AVAILABLE to UNASSESSABLE at the restart: the service suspension is a separate fact.
- The existing gap rules apply at the restart. There is no new "every Stop invalidates the call or the scenario" rule.
- The timer effects hypothesised in the previous delivery are not established and do not motivate this decision.

**Work.**
1. Align the README and the tests to the distinction between the engine's historical state and the served current availability.
2. Prove it on the real worker path: AVAILABLE → Stop requested → Stop confirmed and saved → Start → restore. Check through the API and the cockpit, also after a reload.
3. Follow STOPPED through the tape and the restore: no late decisional application. Bounded correction of the session-event handling only.
4. Check how the interruption is consultable and kept distinct from the call history. No invented UNVERIFIED revision; report any new API or persistence need.
5. Fix the missing method in the v0.5 restore test.

Timers, gap rules, terminals and the method stay unchanged.

## Previous task — Live continuity after a voluntary Stop and a new Start (verification)
Date: 2026-10-11. Status: VERIFIED (`bcf34ea`); the reported Stop-dispatch conflict was decided by the orchestrator and closed in the task above. No product change. Studies INACTIVE; v0.6 and HDP-001 frozen. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (relayed by the Owner, 11 October 2026; expected base `e298660`)

Does a voluntary Stop followed by Start create a new session? Is the same run kept? What happens to the previous call and its availability?
- **Survey.** Kept apart: Stop then Start, a browser reload, and a worker interruption and resumption. The path data interruption → UNVERIFIED → reload → resumption → CLOSED is not repeated. Reconstruct, with references:
  - session and run identity, and the conditions to resume or create a run;
  - the effect of Stop on the call, and the treatment of revisions and terminals;
  - the checks needed before a current availability;
  - the UI path to the previous call.
- **Coverage.** Reuse the existing tests. Add only one targeted synthetic test where proof is missing, through the API and the cockpit. A saved AVAILABLE never becomes current by restore alone.
- **Defects.** Fix only bounded defects against the established contract. Stop and report if a session or lifecycle semantic must be chosen.
- **Excluded.** Language, mobile or graphic polish; Owner data; real feed; economic tests; CI queries.

## Previous task — Cockpit: implementation of the SECOND visual proposal
Date: 2026-10-11. Status: IMPLEMENTATION COMPLETE (`e298660`) — final check with the Owner STILL TO DO ([note](delivery/evidence/COCKPIT-IMPLEMENTATION-2/NOTE.md)). The technical checks are not evidence of Gian's understanding; a short joint check follows the delivery. Studies INACTIVE; v0.6 and HDP-001 frozen. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (relayed by the Owner, 11 October 2026; expected base `c7abfb8`)

Gian approved the second proposal ("per ora ok"). Implement it in this step, with no Astra step in between.
- **Approved scope.**
  - A more compact chart on the left and a wider decision panel on the right.
  - The market reading kept apart from the call.
  - Operational information grouped, details progressive.
  - A separate palette for direction, availability and technical states across the whole cockpit.
  - Candles in the existing PriceChart, from the OHLC already received. No second chart.
- **Unchanged.** Semantics, guidance and authoritative availability. No change to method, API, persistence or Workbench.
- **Check before applying.** The patch must not alter:
  - published contents and values;
  - update identity and ownership;
  - async response handling;
  - the entry band shown only when available;
  - the concluded call kept apart from the new expectation.
- **Ordinary corrections.**
  - Coherent Italian price notation in the chart and the panel, without changing precision or values.
  - No overlapping level labels.
  - A method badge readable at the supported widths.
- **Checks.**
  - The six synthetic states.
  - SHORT available vs an error; concluded LONG vs available entry.
  - Chart OHLC, time order and levels.
  - Proposal, history and continuity regressions.
  - Desktop, 1024 and 390 px.
  - Contrast, and states recognisable by text and symbols.
- **Delivery.** A bounded diff, the checks, the limits and images. Implementation is kept distinct from the Owner's final check.
- **Excluded.** CI queries, real feed, Owner data, economic tests.

## Previous task — Cockpit desktop arrangement: SECOND visual proposal
Date: 2026-10-10. Status: SECOND PROPOSAL DELIVERED — APPROVED by Gian ("per ora ok", relayed 11 October 2026) and implemented in the task above ([proposal](delivery/evidence/COCKPIT-VISUAL-PROPOSAL-2/PROPOSAL.md)). The first proposal was not approved and is not implemented.

## Assignment (relayed by the Owner, 10 October 2026; expected base `4a918dc`)

- **Owner feedback.**
  - The colours looked essentially unchanged.
  - Chart on the left, decision panel on the right.
  - Smaller chart, wider panel.
  - Candles, possibly a second useful chart.
- **Layout.**
  - Keep apart the market reading, the call identity, the new entry and the call update.
  - Group the operational information; put technical details and history progressively below.
  - No equal-height cards with large gaps.
  - Check the supported widths.
- **Chart.**
  - Reuse an existing component for OHLC candles if it can show them with the data the cockpit already has, keeping levels and times. Otherwise state the exact limit.
  - No new chart engine, endpoint or data transformation.
  - Name a reusable second chart only if one answers a distinct, useful question. Do not add it.
- **Colours, whole cockpit.**
  - Green/red for LONG/SHORT and rising/falling.
  - Blue for availability or a ready technical state, with labels that distinguish the two.
  - Amber for attention and non-verifiability.
  - Neutral for waiting, closed entry, history and conclusion.
  - Technical badges must not stay green; also check buttons, alerts and the timeline.
  - Always with text and symbols.
  - In the chart, explain how levels, direction and entry state are distinguished; candles may be green/red; check contrast.
- **Delivery.**
  - The same six synthetic states, new desktop images, and CLOSED also at 1024 and 390.
  - A first-vs-second comparison, the colour map, the candle findings and a second-chart candidate.
  - Independent sessions are not presented as one sequence; everything is marked as an inactive proposal.
  - Product files restored; evidence and documentation only.
- **Excluded.** Semantics and guidance, method, API, persistence, Workbench, real feed, Owner data, economic tests, CI queries.

## Previous task — Cockpit desktop arrangement: visual proposal first
Date: 2026-10-10. Status: PROPOSAL DELIVERED — NOT APPROVED by Gian ([proposal](delivery/evidence/COCKPIT-VISUAL-PROPOSAL/PROPOSAL.md)); not implemented.

## Assignment (Astra, relayed by the Owner, 10 October 2026; expected base `8759c85`)

A complete cockpit arrangement step, whose first delivery is a visual proposal for Gian, not implemented.
- **Distinctions.** The current market reading; the call's direction and identity; new-entry availability; the identified call's update or conclusion.
- **Layout.** Better use of desktop space; main operational information grouped; reading and call kept apart; details progressive; no conflicting duplicates; the two approved perspectives; supported widths kept.
- **Colours.** An explicit map: green LONG, red SHORT, a distinct colour and symbol for availability, distinguishable signals for attention, unverifiable, concluded and technical states, always with text. The whole panel is never coloured by direction; contrast is checked.
- **Images.** Six synthetic states at a declared desktop viewport, labelled as a proposal.
- **Excluded.** Method, API, persistence, Workbench, Owner data, real feed, CI.

## Previous task — Clarity of a call's updates: two perspectives and plain-Italian guidance
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — COCKPIT CALL UPDATES ONLY ([note, second correction](delivery/evidence/LIVE-CALL-UPDATES-EPISODE/NOTE.md)). Guided test only. Studies INACTIVE. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (relayed by the Owner, 10 October 2026; expected base `a0d6029`)

- **Two perspectives.** Two hypothetical sections of equal legibility: "Se non hai ancora aperto un'operazione" (authoritative availability; CLOSED = "Ingresso non disponibile adesso") and "Se hai già aperto un'operazione su questa call".
- **Guidance.** The second section shows in plain Italian what the recorded guidance says. The CLOSED hold text becomes "Il sistema indica di mantenere l'operazione con stop 99.700 e target 100.700.". Hold or exit is never derived from ONGOING, the direction or the levels. Translate only recognised texts with their own values; declare unknown or missing ones; keep the original in the details.
- **TARGET_REACHED.** The target is reached and the indication concluded; the later expectation does not extend the call; no close order unless recorded.
- **Excluded.** Method, API, persistence, Workbench, layout and palette.

## Previous task — Clarity of a call's updates (live cockpit main panel)
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — COCKPIT CALL UPDATES ONLY ([note, correction section](delivery/evidence/LIVE-CALL-UPDATES-EPISODE/NOTE.md)). Guided test only, not a general usability or effectiveness validation. Studies INACTIVE. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (relayed by the Owner, 10 October 2026; expected base `3b10e1a`)

After the guided test with Gian:
- **Groups.** Separate "Disponibilità di un nuovo ingresso" from "Aggiornamento della call già emessa".
- **Call present.** Show the call's recorded guidance in the main panel with its time; never derive "keep" from ONGOING; invent no hold or exit text; assume no entry.
- **Concluded call.** Show the conclusion and recorded reason apart from the current MarketView. Distinguish the operational target from the scenario destination for TARGET_REACHED. Make clear the current expectation does not extend the call.
- **Missing guidance.** Declare it; do not rebuild it.
- **Excluded.** Method, API, persistence, Workbench, general restyling.
- **Checks.** The same v0.6 episode and the existing tests.

## Previous task — Comprehension of a call's updates (synthetic episode, live cockpit)
Date: 2026-10-10. Status: DELIVERED — evidence for the Owner's interpretation ([note](delivery/evidence/LIVE-CALL-UPDATES-EPISODE/NOTE.md)). No UI correction made. Studies INACTIVE; v0.6 and HDP-001 frozen. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (relayed by the Owner, 10 October 2026; expected base `2159ef6`)

One coherent synthetic episode in the current cockpit, with three moments of the same call:
1. entry AVAILABLE;
2. entry CLOSED with the thesis still ONGOING;
3. the call's conclusion through a real method transition.

States come from the engine only. Deliver three labelled screenshots and a short note covering identities, times, revisions, statuses, reasons and recorded guidance, and what is visible versus details-only. Keep historical versus current in the third moment. No explanations that suggest answers, and no new holding or exit text. No UI correction before the Owner's interpretation. Only consistency checks.

## Previous task — Input provisioning for HDP-001 and A v0.6 (technical path; no real data)
Date: 2026-10-10. Status: **CLOSED by the orchestrator's disposition** ([HDP-001 §8.1](delivery/HDP-001-VERIFICATION-REFERENCES.md) · [A v0.6 §10.1](delivery/A-V06-OPERATIONAL-EVALUATION-REFERENCES.md)).
- The preparatory cycle is closed within the documented limits.
- Future source availability is not attested; the risk is accepted.
- Funding not covered: PRICE_NET_ONLY, already admitted, so no funding decision is required.
- Pre-execution conditions and a separate authorization remain. Studies INACTIVE. Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Assignment (relayed by the Owner, 10 October 2026; expected base `9854f16`)

Complete the technical input path of both studies without acquiring real data.
- **Sources.** Official documentation for history, retention, paging and limits (URL, section, date); documented vs guaranteed availability. Report series that need prior collection or post-window recovery that is not documented.
- **Coverage.** Exact intervals from the registered documents, with no margins.
- **Path.** Reuse acquisition, `marketdata.v1`, pack composition, verification and reading. Document parts, order, identity, provenance, gaps, duplicates, overlaps, conflicts, delivery to the executors and immutable identities. Completeness is verified on content.
- **Tests.** Synthetic: boundaries, gaps, conflicting overlaps, duplicates, identity and coverage delivery.
- **Excluded.** Market-data requests, Owner data, credentials, acquisition, changes to windows, semantics, population or profiles, and to the `be44370` behaviour.

## Previous task — A v0.6 statistical completion (offline bootstrap)
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — A V0.6 BOOTSTRAP TOOLING ONLY ([references §9](delivery/A-V06-OPERATIONAL-EVALUATION-REFERENCES.md)). **Decision registered; statistical implementation delivered, awaiting the Director's final review; studies INACTIVE.** The orchestrator decision, missing at delivery (`e52f237`), was then relayed and registered verbatim: [decision](delivery/A-V06-STATISTICAL-CONVENTIONS-DECISION.md). Remote CI is Owner-operated: PENDING / NOT CHECKED.

### Statistical completion assignment (relayed by the Owner, 10 October 2026; expected base `b2ebf20`)

Register the orchestrator decision verbatim in a separate `delivery/` document (text not received) and complete the offline bootstrap with synthetic evidence only.
- **Bootstrap.** The full UTC hourly grid; 168 h moving blocks; 10,000 resamples; one `random.Random(0)`; one `randrange(N-L+1)` per block, in resample -> block order; no wrap; truncated last block. The statistic is the sum of the resampled hourly values, with the registered 95% percentile convention. Zeros are only attested null contributions.
- **Protections.**
  - Not attested: no balance, no bootstrap, no reconciled subtotal.
  - Undetermined included path: no balance, no bootstrap, an explicitly partial subtotal only.
  - Attested and determinable: balance and bootstrap, with the interval separate and no verdict.

  The owner journal stays descriptive.
- **Identities.** Full SHAs of `b47b997` and `be44370` and the tool versions, with product and tool identities kept separate.
- **Excluded.** `src/`, method, preset, evaluator, acquisition, Owner data, real evaluation, CI. The design term 2027-01-25T00:00Z is unchanged.

## Previous task — A v0.6 continuous evaluation, technical preparation
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — A V0.6 STUDY PATH ONLY. **Technically ready** on synthetic evidence only; the **study is not launchable** ([references §8.6](delivery/A-V06-OPERATIONAL-EVALUATION-REFERENCES.md)). Studies INACTIVE. Remote CI is Owner-operated: PENDING / NOT CHECKED.

**Review correction (base `2018634`).** The ledger gives no complete balance or hourly series without attested identity and completeness. It is a ledger-only change ([references §8.8](delivery/A-V06-OPERATIONAL-EVALUATION-REFERENCES.md)): method, preset, population and economic criteria are unchanged, and the bootstrap is not implemented.

### Study path assignment (relayed by the Owner, 10 October 2026; expected base `77420cd`)

Make the full A v0.6 preparation, execution and reporting path technically executable, proven only with isolated synthetic data.
- **Sources.** The design, the orchestrator decision, the references decision, the operational references and `identities-b47b997.json`. Authoritative sources prevail. `b47b997` is the frozen behaviour reference. Pinned documents are not modified.
- **First step.** Reconstruct the existing path and locate the impediments; choose the minimal adaptation of existing tools. No new engine or parallel infrastructure.
- **Window and continuity.** [2027-01-25, 2027-07-26), with the registered initialization and tail. One continuous run, no monthly reset. Technical partitions keep state, order and identity. The tail only completes included paths. No indiscriminate date access; no protected periods.
- **Method and population.** The ordinary v0.6 policy, unchanged. Primary = every A call issued in the window. These are kept apart:
  - pre-existing owners and owners born in the window;
  - non-confirmation and non-issue;
  - included calls and post-boundary issues;
  - NO_ENTRY and undetermined entered paths.

  No imputation and no invented balance.
- **Reporting.** PRIMARY results, price_net or total_net (only with certified funding), per-call results, UTC issue-hour attribution. Hours without a call are 0; undetermined hours are not automatically 0. No HDP-001 conventions. Open statistical conventions go to the Director.
- **Identity and equivalence.** Register the reference, the build, the method, parameters, profile and evaluator, and the synthetic inputs. Map the relevant diff, compare reference and build on the same inputs where applicable, and verify the window extension separately. No general equivalence from a few fixtures.
- **Excluded.** Real feed, Owner data, acquisition, real cache, economic replay, the Owner stack, real evaluations, CI polling. HDP-001 and v0.6 frozen.

## Previous task — HDP-001 verification executor, technical preparation
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — HDP-001 EXECUTOR ONLY. The executor is prepared only to the extent shown by synthetic tests ([references §7](delivery/HDP-001-VERIFICATION-REFERENCES.md)). **HDP-001 INACTIVE.** Remote CI is Owner-operated: PENDING / NOT CHECKED.

### HDP-001 executor assignment (relayed by the Owner, 10 October 2026; expected base `d5a666b`)

Implement and document an offline HDP-001 verification executor, ready to apply the frozen protocol, verified only with isolated synthetic fixtures.
- **Sources.** The protocol, the Director decision, the exploration closure and the references decision. The operational references are an index only. The temporal semantics and the exploration script are reused, not modified.
- **Scope.** Existing formats and tools. Explicit offline path: no download, service, Owner DB or UI, and no adviser change.
- **Samples.** The frozen window, 2016 cutoffs, the last one BOUNDARY_NOT_SCORED. Complete hours only, with no interpolation. UP fixed. No MarketView, scenario or call selection. FLAT and unavailability per the protocol, with grid and masks kept.
- **Integrity.** Concrete checks; UNAVAILABLE vs NOT_EVALUABLE; no coverage percentage; internal vs external provenance declared.
- **Computation.** Paired cells, accuracies, Delta; the registered bootstrap; duration and zero denominators per the protocol; no A v0.6 convention.
- **Output.** Identities and hashes, coverage, masks, absence distribution, synthetic vs real distinguished, no overwrite, no automatic update of the reference, status or register.
- **Tests.** Few discriminating synthetic cases with hand-derived expectations. The existing framework, no product suites, DB or E2E.
- **Excluded.** Acquiring or consulting verification data or protected periods; running the real study. v0.6 frozen; A technical preparation not activated.

## Previous task — Closure of the study references (documentary only)
Date: 2026-10-10. Status: **Riferimenti registrati; preparazione esecutiva ancora incompleta; studi INACTIVE.** [Decision (verbatim)](delivery/HDP-001-A-V06-REFERENCES-DECISION.md) · [HDP-001 references](delivery/HDP-001-VERIFICATION-REFERENCES.md) · [A v0.6 references](delivery/A-V06-OPERATIONAL-EVALUATION-REFERENCES.md) · [exposure register](delivery/STUDY-EXPOSURE-REGISTER.md). Remote CI is Owner-operated: PENDING / NOT CHECKED.

### Study references closure assignment (relayed by the Owner, 10 October 2026)

Base `aff2a3d`.
- Register the authoritative decision verbatim in a separate addendum linked to the pinned HDP-001 and A v0.6 documents. Do not edit the pinned texts or replace the decision with a summary.
- Update the two operational addenda, separating what is resolved from residual dependencies.
- Designate and create `delivery/STUDY-EXPOSURE-REGISTER.md` with a minimal structure. Columns: study, period, consultation date, material, subject, use in decisions, source. Documented exposures only; gaps stay explicit; never "no exposure" from missing information.
- **Checks.** Text fidelity, links, state coherence; identities recomputed with the existing functions; pinned hashes unchanged; no re-run of the exploration.
- **Operational points.** Close only those already determined by the designs. List the missing computation conventions without completing them.
- **Excluded.** Acquisition, Owner extraction, implementation, running the studies, CI polling, pull/fetch. v0.6 and HDP-001 frozen; protected periods unchanged.

## Previous task — Complete the references of the two frozen studies (documentary only)
Date: 2026-10-10. Status: DELIVERED at `aff2a3d` (superseded by the closure above).

### Study references authorization (Astra, relayed by the Owner, 10 October 2026)

Make the artifacts, rules and residual dependencies of HDP-001 and of the A v0.6 operational evaluation identifiable. Documentary preparation only.
- **HDP-001 (first priority).** Protocol and decisions, exploratory closure and constant UP, frozen window, script and conventions (168 h blocks, 10,000 resamples, `random.Random(0)`, type 7, masks, boundary), verifiable identities of reusable artifacts. Keep the exploratory script distinct from verification instructions; do not modify it.
- **A v0.6.** From the design and closure, identify method, parameters, implementation, evaluator and profile through existing identities and functions. Verify `b47b997` and record full SHAs and hashes. Later UI changes do not make the newest commit the study build. Identities that depend on future data or a non-existent pack are declared for later registration; no invented hashes, no new identity system.
- **Per study.** Separate what is fixed and verified now, future data/hashes, and checks/authorizations still needed. An executor must understand what to use without the chats.
- **Mode.** Update existing documents and STATE/task only as needed; no general dossier or duplicated specifications. Authoritative text stays recognizable; operational additions are separate and labelled; pinned documents are not rewritten. Report any missing convention or conflict touching method, window, population, outcome or frozen reference; do not resolve it implicitly.
- **Excluded.** Acquisition, Owner extraction, running the studies, opening protected periods, CI polling, pull/fetch. v0.6 and HDP-001 frozen.

## Previous task — Historical alerts vs current availability (live cockpit banner and timeline only)
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — HISTORICAL ALERTS PRESENTATION ONLY ([evidence](delivery/evidence/LIVE-HISTORICAL-ALERTS/NOTE.md)). Remote CI is Owner-operated: PENDING / NOT CHECKED. No further package is activated.

### Historical alerts authorization (Astra, relayed by the Owner, 10 October 2026)

Presentation correction of historical alerts in the banner and timeline only. First verify the defect reported at `f62aa63`: during UNVERIFIED and CLOSED, earlier guidance such as "Entry still valid now" and "entry available inside …" remains. Then correct it.
- Each alert is a recorded event with local date, time and an identifiable time zone. The main message is a past-tense description based on the recorded type.
- The original text stays in the details, labelled "Testo registrato a quell'ora". Any entry band is qualified as relative to the historical event, never as usable now.
- Current availability is read in the main panel, which keeps reading the authoritative state. A missing time shows "Orario non registrato", never the load time.
- No record rewrite, frontend availability inference or new alert expiry. Existing dismiss/acknowledgement commands are kept.
- **Verification.** Reuse `test_live_continuity_e2e`: banner and timeline during UNVERIFIED and CLOSED, before and after reload. The original text stays consultable, and the current panel equals the backend. The v0.2 fixture is allowed, documented as crossing the shared components; do not extend the test to certify v0.6.
- **Excluded.** The transitional "Stopped / Loading…", method, API, persistence, Workbench, Owner data, real feed, economic replay and CI polling. v0.6 and HDP-001 frozen; evaluations INACTIVE.

## Previous task — Cockpit: clarity of the operational state (live cockpit only)
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — COCKPIT CLARITY ONLY ([evidence](delivery/evidence/LIVE-PROPOSAL-CLARITY/NOTE.md)). Remote CI is Owner-operated: PENDING / NOT CHECKED. No Owner launch is prepared and no further package is activated.

### Cockpit clarity authorization (Astra, relayed by the Owner, 10 October 2026)

Live cockpit only; Workbench excluded. The main panel must answer "Che cosa propone il sistema adesso?":
- **States.** "In attesa — nessun ingresso proposto" / "Ingresso disponibile secondo il sistema" / "Ingresso non più disponibile" / "Non è possibile confermare la disponibilità dell'ingresso". Terminal and non-current keep the existing protections.
- **Source.** Only the backend's authoritative state; no availability inferred from direction, quotes or levels.
- **Without a call.** Direction, the needed condition, the scenario destination and the structural invalidation, never called entry, target or stop.
- **With a call.** Plain LONG/SHORT, the admissible band only when available, the published target and stop, conditions, deadline and the reason for unavailability. Past levels are history only.
- **Kept distinct.** Narrative destination vs operational target, horizon vs deadline, entry availability vs thesis validity, the system's indication vs the user's unknown operation.
- **Presentation.** Grouped, readable on phones, simple Italian, details collapsed, local time with time zone; no probabilities, promises or countdowns; absences declared.
- **Checks.** Fields and states verified first, including CLOSED, UNVERIFIED, terminal and not current, without changing rules.
- **Excluded.** Method, API or persistence changes; Owner data, live feed or economic replay. v0.6 and HDP-001 frozen; evaluations INACTIVE.

## Previous task — Live call history in the live cockpit (product, read-only consultation)
Date: 2026-10-10. Status: DELIVERED — READY FOR DIRECTOR REVIEW — LIVE CALL HISTORY ONLY ([evidence](delivery/evidence/LIVE-CALL-HISTORY/SUMMARY.md)), with the revision-label correction at `e582f38`; synthetic comprehension episode at `1c346ff` ([note](delivery/evidence/LIVE-COMPREHENSION-EPISODE/NOTE.md)).

### Live call history authorization (relayed by the Owner, 10 October 2026)

After the read-only adviser user-path survey at `6710474` (the Owner's visual review was closed as not assessable from the available material, with no interface finding), the Director authorized making the already-recorded history of a single call consultable from the live cockpit:
- identity = session/run + call, never mixing records; reuse of *Guidance revisions* where compatible; minimal presentation adaptation and reading of existing records only;
- revisions in recorded order, explicit UTC times, stored values/changes/reasons only; current vs earlier revisions, no-revision/partial/missing/error, available/not-current/terminal kept distinct; no stale data under a new call/session, including out-of-order responses;
- no reconstructed motivations, no implied Owner entry, no hypothetical economic path in live; read-only, no dedicated continuous polling;
- stop at the boundary if new events, persistence or method semantics were needed. A minimal read-API adaptation was allowed but was not needed.

Not authorized: general restyling, new infrastructure, kernel/rule/parameter/selection/evaluator/method-identity changes, persistence or migrations, live feed, Owner data or stack changes, acquisition or economic replay. v0.6 and HDP-001 stay frozen; studies stay INACTIVE.

## Previous task — WP-015: MP-005 implementation / candidate v0.6
Date: 2026-10-09. Status: DELIVERED — READY FOR DIRECTOR REVIEW — WP-015 ONLY ([evidence](delivery/evidence/WP-015-ENGINEERING-EVIDENCE.md)). Remote CI is Owner-operated: PENDING / NOT CHECKED.

## Preceding record and studies (not active packages; execution INACTIVE)

The read-only four R→N paths diagnosis of `eval-20261009T155751-be8b2b` was delivered at `cb356f2`, with Astra documentary corrections at `3c6af11`; see the STATE.

**HDP-001 — not an active package.** The [protocol](delivery/HDP-001-HOURLY-DIRECTIONAL-PERSISTENCE.md) and its [registration decision](delivery/HDP-001-DIRECTOR-CLOSURE.md) are approved and registered (bootstrap seed 0).
- **Exploration closed.** The Director accepted the [exploration](delivery/evidence/HDP-001-EXPLORATION/SUMMARY.md) at `cf18dbd`, on Astra's independent review ([closure and freeze](delivery/HDP-001-EXPLORATION-CLOSURE.md)). It promotes no signal and shows no economic effectiveness.
- **Verification frozen.**
  - Constant reference UP.
  - Window [2026-11-02T00:00Z, 2027-01-25T00:00Z) ([note](delivery/HDP-001-VERIFICATION-WINDOW-PROPOSAL.md)).
  - Protocol and conventions: 168 h blocks, 10,000 resamples, `random.Random(0)`, type-7 percentiles.
  - Boundary: the last cutoff is kept, and the endpoint equal to the end is not scored.
  - No adaptation, extension, opportunistic stop or interim consultation. Any exposure that influences research decisions must be declared.
- **Execution INACTIVE.** Acquisition and computation after the end need a separate executive assignment.
- v0.6 stays frozen, and January–August 2026 stays protected.

**A v0.6 operational evaluation — not an active package.** The [design](delivery/A-V06-OPERATIONAL-EVALUATION-DESIGN.md) and the [orchestrator decision](delivery/A-V06-OPERATIONAL-EVALUATION-CLOSURE.md) are approved (Astra, relayed by the Owner) and registered verbatim.
- Window [2027-01-25T00:00Z, 2027-07-26T00:00Z) fixed. The pre-start freeze of method, implementation and profile identities (technical reference `b47b997`) is still to be completed and verified.
- **Execution INACTIVE.** No future pack is acquired or certified by the registration. Acquisition, access and execution need a separate assignment.
- v0.6 and HDP-001 unchanged; January–August 2026 stays protected.

## WP-015 authority

- [MP-005 specification](delivery/MP-005-V06-INITIAL-RESPONSE-INCOMPATIBILITY.md) and [Director methodological closure](delivery/MP-005-DIRECTOR-CLOSURE.md): separate documents, registered from the relayed authoritative text.
- **Executive authorization**, recorded verbatim and separately in [WP-015-MP-005-IMPLEMENTATION-SPEC.md](delivery/WP-015-MP-005-IMPLEMENTATION-SPEC.md). The closure alone did not activate work. The authorization covers implementation and synthetic engineering checks only, not economic runs.

## WP-015 assignment (summary; the verbatim text is authoritative)

1. **Registration.** Register spec, closure and authorization separately. Prepare the task, register and v0.6 identities. Keep every inherited numerical value and show only the new categorical elements. Preserve v0.2–v0.5 specifications, identities, outputs and checkpoints.
2. **Scoped implementation.** Only the MP-005 check after the valid preparation of the single RETURN reference:
   - historical: F ∩ corridor ∩ economic region;
   - live: F ∩ corridor only, cost-independent;
   - a single admissible tick is non-empty;
   - inherited protections first;
   - `INITIAL_RESPONSE_INCOMPATIBLE` ends the child, not the scenario;
   - P and X in the same dispatch, never C/R/N/I/A;
   - no renewal, reopening or later local classification.
   
   Reuse the existing formulas. No tolerances, live minimum costs, thresholds or new interpretations.
3. **Integration.**
   - v0.6 selectable in the Workbench and live.
   - Distinct identities and persisted state, with production restore.
   - The reason, diagnostic bases and count identities in JSON, Markdown, Copy report and export.
   - The new count is a subset of X with denominator P, never summed again.
   - WAIT-open cohorts kept, and the C/R loss explained.
   - No 20-RETURN threshold for v0.6.
   - UI: an ended attempt is distinct from an invalidated scenario.
   - Assurance, reconciliation and Deep extended only where needed.
4. **Checks.**
   - Every MP-005 fixture, LONG and SHORT, plus direct live CORRIDOR coverage with a preparable reference.
   - Single tick and edges; precedence; same dispatch.
   - Checkpoint/restore and crash; live temporary cost restriction.
   - Parity with v0.5; previous pins.
   - Reports and copy text; a minimal browser path.
   - Typecheck, build and schemas, on an isolated database.
   - Report counterexamples; never correct silently.
5. **Limits.** No acquisition, Owner extraction, real-data replay or economic backtest/comparison; no automatic Owner launch; no Owner-stack change.
6. **Delivery.** Compact evidence; update STATE and task; commit and push. No CI polling or waiting.
