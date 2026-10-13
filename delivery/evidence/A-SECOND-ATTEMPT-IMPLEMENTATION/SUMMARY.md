# A — secondo tentativo: implementazione sperimentale isolata (v0.6-a2x)

12 ottobre 2026. Base `3705fd0`, branch main. Consegna dell'executor; la review del Director è pendente.

Fonte autoritativa: [`delivery/A-SECOND-ATTEMPT-DESIGN.md`](../../A-SECOND-ATTEMPT-DESIGN.md) (disegno `b20919e`, ratifica e precisazioni `3705fd0`), letta per intero prima di implementare. Solo prove sintetiche.

Il checkout è stato aggiornato dall'Owner durante l'ispezione iniziale: prima `137b8af`, poi `3705fd0`, per un fast-forward eseguito fuori da questa sessione. Nessun pull o fetch dell'executor.

## Identità della variante

| Campo | Valore |
|---|---|
| Chiave | `v0.6-a2x`, in `methods.EXPERIMENTAL`, non in `RELEASES` |
| Modello / regole | `btc.context-action.v0.6-a2x` / `a2x.rules.exp1` |
| Implementazione / stati | `adviser.core.v6-a2x`, `algotrader.adviser-state.v6-a2x`, `algotrader.adviser-runtime.v6-a2x`, engine `observe.stream.v7-a2x` |
| Documento regole | `method/A-SECOND-ATTEMPT-DESIGN.md`, copia byte-identica del disegno. Manifest: delta, poi MP-005 e tutti i testi ereditati da v0.6 |
| Registro | `method/A2X-SECOND-ATTEMPT-PARAMETERS.json` = registro MP-005 con identità e stato cambiati, più la sezione categorica `second_attempt`. **Nessun numero nuovo**: residuo A 30 min, frazione di progresso e scala ereditati |
| Report / riconciliazione / Deep | Nessuno (`NONE_EXPERIMENTAL`) |

**Selezione.** `methods.get("v0.6-a2x")` è rifiutato: è la chiamata usata da API, controlli, job e live. La variante si ottiene solo con `experimental=True`, che passano soltanto:
- `harness.make_runtime/run_pure` (percorsi di prova);
- `engine_config(..., experimental=True)`, mai passato dall'app.

`for_engine` accetta solo un documento che la fissi già. La variante non è elencata da `selectable()`, non è predefinita e non è installata nello stack Owner. Nessuna UI.

## Diff

- **`core3.py`.** Due hook a comportamento invariato:
  - `_conf_clocks`, alla conferma;
  - `_a_hard`, al routing e all'emissione A.

  Per v0.3–v0.6 restituiscono esattamente le espressioni precedenti. Lo dimostrano i pin byte-per-byte esistenti e la suite completa.
- **`core_a2x.py` (nuovo).** `AdviserCoreA2X(AdviserCoreV6)`:
  - apertura del riesame su `_scen_end`;
  - riserva dell'owner;
  - formazione fresca in `_a_close`;
  - B, gap e staleness nel riesame;
  - successore con legame al genitore;
  - clock limitati a H0;
  - recupero escluso per residuo insufficiente;
  - rinvio delle nascite ordinarie;
  - capacità che conta la riserva;
  - codec di stato.
- **`runtime_a2x.py` (nuovo).** Codec runtime della variante. Uno stato v0.6 e uno della variante non si decodificano a vicenda.
- **`methods.py`, `engine.py`, `harness.py`.** Registrazione sperimentale e selezione esplicita.
- **Test (nuovi).** `tests/adviser_a2x_fixtures.py`, `tests/test_a2x_second_attempt.py`.
- **Documenti.** README (sezione sperimentale), STATE, task.

## Effetto sulle nascite ordinarie (politica diversa)

Durante la riserva e fino al terminale del successore o a H0, **una nascita A ordinaria nella stessa direzione non può avvenire**, anche se Q_A è vero.

Nel nastro dedicato:
- v0.6 fa nascere un impulso ordinario alle 05:15;
- la variante lo rinvia e pubblica `ORDINARY_BIRTH_DEFERRED`;
- al rilascio (H0, 05:30) vale il latch ordinario: i Q_A veri delle 05:30 e 05:45 non bastano, serve un falso osservato dopo il rilascio (06:00), poi un vero (07:30).

