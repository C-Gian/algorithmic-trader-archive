# A — confronto del ragionamento professionale con v0.6: il pullback complesso

12 ottobre 2026, base `58ff69a`, branch main. Consegna dell'executor; la review del Director è pendente.

È un confronto documentale e di codice. Non contiene implementazioni, nuove misure o soglie, e non riapre E né la componente ciclica Evoluta. Non ci sono nuove acquisizioni, nuovi replay, accessi allo stack Owner o ai periodi protetti, né risultati economici.

## Conclusione

**Differenza concreta da affrontare.**

Supponiamo che un primo tentativo di ripresa fallisca e che il nuovo ramo contrario arrivi a V (il minimo della reazione meno z). Per v0.6 l'aspettativa sopravvive o muore a seconda di un solo fatto: se quel tentativo aveva già prodotto una chiusura 1m ≥ K + 1 tick.
- **Senza conferma**, v0.6 perde soltanto l'ancora e poi riarma. Lo scenario e l'aspettativa restano.
- **Dopo la conferma**, lo scenario termina INVALIDATED. Un'aspettativa di continuazione nella stessa direzione torna solo con una nuova nascita.

Nella fonte, un primo tentativo di ripresa fallito è ciò che definisce il pullback complesso: un secondo tentativo può riuscire. Nei materiali raccolti la fonte non fa dipendere questo mantenimento dall'aver superato una soglia d'ingresso.

## 1. L'esempio scelto e ciò che afferma

**Fonte.** Adam Grimes, *Fundamental Trading Patterns* (EXT-001, [`knowledge/external_registry.yaml`](../knowledge/external_registry.yaml)). Il testo è stato letto per intero da RP-001 il 30 settembre 2026; qui si usano le citazioni e le sintesi registrate in [RP-001A](../research/first_trader/RP-001A-PROCESS-TRANSLATION.md) (punto 1 delle fonti e tabella delle esclusioni). La pagina non è stata riletta.

