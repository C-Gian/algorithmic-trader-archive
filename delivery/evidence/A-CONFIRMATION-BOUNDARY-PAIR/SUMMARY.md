# A v0.6 — confine conferma / perdita dell'ancora: verifica sintetica a coppie

12 ottobre 2026, base `0deb61e`, branch main. Evidenza dell'executor; la review del Director è pendente. Nessuna regola modificata. È la verifica proposta al §5 punto 1 del [confronto](../../A-PROFESSIONAL-REASONING-COMPARISON.md). Il conteggio sui 28 casi reali non è stato eseguito.

## Costruzione

Due nastri OHLC fatti a mano (input d'ingegneria, non dati di mercato) sulla geometria A LONG di `a3_base`:
- A 97000, B 100900, S15 2000, z 200;
- BIRTH 03:30 e ARM 03:45;
- REVISE alle 04:00, con R 99900, K 100049,9 e V 99700. La soglia di conferma è K + 1 tick = 100050.

**L'unica differenza** è la chiusura del minuto [04:00,04:01), il primo tentativo di ripresa:

| Variante | Chiusura del primo tentativo |
|---|---|
| **N** | 100049,9, appena sotto K + tick |
| **C** | 100050, esattamente a K + tick |

Apertura, massimo e minimo di quel minuto sono uguali. Mark e index sono fissati a 100050 in entrambe le varianti.

**Identico in entrambi i nastri:**
- **Contatto con V.** [04:01,04:02) o 100050 h 100050 l 99700 c 99950. Nessuna chiusura 15m scende ad A+z (97200), quindi la premessa non cede.
- **Reazione successiva.** Deriva fino a 99800: la barra 15m [04:00,04:15) ha h 100050, l 99700, c 99800.
- **Ripresa.** Sale a 100150 entro le 04:25, poi a 100950 (oltre B) entro le 05:05, poi una coda piatta.

La coppia SHORT è la riflessione intorno a 100000.

**Esecuzione.** Entrambi i nastri passano per l'ordine ordinario del kernel puro v0.6: evento di feed → clock temporale → barriere professionali → ammissione (`harness.run_pure`). Lo stato codificato è letto in sola lettura dopo i dispatch delle 04:00, 04:01, 04:02, 04:15, 04:23, 05:03 e 05:30. Il journal letto con le pause è identico a quello di un'esecuzione senza pause. Nessuno stato è stato inserito e nessun gate aggirato.

## Isolamento: che cosa cambia davvero

| Livello | Risultato (LONG e SHORT) |
|---|---|
| Eventi di feed | Differisce **un solo** evento: la barra trade delle 04:00. Nel payload cambiano `close` e `volume_quote` (l'harness lo calcola come chiusura × volume, e il volume non entra nelle regole A) |
| Journal prima delle 04:01 | Identico |
| Journal prima del contatto con V (04:02) | Solo C pubblica alle 04:01: `scenario` CONFIRM, `entry_attempt` WAIT_OPEN, `market_view` CONFIRMED. N non pubblica nulla di proprio |
| Osservazioni e landmark | Identici su tutto il nastro |
| Call | Nessuna in entrambe le varianti |
| Aggregazioni e stato derivato del mercato | Identici a ogni snapshot, eccetto la finestra di dislocazione. Coincidono: barre 15m/1h/broad, S15 e la sua storia, fase, contesto, partecipazione, landmark, pivot, box, Q_A, funding, eventi |
| Dislocazione | Nella base di 60 slot, il solo slot delle 04:00 vale circa −0,01 bps in N e 0 in C, per gli effetti di trade/mark e trade/index. È visibile dalle 04:01 alle 04:23 ed esce dalla finestra prima delle 05:03. Non pubblica nulla: le osservazioni restano identiche |
| Stato di rinnovo A | In C l'owner è rilasciato alle 04:02, e il latch passa a READY al Q_A falso delle 04:15. In N l'owner resta occupato fino a B (05:03). Il latch differisce dalle 04:15 alle 05:03, poi converge |
| Nascita successiva | La nascita A delle 05:30 è lo stesso record in N e in C |

Quindi una sola chiusura non lascia invariata ogni derivazione: lascia una traccia nella dislocazione e nello stato di rinnovo. Su questo nastro nessuna delle due tracce cambia una pubblicazione, a parte quelle dovute alla conferma stessa.

## Sequenza comparata (LONG; SHORT speculare)

| Ora | Osservazione | N: scenario / aspettativa / condizione pubblicate | C: scenario / aspettativa / condizione pubblicate |
|---|---|---|---|
| 04:00 | Reazione rivista | ARMED. Vista UP condizionale: "chiusura 1m ≥ 100050 con minimo > 99700 conferma la continuazione verso 100900" | Uguale |
| 04:01 | Primo tentativo chiude a 100049,9 (N) oppure a 100050 (C) | Nessun cambiamento: resta ARMED con la stessa condizione | CONFIRMED. Vista: "continuazione verso 100900 finché V 99700 tiene, entro le 08:01". Figlio d'ingresso in WAIT (IMMEDIATE con reward/risk insufficiente, corridoio RETURN usabile) |
| 04:02 | Minimo 99700 = V | **ANCHOR_LOST**: stesso scenario e stesso owner, in WATCH. Vista WATCH_ONLY: "in attesa di una nuova reazione completa oltre la R persa 99900" | **INVALIDATED**: scenario terminato, figlio chiuso, owner rilasciato. Vista NO_QUALIFIED_STRUCTURE, UNCERTAIN |
| 04:15 | Barra 15m di reazione (l 99700, c 99800) | **REARM** sullo stesso impulso: R 99700, K 100050, V 99500. Vista UP condizionale: "chiusura ≥ 100050,1 con minimo > 99500" | Nessuno scenario A; vista NO_QUALIFIED_STRUCTURE |
| 04:23 | Ripresa oltre K | **CONFIRM** e figlio in WAIT. Vista CONFIRMED, V 99500, entro le 08:23 | Nessuno scenario A |
| 04:53 | Il prezzo raggiunge cap/target prima di un ritorno | Figlio chiuso per PRE_ENTRY_TARGET_CONTACT, senza call | — |
| 05:03 | Contatto con B 100900 | **DESTINATION_REACHED** | Nessuno scenario A ad attenderlo |
| 05:30 | Q_A vero sulle 7 barre della risalita | Nuova nascita A (nuovo impulso, B 100955), identica in N e in C | Uguale |

## Le tre cose da non confondere

1. **Protezione di una call emessa.** In nessuna delle due varianti è stata emessa una call: in C il figlio era in WAIT e si chiude con lo scenario. Quando una call è emessa, il contatto con V la chiude INVALIDATED: è guida protettiva, documentata dal test esistente `test_mp003_paths.py::test_issued_call_v_contact_keeps_the_existing_protection_identical_to_v03`. La coppia non la modifica né la mette in discussione.
2. **Conclusione dell'ipotesi confermata.** In C il contatto con V termina l'ipotesi confermata alle 04:02 (`core3._scen_interval`, MP-003 §5). In N la stessa barra chiude solo l'ancora (`core4._scen_interval` → `_anchor_lost`).
3. **Riconoscere la continuazione con una nuova reazione, senza un nuovo impulso.**
   - N la riconosce: REARM alle 04:15 sullo stesso owner e sullo stesso impulso A/B, conferma alle 04:23, B alle 05:03.
   - C no: dalle 04:02 alle 05:30 non esiste alcuno scenario A in quella direzione. L'unico riconoscimento successivo è una nascita da un nuovo impulso, alle 05:30, formato dalla risalita stessa dopo il contatto con B.

## Conclusione circoscritta

Su questa coppia di nastri, con tutto il resto identico, una chiusura 1m di 0,1 sotto oppure a K + tick decide se lo stesso contatto con V è:
- la perdita di un'ancora, seguita dal riarmo sulla reazione successiva, dalla conferma e dal raggiungimento di B nello stesso scenario;
- oppure la fine dell'ipotesi confermata, senza aspettativa A in quella direzione per 88 minuti, fino a un nuovo impulso.

Prima del contatto, la variazione produce soltanto la conferma e le sue conseguenze dirette (record delle 04:01). In più lascia una traccia non pubblicata nella base di dislocazione e, dopo il contatto, nello stato di rinnovo.

Questo descrive il comportamento delle regole v0.6, non un difetto. La fonte raccolta (Grimes, EXT-001) non definisce la validità del secondo ramo, quindi non indica quale dei due trattamenti sia corretto.

## Controlli e file

- **Script.** [`pair.py`](pair.py) → [`comparison.json`](comparison.json), identico byte per byte alla riesecuzione (sha256 `eda889c2…5925`).
- **Test.** [`tests/test_a_confirmation_boundary_pair.py`](../../../tests/test_a_confirmation_boundary_pair.py): 10 test su LONG e SHORT. Verificano la differenza degli eventi, il journal prima del contatto, i cicli di vita, gli effetti sullo stato derivato, l'equivalenza fra esecuzione con pause e senza, e la coerenza del JSON committato.
- **Esecuzione.** Con le suite `test_mp003_paths.py`, `test_mp004_paths.py` e `test_mp005_paths.py`: 221 test passati.
- **Non eseguiti.** Lint (ruff non installato) e suite complete: il codice di prodotto non è cambiato.

## Limiti

- **Un solo caso.** Una geometria a mano, con le due varianti speculari; nessuna frequenza e nessun dato reale.
- **Valori scelti.**
  - Mark e index sono fissati per isolare la chiusura trade.
  - Con mark e index uguali alla chiusura (default dell'harness), differirebbero anche le barre mark/index della stessa ora.
- **Specifico di questo nastro.**
  - Il figlio d'ingresso non arriva mai a una call.
  - L'esito del secondo figlio in N dipende dalla geometria economica di questo nastro.
- **Fuori dall'ambito.** Nessuna acquisizione, accesso Owner, periodo protetto o CI. E non è riaperto; il RETURN non è modificato. v0.6 e HDP-001 restano invariati; gli studi restano INACTIVE.