Inoltre i falsi osservati durante la riserva non vengono "accantonati". Una valutazione dovrà quindi riguardare l'intera politica, non solo le call del successore.

## Comportamento atteso e osservato (LONG; SHORT speculare con gli stessi tempi)

Nastro principale `two_calls`:
- A 97000, B 100900, z 200, H0 05:30;
- S1 confermato alle 04:01, con la call 1 emessa alle 04:03.

| Ora | Atteso dal disegno | Osservato |
|---|---|---|
| 04:04 | V contattato: S1 e la call 1 INVALIDATED come in v0.6; riesame con origine O = 04:15 | S1 `TERMINAL INVALIDATED V_CONTACT` e record di S1, figlio e call 1 identici a v0.6; osservazione `REVIEW_OPEN` (origine 04:15, R1 99900) |
| 04:15 | La barra [04:00,04:15) contiene il fallimento: esclusa | Non conteggiata (`new_bars` 0) |
| 04:30 | Barra fresca con chiusura contraria, R2 99650 < R1: ARM S2 con K2 = 100050, V2 = 99450 | `SUCCESSOR_ARMED` e S2 `ARM SECOND_ATTEMPT_FRESH_POST_FAILURE_REACTION`: R 99650, K 100050, V 99450, B 100900, parent = S1; monitoraggio di B dalle 04:30 |
| 04:31 | Chiusura 100050,1 = K2 + tick: C2 con 59 min residui; scadenza H0, progresso a C2 + (H0 − C2)/2 | `CONFIRM`: deadline 05:30, progresso 05:00:30; figlio in WAIT RETURN con hard deadline 05:30 |
| 04:32–04:34 | Blocco temporaneo, riferimento, recupero (regole ereditate) | `BLOCKERS` (CLOSE_OUTSIDE_RETURN_CORRIDOR), `RESPONSE_REFERENCE`, `ISSUE` |
| 04:34 | Call 2 distinta: hard deadline H0, progresso a issue + (H0 − issue)/2 | Call 2: V 99450, ref 99865, scadenza 05:30 `ORIGINAL_IMPULSE_EXPIRY`, progresso 05:02 |
| 05:04 | — | S2 `DESTINATION_REACHED` |

Bordi e precedenze (LONG e SHORT):

| Caso | Atteso | Osservato |
|---|---|---|
| Nessun fatto nuovo (contraria senza minimo sotto R1; vecchio K superato) | Nessun S2; riesame fino a H0 | `REVIEW_CLOSED EXPIRED` alle 05:30; una sola CONFIRM di S1 |
| Recupero già avvenuto nella barra del fallimento (chiusura 100100) | Né vecchie barre né vecchia conferma | K2 = 100050 dalla barra fresca; C2 dal minuto [04:30,04:31) |
| Fallimento sulla frontiera (contatto [04:14,04:15)) | tf = O = 04:15; la barra che inizia a tf è ammessa | Riesame con opened_at = origine = 04:15; ARM alle 04:30 |
| Residuo esattamente 30 min | Conferma | CONFIRM alle 05:00, progresso 05:15, nessun TOO_LATE |
| Residuo inferiore (29 min) | Osservazione conservata, nessuna opportunità, nessuna proroga | `RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL` (barra, intervallo, disponibilità 05:01, cursor, close 100050,1, residuo 1740 s, richiesto 30); S2 `EXPIRED SECOND_ATTEMPT_RECOVERY_WITH_INSUFFICIENT_RESIDUAL` |
| Recupero disponibile esattamente a H0 | Il timer precede | S2 `OWNER_RELEASE` + `EXPIRED ORIGINAL_SETUP_DEADLINE` alle 05:30; nessuna CONFIRM né esclusione |
| Barra qualificante che chiude a H0 | Il timer precede l'ARM | `REVIEW_CLOSED EXPIRED` alle 05:30; nessun S2 |
| Chiusura 15m ≤ A+z prima dell'ARM | Riesame chiuso | `WITHDRAWN CLOSE_AT_OR_BEYOND_A_PLUS_ZONE` alle 04:30 |
| Chiusura ≤ A+z nel dispatch del fallimento | Nessuna riserva | `REVIEW_NOT_OPENED PREMISE_…`; il resto del journal identico a v0.6 |
| Contatto con B durante il riesame | Chiuso | `DESTINATION_REACHED` alle 04:55 |
| Minuto mancante | Chiuso | `UNASSESSABLE REQUIRED_MONITORING_GAP` alle 04:21 |
| Stallo del feed (1m stale) | Chiuso | `UNASSESSABLE REQUIRED_TRADE_1M_STALE` alle 04:22 |
| S2 confermato poi V2 contattato, nuova reazione e recupero | Nessun terzo tentativo | S2 INVALIDATED alle 04:38; nessuna osservazione o scenario successivo |
| Contraddizione locale del figlio S2 | Terminale del solo figlio; nessun riavvio | `LOCAL_RESPONSE_CONTRADICTED` alle 04:34; S2 resta CONFIRMED fino a STALLED alle 05:00:30; una sola call |