**Perché questo esempio.** Fra i materiali raccolti è l'unico esempio a solo prezzo il cui contenuto registrato copre tutti e cinque i passaggi.
- EXT-002 (l'esempio S&P di *One step ahead…*) non ha una condizione operativa registrata. Inoltre la direzione di "reaction" e "the other side" è ambigua nella parafrasi registrata.
- I casi LIB-005 (Chiu, Bandazian, Berry, Russo) sono sintesi di dossier, basate su notizie, fondamentali o posizionamento che v0.6 non riceve. Il confronto ribadirebbe soltanto un'informazione mancante.

| Passaggio | Ciò che il trader afferma (registrato) | Ciò che interpretiamo noi |
|---|---|---|
| Osservazioni | Mercato in trend: alternanza di gambe col trend e pullback contro il trend | Che "trend" e "pullback" siano riconoscibili con le nostre regole su 15m e 1h |
| Aspettativa | Il pullback è "a trade intended to enter a trending market": il trend dovrebbe riprendere | Nessuna destinazione numerica: B è una convenzione nostra |
| Condizione operativa | Entrare "as the market turns back into the trend (on a breakout of the pattern)", oppure vicino al minimo (failure test, escluso da A) | Quale sia il confine del "pattern": non è registrato |
| Nuove osservazioni | Pullback complesso: due o più gambe contro il trend, con un primo tentativo di ripresa fallito | La profondità del secondo ramo rispetto al primo; se il primo tentativo aveva soddisfatto la condizione d'ingresso |
| Mantenimento o revisione | Il primo tentativo può fallire prima che riesca il secondo; queste strutture possono precedere movimenti forti | Nulla sulla posizione (uscita, mantenimento, rientro) né su quando abbandonare la tesi |

## 2. Confronto passo per passo con v0.6

Parametri v0.6 da `MP-005-PARAMETERS.json`, invariati da MP-002.

| Passaggio | Informazione del professionista | Informazione disponibile a v0.6 | Decisione delle regole attuali | Esito |
|---|---|---|---|---|
| Osservazioni | Trend, gamba col trend, pullback | Barre trade 15m complete, contesto 1h. Q_A: 7 barre 15m, efficienza ≥ 0,55, spostamento ≥ 1,5 S15, contesto 1h concorde (`core._qa`) | BIRTH con A/B dalle 7 barre. ARM quando la reazione ha una chiusura inferiore, R < B − 0,25 S15 e R > A+z, entro 8 barre 15m (`core4._a_close`) | **Corrispondenza** nel tipo; tutte le soglie sono nostre |
| Aspettativa | Ripresa del trend | Scenario A condizionale verso B. MarketView condizionale, senza probabilità | Lo scenario è pubblicato e monitorato anche senza call | **Corrispondenza** |
| Condizione operativa | Ripresa nella direzione del trend, rottura del pattern | K = massimo della barra 15m che contiene R; V = R − z | Conferma alla prima chiusura 1m ≥ K + 1 tick (`core3._confirmations`). La call non coincide con la conferma: segue il figlio d'ingresso (IMMEDIATE, oppure RETURN con riferimento locale v0.5 e compatibilità iniziale v0.6) | **Non determinabile**: il "pattern" non è definito. v0.6 usa una sola barra, non l'intero pullback. Sulle 64 conferme Q4 (stesse regole d'ancora), K − R vale da 0,47 a 3,05 S15, mediana 1,01 |
| Nuove osservazioni: primo tentativo fallito, secondo ramo contrario | Il tentativo fallisce, il pullback continua | Chiusure e contatti 1m rispetto a K e V; chiusure 15m rispetto ad A+z | (a) Prima della conferma: REVISE se il nuovo minimo resta sopra V; ANCHOR_LOST se tocca V, poi REARM su una reazione 15m più profonda e pulita (`core4._scen_interval`, `_anchor_lost`, `_a_close`). (b) Dopo la conferma, con il figlio in attesa RETURN e ritorno nel corridoio sopra V: riferimento locale e una sola ripresa locale valutabile per la call (`core5._response_step`). (c) Dopo la conferma, contatto con V: INVALIDATED (`core3._scen_interval`) | (a) **corrispondenza**; (b) **corrispondenza parziale** (un solo secondo tentativo, con regole nostre); (c) vedi sotto |
| Mantenimento o revisione | Struttura ancora valida: il secondo tentativo può riuscire | Gli stessi record | (a) Stesso scenario e stesso owner, R/K/V nuovi. (b) Scenario CONFIRMED; una contraddizione locale chiude solo il figlio, senza un terzo tentativo. (c) Scenario terminato; l'owner, se ancora attivo, è rilasciato. Una nuova A nella stessa direzione nasce solo dalla qualificazione ordinaria, Q_A falso e poi vero su 7 nuove barre (`core3._scen_end`, `_a_births`) | (c) **differenza** |

**Assenza di call non significa assenza di analisi.**
- Nei rami (a) e (b) l'aspettativa resta pubblicata senza call.
- Nel ramo (c) MarketView, contesto, fase e le altre famiglie continuano. Ciò che sparisce è l'aspettativa di continuazione di *quel* movimento.

**Funzione prevista o capacità dimostrata.** I rami (a), (b) e (c) sono comportamenti dimostrati su nastri sintetici (§4). Sul periodo di sviluppo sono contati soltanto come record del motore, non come esiti di prezzo.

## 3. Il punto preciso

Lo stesso secondo ramo contrario (minimo ≤ V, chiusure 15m sopra A+z) produce due decisioni diverse. L'unica cosa che cambia è se prima c'è stata una chiusura 1m ≥ K + 1 tick.

| Stato al contatto con V | Codice | Aspettativa |
|---|---|---|
| ARMED (non confermato) | `core4.py:89-115` `_scen_interval` → `_local_contact` → `_anchor_lost` (WATCH, owner occupato); `core4.py:245-248` REARM | Mantenuta, con condizione rivista |
| CONFIRMED | `core4.py:91` delega a v0.3 → `core3.py:637-645` `hit_v` → `_scen_end(INVALIDATED, V_CONTACT)`; `core3.py:531` owner rilasciato; `core3.py:778-803` rinascita solo con il latch | Abbandonata |

**Da dove viene la regola.**
- Regola: [MP-003 §5](MP-003-A-REACTION-ANCHOR-DISPOSITION.md): "From the FIRST valid confirmation onward there is no R/K/V re-anchoring … Frozen V contact invalidates the confirmed scenario … WAIT cannot return to reaction formation."
- Origine: RP-001C C13 ("no re-entry"). RP-001A la registrava come "a known coverage loss" proprio per i pullback complessi.
- È una scelta deliberata, non un difetto di implementazione.

**Da non confondere.** Un contatto con V che chiude una call emessa è guida protettiva e resta corretta. La differenza riguarda l'aspettativa strutturale, non lo stop della call.

v0.6 separa già il figlio d'ingresso dallo scenario: `INITIAL_RESPONSE_INCOMPATIBLE` e `LOCAL_RESPONSE_CONTRADICTED` chiudono soltanto il figlio. Non applica la stessa separazione al contatto con V dopo la conferma.

**Ciò che la fonte non decide.**
- Se Grimes manterrebbe la tesi quando il secondo ramo scende oltre il primo minimo di più di z.
- Dove finisca un pullback complesso.
- Se il trader fosse già in posizione.

La differenza è quindi questa: il discriminante di v0.6 (K superato oppure no) non ha corrispondenza nella fonte, e nel ramo (c) v0.6 elimina proprio la possibilità che la fonte nomina. Non dimostra che il mantenimento sarebbe migliore.

## 4. Evidenze riusate

**Sintetiche.** Test esistenti, rieseguiti su `58ff69a`: 120 passati in 232 s.
- `test_mp003_paths.py`:
  - `::test_local_contact_invalidates_only_the_anchor_and_a_deeper_reaction_rearms_prospectively`, sul nastro `contact_then_rearm`. ARM a R 100000, K 100700, V 99800; contatto a 99790; REARM a R 99790, K 100300; nuova conferma. Ramo (a).
  - `::test_supersession_without_contact_keeps_the_inherited_inclusive_tie`: ramo (a), REVISE.
  - `::test_confirmed_wait_v_contact_is_terminal_with_no_reanchor`, sul nastro `a3_wait_v_contact_then_rebound`. A 97000, B 100900; dopo il REVISE R 99900, K 100049,9, V 99700; conferma 04:01 a 100050; il minuto successivo tocca 99700; rimbalzo a 100500. Risultato: INVALIDATED, nessun REARM, nessuna call. Ramo (c), con la forma del pullback complesso.
  - `::test_issued_call_v_contact_keeps_the_existing_protection_identical_to_v03`.
- `test_mp004_paths.py`:
  - `::test_valid_first_recovery_issues_once_at_its_own_close`: ramo (b).
  - `::test_intermediate_violation_terminates_and_a_later_recovery_never_reopens`: ramo (b), contraddizione.
- Parità fra versioni, che include questi nastri:
  - `test_mp004_versions.py::test_v05_equals_v04_outside_the_a_return_child`;
  - `test_mp005_paths.py::test_v06_equals_v05_outside_the_new_terminal`.

**Storiche.** Solo record del motore già committati, rielaborati da [`evidence/A-PROFESSIONAL-REASONING-COMPARISON/tabulate_existing.py`](evidence/A-PROFESSIONAL-REASONING-COMPARISON/tabulate_existing.py) → [`counts.json`](evidence/A-PROFESSIONAL-REASONING-COMPARISON/counts.json) (identico alla seconda esecuzione).

**v0.6, owner nati in Set–Dic 2025** (`A-REACTION-EFFICIENCY-EXPLORATION/results.json`):

| Misura | Valore |
|---|---|
| Owner armati | 161 |
| … che hanno perso almeno un'ancora | 111 |
| … che hanno riarmato | 99 |
| Conferme | 89, di cui 61 dopo un REARM |
| Terminali delle conferme | 54 DESTINATION_REACHED, **28 INVALIDATED per V_CONTACT**, 4 TIME_EXPIRED, 3 STALLED |

Dopo quei 28 contatti, la nascita successiva di una A nella stessa direzione arriva fra 42 minuti e circa 4 giorni dopo: 6 entro 2 ore, 12 entro 4 ore.

**v0.4, ottobre–dicembre 2025** (`WP-012-OWNER-Q4-DIAGNOSIS/confirmations.csv`): 64 conferme, di cui 16 terminate INVALIDATED; K − R come in §2.

## 5. Verifica minima proposta prima di correggere (non eseguita)

1. **Nastro sintetico a coppie, senza dati.**
   - La geometria `a3_base` in due varianti, identiche tranne la chiusura del primo tentativo: 100049,9 (sotto K + tick) contro 100050 (conferma).
   - Lo stesso secondo ramo sotto V e sopra A+z, poi la stessa ripresa fino a B.
   - Asserzioni attese con le regole attuali: la prima variante dà ANCHOR_LOST, REARM e un nuovo CONFIRM, con lo scenario vivo fino a B; la seconda dà INVALIDATED e nessuno scenario fino a una nuova nascita.
   - Isola il discriminante in un test, senza cambiare regole.
2. **Rilevanza, solo su record di sviluppo già esposti.**
   - Per i 28 casi v0.6 del ramo (c), contare quanti mostrano, prima della scadenza originale, una nuova chiusura oltre K oppure il contatto con B, senza una chiusura 15m ad A+z o oltre.
   - Richiede i prezzi 1m del pack Set–Dic, oggi fuori da Git: serve un'autorizzazione esplicita.
   - Non è una valutazione di profitto. Non sceglie soglie e non fornisce il confine del pullback complesso.

Una correzione richiederebbe poi un criterio professionale per la fine del pullback complesso (la fonte registrata non lo fornisce) e una nuova versione del metodo, decisa dal Director.

## 6. Limiti

- Il testo primario di Grimes non è nel repository e non è stato riletto: si usano le citazioni registrate. Si tratta di una descrizione di pattern, non di un episodio con prezzi; non riguarda BTC.
- v0.6 non registra i rimbalzi intermedi. Un ANCHOR_LOST è un approfondimento della reazione, non necessariamente un tentativo fallito, quindi i conteggi non identificano i pullback complessi.
- I conteggi sono record del motore su periodi di sviluppo esposti (registro esposizioni, riga 13), non esiti di prezzo.
- I dati Q4 sono v0.4. L'uguaglianza strutturale con v0.6 è provata su nastri sintetici, non riverificata sui dati reali.
- v0.6 e HDP-001 restano congelati; gli studi futuri restano INACTIVE. Nessuna attività successiva viene attivata.