## Mappa requisiti → prove (`tests/test_a2x_second_attempt.py`)

| Requisito | Prova |
|---|---|
| Identità separata, selezione esplicita, non installabile | `test_variant_identity_is_separate_explicit_and_not_selectable` |
| v0.6 invariato quando la variante non è selezionata | `test_v06_behaviour_is_preserved_when_the_variant_is_not_selected`; pin byte-per-byte esistenti v0.4/v0.5 e suite completa |
| Un solo successore dopo V_CONTACT ammissibile; terminali esclusi | `test_without_a_confirmed_v_contact_the_variant_equals_v06` (75 nastri: STALLED, DESTINATION_REACHED, UNASSESSABLE, perdita d'ancora pre-conferma, terminali del solo figlio); `test_other_confirmed_terminals_never_open_a_review` (TIME_EXPIRED, B+V nello stesso intervallo) |
| LONG e SHORT fino al successore, call effettiva | `test_successor_reaches_an_issued_call_long_and_short` |
| S1, figlio e call 1 preservati | `test_first_attempt_child_and_call_records_are_exactly_v06` |
| Formazione post-fallimento, vecchie barre e vecchia conferma inutilizzabili | `test_old_bars_and_the_old_confirmation_are_never_new_facts`, `test_an_earlier_recovery_and_the_old_confirmation_never_confirm_the_successor` |
| Nessun terzo tentativo | `test_no_third_attempt` |
| Premessa, B, gap/staleness, H0 con precedenze | `test_premise_close_before_arm_ends_the_review`, `test_premise_close_in_the_failure_dispatch_excludes_the_review_and_keeps_v06`, `test_destination_gap_and_staleness_close_the_review`, `test_original_expiry_precedes_an_arm_completing_at_h0` |
| Bordi temporali | `test_failure_exactly_on_a_15m_frontier`, `test_residual_exactly_30_minutes_confirms`, `test_residual_below_30_minutes_is_recorded_not_confirmed`, `test_recovery_available_exactly_at_h0_is_preceded_by_the_timer` |
| Riserva, rilascio, latch | `test_reservation_defers_an_ordinary_birth_then_releases_with_the_ordinary_latch` |
| Routing: blocco temporaneo e terminale distinti | `test_successor_routing_keeps_temporary_blockers_and_terminal_endings_distinct` |
| Encode/decode e restore | `test_restore_at_every_critical_point_reproduces_the_uninterrupted_run`. Codec di produzione `pack_runtime/unpack_runtime` dopo 9 dispatch: call 1, apertura, formazione, ARM, C2, blocco, riferimento, call 2, scadenze. Digest identici, nessun record duplicato o mancante, clock invariati (05:30 / 05:00:30), riserva ripristinata; nessuna decodifica come v0.6 |

Verifiche indipendenti: livelli, tempi e transizioni sono scritti a mano dalle costanti dei nastri, non ricavati dal motore. Ogni nastro parte da storia fredda attraverso l'ordine ordinario del kernel (warmup, readiness, contesto, scala). Nessuno stato, anchor o call è predisposto.

## Controlli eseguiti

- **Test della variante.** `tests/test_a2x_second_attempt.py`: 112 passati.
- **Suite completa senza e2e** (come il primo job CI), in 6 shard paralleli: **1276 passati, 0 falliti, 255 skippati**.
  - Tutti i 255 skip hanno lo stesso motivo: `ALGOTRADER_TEST_DATABASE_URL not set`, cioè nessun DB di test isolato in locale. Le suite DB **non** sono quindi verificate qui.
  - Sono inclusi i pin byte-per-byte v0.4 (53) e v0.5 (68), la parità v0.5/v0.6 e tutti i percorsi MP-002–MP-005.
- **Non eseguiti.**
  - e2e: richiede build web, stack Postgres e Chromium.
  - Lint: ruff non installato.
  - La CI non è stata interrogata: e2e e suite DB restano affidati alla CI dell'Owner.

## Limiti

- **Solo prove sintetiche.** Nessun dato Owner, acquisizione, conteggio sui 28 casi, replay reale, backtest o valutazione economica. L'utilità della politica è ignota.
- **Contratti.** I record usano le forme semantic.v2 revisione 5 e si validano. Introducono però **valori nuovi** non registrati nel changelog pubblico, perché la variante non è una release pubblicata:
  - l'osservazione `structure/a_second_attempt` con le categorie REVIEW_OPEN, REVIEW_NOT_OPENED, REVIEW_CLOSED, SUCCESSOR_ARMED, ORDINARY_BIRTH_DEFERRED, RECOVERY_EXCLUDED_INSUFFICIENT_RESIDUAL;
  - il motivo ARM `SECOND_ATTEMPT_FRESH_POST_FAILURE_REACTION`;
  - il motivo terminale `SECOND_ATTEMPT_RECOVERY_WITH_INSUFFICIENT_RESIDUAL`;
  - le chiavi `setup` attempt, impulse_id, parent_scenario_id, review_opened_at, formation_origin, failed_attempt_R;
  - renewal `SECOND_ATTEMPT` e `hard_deadline_origin` `ORIGINAL_IMPULSE_EXPIRY`.

  La registrazione è necessaria prima di qualsiasi pubblicazione. *(13 ottobre: ora registrati in forma additiva e sperimentale, non pubblica; vedi [Completamento della review](#completamento-della-review-13-ottobre-2026-base-048bf2d).)*
- **Id.** Gli id degli scenari includono l'hash delle regole, come per ogni release: gli id della variante differiscono da quelli v0.6. I confronti normalizzano gli id.
- **Scelte tecniche dell'executor** (nessuna deroga metodologica):
  - la vista aggiunge una riga di motivo mentre il riesame è aperto;
  - l'orizzonte descrittivo di S2 armato è limitato al residuo;
  - un riesame aperto si chiude alla fine della finestra di valutazione (TAIL), e in TAIL non se ne aprono;
  - la riserva conta nella capacità A.
- **Non coperto da un nastro dedicato.** La chiusura del riesame per contesto contrario. Il codice applica il gate A ordinario a ogni dispatch. *(13 ottobre: ora coperta, con apertura esclusa e barra qualificante nello stesso dispatch; vedi sotto.)*
- **Non raggiungibile su dati completi.** Un PRICE_PREMISE_FAILED di A confermato prima di un contatto V, perché V = R − z sta sopra A.
- v0.6 e HDP-001 restano invariati; gli studi restano INACTIVE.


## Completamento della review (13 ottobre 2026, base `048bf2d`)

Richiesta del Director, relayata dall'Owner. Consegna dell'executor; la review del Director è pendente. Nessun pull o fetch; checkout su `main` = `origin/main` = `048bf2d`, con un file vuoto non tracciato `0` estraneo, lasciato intatto e non committato.

**Nessuna modifica al motore o ai metodi.** `core_a2x.py`, `core3.py`, `methods.py` e gli altri sorgenti sono invariati. Si aggiungono soltanto nastri e prove sintetiche, e una registrazione documentale. Nessuna modifica metodologica, UI o attivazione della variante.

### 1. Contesto 1h e espansione 15m avversa

Gate A ordinario: contesto 1h concorde (UP per LONG, DOWN per SHORT) e nessuna EXPANSION 15m nella direzione avversa. Ogni nastro passa dall'ingresso ordinario a freddo, senza stati predisposti. Ogni nastro contrario ha un **controllo** che differisce solo dove si decide il gate.

**Come si ottiene il contesto 1h non concorde** (`ctx_balanced_from_0500`):
- si cambia una sola barra 15m del giorno 1: la chiusura 1h [20:00,21:00) diventa 98500 invece di 97000 (TR 1h sempre 2000);
- alle 04:00 le nove chiusure 1h danno spostamento 2950/2000 = 1,475 ed efficienza 2950/5950 = 0,496: UP, quindi nascita, ARM, REVISE e conferma di S1 restano invariati;
- alle 05:00 lo spostamento è (X − 98500)/2000 < 1 per ogni X < 100500: BALANCED, senza alcuna EXPANSION;
- sulla storia originale la stessa chiusura delle 05:00 resta UP (controllo).

**Come si ottiene l'espansione 15m avversa.** Alle 04:45 le sette chiusure sono 100250, 100700, 100049,9, 99950, c(04:15), c(04:30), c(04:45). Il contesto 1h resta UP.

| Caso | Causa | Atteso dal disegno | Osservato (LONG; SHORT speculare) | Controllo |
|---|---|---|---|---|
| Fallimento con gate già contrario | 1h | Nessuna riserva; v0.6 (owner rilasciato) | V toccato [05:04,05:05), tf 05:05: `REVIEW_NOT_OPENED` `CONTEXT_OR_ADVERSE_EXPANSION:BALANCED/TRANSITION:None`; journal identico a v0.6 salvo l'osservazione | Storia originale: `REVIEW_OPEN` alle 05:05 |
| Fallimento con gate già contrario | 15m | Idem | Contatto sulla frontiera [04:44,04:45) con chiusura 98500: S15 1075, spostamento6 −1,628, ER6 0,660 → EXPANSION DOWN a tf 04:45: `REVIEW_NOT_OPENED` `…:UP/EXPANSION:DOWN` (SHORT `…:DOWN/EXPANSION:UP`); identico a v0.6 | Chiusura 99600: `REVIEW_OPEN` |
| Riesame aperto, poi gate contrario | 1h | Chiusura WITHDRAWN, rilascio, latch ordinario | Aperto 04:04; barre quiete senza chiusura contraria; la chiusura 1h delle 05:00 rende BALANCED: `REVIEW_CLOSED WITHDRAWN` alle 05:00 (new_bars 2) | La stessa reazione fresca arma alle 05:15 (recupero 05:16 escluso: 14 min) |
| Riesame aperto, poi gate contrario | 15m | Idem | Aperto 04:41 (contatto [04:40,04:41)); la barra del fallimento [04:30,04:45), mai fatto nuovo, completa l'EXPANSION alle 04:45: `REVIEW_CLOSED WITHDRAWN` (new_bars 0) | Chiusura 99400: il riesame resta aperto e arma alle 05:15 |
| Barra qualificante nello stesso dispatch del gate contrario | 1h | Il gate precede la formazione (§6): nessun successore | [04:45,05:00) (h 100050, l 99650, c 99750: contraria, R2 < R1) chiude alle 05:00, quando il contesto diventa BALANCED: `REVIEW_CLOSED WITHDRAWN`; new_bars 2, contrary false, minimo 99930 (la barra non è conteggiata) | ARM alle 05:00 (K2 100050, R2 99650) |
| Barra qualificante nello stesso dispatch del gate contrario | 15m | Idem | [04:30,04:45) (l 98950, c 99000 < 99460) qualifica alle 04:45, dove S15 675, spostamento6 −1,852, ER6 0,576 → EXPANSION DOWN: `WITHDRAWN`; new_bars 1, contrary false, minimo 99300 | Barra (l 99250, c 99300): ARM alle 04:45 (K2 99470), conferma alle 04:46 |

**Verificato su ogni caso:**
- **motivo.** 1h = contesto BALANCED senza EXPANSION nel motivo; 15m = contesto concorde con EXPANSION avversa;
- **rilascio e latch.**
  - Durante il riesame: owner `<S1>#review` e latch NEED_FALSE (nessun falso accantonato).
  - Al dispatch di chiusura: owner nullo e latch READY, perché il Q_A falso è osservato dopo il rilascio. È lo stesso valore di v0.6 in quel momento.
  - Dopo la chiusura, scenari, figli e call sono identici a v0.6.
- **nessuna riapertura.**
  - Una chiusura oltre il vecchio K, una reazione fresca qualificante e il suo recupero successivi non producono osservazioni, successori o nuove conferme di S1.
  - Nel caso 15m la reazione completa alle 05:15 incontra di nuovo un gate concorde (UP, non EXPANSION).
- **restore prima del cambiamento.** Codec di produzione `pack_runtime/unpack_runtime`:
  - percorso 1h "stesso dispatch": tagli 04:45, 04:59, 05:00;
  - percorso 15m "riesame aperto": tagli 04:41, 04:44, 04:45;
  - LONG e SHORT.
  - Esito: digest dei record identici alla corsa ininterrotta. Prima del cambiamento la riserva è ripristinata (bars, contrary, owner, latch NEED_FALSE); dopo, nessun riesame, owner nullo e latch READY.

Prova di non vacuità: con il gate disattivato nel codice della variante (prova di mutazione locale, annullata con `git checkout`), tutte le 16 nuove prove falliscono.

### 2. Registrazione sperimentale dei record

[`src/algotrader/adviser/method/A2X-EXPERIMENTAL-RECORDS.json`](../../../src/algotrader/adviser/method/A2X-EXPERIMENTAL-RECORDS.json), `algotrader.semantic.v2.experimental-values.a2x` revisione 1, stato `EXPERIMENTAL_NOT_PUBLIC_NOT_A_SEMANTIC_V2_REVISION`.

**Cosa registra:**
- l'osservazione `structure/a_second_attempt` con `decision_role` A_SECOND_ATTEMPT_RESERVATION. Per ciascuna delle sei categorie: chiavi dei valori, motivi (REVIEW_NOT_OPENED) o coppie stato→codice (REVIEW_CLOSED), formato dei dettagli e lineage;
- il successore:
  - formato dell'id;
  - chiavi `setup` aggiunte (attempt, impulse_id, parent_scenario_id, review_opened_at, formation_origin, failed_attempt_R);
  - renewal `SECOND_ATTEMPT`;
  - motivo ARM e motivo terminale aggiunti;
  - lineage (successore, impulso);
- il figlio, senza valori nuovi;
- la call: `hard_deadline_origin` `ORIGINAL_IMPULSE_EXPIRY`, e la call del primo tentativo resta `STRUCTURAL_CONFIRMATION_PUBLICATION`;
- i tre ruoli. La **riserva** non è un record né uno scenario: il suo token `<impulse>#review` appare solo nello stato e in `ORDINARY_BIRTH_DEFERRED.reserved_by`;
- l'elenco dei valori esercitati da nastri sintetici.

**Cosa resta invariato:**
- `SEMANTIC_V2_REVISION` = 5 con 5 voci di changelog;
- nessuna voce per il modello in `SEMANTIC_V2_EMITTED_REVISION`;
- `KIND_CONTRACTS_V6` e `schemas/algotrader.semantic.v2.json`;
- il file è fuori dal manifest delle regole e dal registro, quindi le identità v0.6 e v0.6-a2x restano quelle di `048bf2d` (hash fissati nei test).

La variante non è presentata come release pubblica. Una pubblicazione richiederebbe comunque una revisione approvata dal Director.

**Verifiche mirate:**
- `test_record_registration_is_additive_experimental_and_outside_every_identity`: identità della variante, contratto pubblico invariato, file fuori dalle identità, costanti del codice uguali ai valori registrati.
- `test_every_emitted_variant_value_is_registered_and_the_coverage_is_declared`. Su 58 corse (29 nastri × LONG/SHORT, staleness inclusa):
  - ogni osservazione ha categoria, chiavi esatte, valori stringa/null, lens, ruolo, lineage e motivo registrati;
  - ogni record del successore ha esattamente le chiavi aggiunte, renewal, lineage e motivi registrati;
  - i record del primo tentativo non contengono nessun valore aggiunto;
  - solo le call dei successori hanno `ORIGINAL_IMPULSE_EXPIRY`;
  - nessun id di record contiene il token della riserva;
  - l'insieme esercitato coincide con quello dichiarato.
- `test_variant_records_serialize_exactly_through_the_revision_5_contracts`: osservazioni, scenari, figli, call e revisioni dei successori. Validazione con i contratti revisione 5, round trip JSON esatto, digest del journal uguale allo sha256 dei byte canonici.
- `test_first_attempt_reservation_and_successor_are_distinct_in_records_and_state` (LONG/SHORT):
  - S1 solo vocabolario v0.6, con terminale RELEASED come in v0.6;
  - riserva come osservazione nello stesso dispatch, legata al solo impulso, e come token di stato;
  - successore con id, lineage, figlio e call propri;
  - round trip esatto del codec di stato con riserva aperta e con successore confermato (R1 congelato).

**Valori registrati senza nastro dedicato**, dichiarati nel file:
- REVIEW_NOT_OPENED: EVALUATION_TAIL, AT_OR_AFTER_ORIGINAL_EXPIRY, DISCOVERY_OWNER_ALREADY_RELEASED, DESTINATION_CONTACT_IN_FAILURE_DISPATCH, REQUIRED_DATA_NOT_READY;
- REVIEW_CLOSED: REQUIRED_INPUT_STALE, REQUIRED_GAP_15m, DESTINATION_CONTACT_TIME_AMBIGUOUS, EVALUATION_WINDOW_ENDED.

### Mappa requisiti → prove (aggiunte)

| Requisito | Prova |
|---|---|
| Riesame non aperto con gate contrario al fallimento, 1h e 15m | `test_a_contrary_gate_at_the_failure_never_opens_a_review` |
| Riesame aperto chiuso quando il gate diventa contrario; rilascio, latch, nessuna riapertura | `test_an_open_review_ends_when_the_gate_turns_contrary` |
| Nessun successore da una barra qualificante nello stesso dispatch del gate contrario | `test_a_bar_qualifying_in_the_dispatch_where_the_gate_turns_contrary_arms_nothing` |
| Restore prima del cambiamento | `test_restore_before_the_gate_change_reproduces_the_uninterrupted_run` (1h e 15m) |
| Registrazione additiva sperimentale, identità invariate | `test_record_registration_is_additive_experimental_and_outside_every_identity` |
| Valori emessi = valori registrati; copertura dichiarata | `test_every_emitted_variant_value_is_registered_and_the_coverage_is_declared` |
| Serializzazione | `test_variant_records_serialize_exactly_through_the_revision_5_contracts` |
| Primo tentativo, riserva e successore distinti | `test_first_attempt_reservation_and_successor_are_distinct_in_records_and_state` |

### Controlli eseguiti (13 ottobre)

- **Suite della variante** `tests/test_a2x_second_attempt.py`: **133 passati** (112 precedenti + 21 nuovi), 0 falliti.
- **Parità e contratti** interessati: **356 passati**, 0 falliti, 0 skippati.
  - File: `test_mp005_paths` (i 75 nastri della parità), `test_mp005_versions`, `test_mp004_versions`, `test_mp002_versions`, `test_schema`, `test_contracts`, `test_adviser_method`.
- **Suite completa non ripetuta.** Nessuna modifica condivisa: nessun sorgente cambiato, solo un file JSON nella cartella `method` e i test della variante.
- **Restano non verificati, e non vanno presentati come superati:**
  - **255 test DB non eseguiti localmente**: manca `ALGOTRADER_TEST_DATABASE_URL`;
  - **e2e non eseguiti**;
  - **CI non verificata**: PENDING / NOT CHECKED, a cura dell'Owner;
  - lint non eseguito: nessun linter configurato o installato.

### Limiti aggiornati

- **Solo prove sintetiche.** Nessun dato Owner, acquisizione, replay reale, conteggio sui 28 casi, backtest o valutazione economica. L'utilità della politica resta ignota.
- **Contesto 1h nei nastri.** Si ottiene modificando una barra della storia del giorno 1: è un input di ingegneria, non un caso di mercato. Prima di H0 nessuna nuova chiusura 1h può far tornare il contesto concorde, quindi la non riapertura con gate di nuovo concorde è mostrata sul percorso 15m.
- **Terminale di S1.** Anche quando la riserva si apre, il record terminale di S1 dice `discovery_owner` RELEASED, perché è identico a v0.6 per costruzione. La riserva risulta dall'osservazione REVIEW_OPEN dello stesso dispatch: va letta insieme a quella.
