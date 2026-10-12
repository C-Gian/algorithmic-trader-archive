# A dopo la conferma — revisione dell’aspettativa
12 ottobre 2026. Review del Director su codice e specifiche a `8a55029`. Design documentale soltanto: nessuna implementazione, nuova misura, soglia, estrazione, prova o esito Owner consultato.

## Decisione
**Capacità già presente da rendere esplicita, entro i limiti della lettura pubblicata.** v0.6 distingue sopravvivenza strutturale, controevidenza corrente e verifica temporale del progresso. Non è corretto presentare una tesi CONFIRMED aperta come se tutte le ragioni iniziali fossero confermate di nuovo. Non emerge da questi materiali una regola sufficientemente motivata per aggiungere un giudizio globale di “tesi indebolita” o un nuovo terminale.

La formulazione fedele è: **la continuazione resta una tesi condizionale, confermata a un istante noto; indicare separatamente ciò che la contrasta ora, ciò che resta da verificare e ciò che non è valutabile.** Questo è un contenuto di spiegazione proponibile, non autorizzazione a cambiare il prodotto.

## Fonti e natura della verifica
Lettura statica diretta: `core.py`, `core3.py`, `core4.py`, `core5.py`, `core6.py`, `params.py`; MP-002-SCENARIO-CONFIRMATION-ENTRY-PROPOSAL §§3–4 e relativo WP-011; RP-001A-PROCESS-TRANSLATION §§fonti/A6/A7 e `knowledge/external_registry.yaml`.
v0.4 conserva per A confermata il ciclo v0.3; v0.5/v0.6 modificano il tentativo locale RETURN, non istituiscono una nuova revisione globale della tesi. RETURN ed E non sono riaperti.

Grimes EXT-001 sostiene l’alternanza di movimenti e reazioni, compresa una ripresa iniziale fallita; EXT-002 e le sintesi LIB-005 richiamate da RP-001 sostengono l’importanza della risposta rispetto all’attesa. Qui sono consultati i materiali già raccolti, non nuovamente gli articoli o i libri. Non forniscono una regola BTC per pesare una fase contraria, decidere quando una vecchia prova di progresso perda valore o abbandonare una tesi. Le soglie correnti sono convenzioni del metodo, non regole attribuite a Grimes.

Nessun test eseguito: le sequenze sotto sono illustrazioni manuali delle condizioni lette, non fixture accettate dal motore.

## 1. Che cosa sostiene A alla prima conferma
La catena esistente è qualificazione Q_A → nascita dell’impulso nel contesto ammesso → reazione qualificata e anchor pubblicato → barra completa 1m successiva all’ARM, con chiusura nel verso della ripresa oltre K secondo i tick previsti e senza contatto V certificato. Readiness e precedenze dei contatti restano necessarie. R/K/V sono congelati alla conferma; B è la destinazione narrativa, non il target economico della call.

Questa è una conferma locale della ripresa, non la prova che il pullback sia finito né una probabilità di raggiungere B. `_confirm` salva istante, chiusura, scala e barra della conferma; da lì A ha un orizzonte di 4 ore e un controllo di progresso a 2 ore. La selezione/possibilità di ingresso non aggiunge una ragione strutturale e può fallire lasciando lo scenario confermato.

## 2. Che cosa viene rivalutato
| Oggetto | Osservazione/regola effettiva | Conseguenza per la lettura |
|---|---|---|
| Protezione locale congelata | Contatto V su intervallo certificabile; collisione B/V ambigua | INVALIDATED oppure UNASSESSABLE; non semplice indebolimento |
| Premessa d’impulso | Nuova chiusura completa 15m oltre A, strettamente, dopo conferma | PRICE_PREMISE_FAILED; l’assenza di questa chiusura è sopravvivenza, non prova favorevole nuova |
| Destinazione | Contatto certificato B | DESTINATION_REACHED; conclusione, non nuova conferma da conservare indefinitamente |
| Progresso | Massimo spostamento favorevole delle chiusure 1m interamente successive alla conferma, fino a metà orizzonte; confronto con 0,5 S15 della conferma | Sotto soglia: STALLED. Prima del controllo: verifica ancora aperta. Sopra soglia: requisito temporale soddisfatto una volta, non sostegno corrente permanente |
| Contesto 1h | Per A principale confermata, contesto corrente non concorde con la direzione | `counterevidence` in MarketView; nessun terminale automatico dello scenario |
| Fase 15m | Categoria aggiornata e direzione dell’espansione disponibili | Osservazione corrente; dopo conferma non esiste una regola che faccia di una sola fase contraria un terminale o un punteggio della tesi |
| Scenari opposti | ARMED/CONFIRMED in entrambe le direzioni | MarketView complessiva UNCERTAIN con alternative; non invalidazione automatica di A |
| Tempo | Scadenza conferma +4h | TIME_EXPIRED; distinto dal mancato progresso |
| Dati | Gap/staleness richiesti 1m/15m | UNASSESSABLE. Non bearish, non mancato progresso dedotto dal silenzio |
| Contesto indisponibile | Readiness 1h/15m insufficiente per MarketView | Lettura UNAVAILABLE. La disponibilità di contesto e quella del monitoraggio strutturale non sono identiche |
| Quotazione/servizio/ingresso | Restrizioni della call e del tentativo | Non trasformarle in controevidenza di prezzo; gestione separata |

Riferimenti: `core3._confirmations/_confirm/_scen_interval/_scen_intervals/_scen_progress/_premise_close/_scen_timers/_context_withdrawals/compute_view`; `core4._confirm/_scen_interval`. Al terminale dello scenario può seguire il ritiro della guidance collegata secondo il contratto: qui si descrive prima il motivo analitico, senza inventare una regola di gestione della posizione.

## 3. Quanto è già esplicito e quanto no
MarketView conserva `observed_context`, `phase`, `reasons`, `counterevidence`, scenari e alternative. Con una sola direzione forte rimane CONDITIONAL anche se il contesto diventa contrario: la direzione è quella dell’ipotesi sopravvissuta, accompagnata da controevidenza, non una nuova attestazione che il contesto la sostenga.

La controevidenza del contesto viene associata esplicitamente al principale A confermato. Non va affermato che ogni A alternativo possieda una valutazione completa autonoma di sostegno: `_scenario` non pubblica una sintesi equivalente per ogni alternativa.

Il progresso è accumulato internamente (`max_fav_t`, `progress_done`) e verificato una volta. Il record di scenario pubblica riferimento e orario del controllo; non pubblica un continuo stato analitico “sostegno confermato” né una transizione PASS al superamento. Qualsiasi esposizione futura di quella verifica dovrebbe distinguere informazione interna da campo già disponibile nell’API.

Il journal è selettivo: `_publish_observations` emette quando cambia la categoria; `_publish_view` confronta una chiave di stato, non ogni valore numerico o minuto trascorso. Il silenzio del journal non prova prezzo fermo, dati assenti o sostegno invariato.

**Unico collegamento non definito per una revisione ulteriore:** dopo che il requisito una tantum di progresso è stato soddisfatto, non è stabilito come nuove osservazioni debbano rinnovare o revocare il sostegno globale, prima di un terminale. Le fonti motivano osservare la risposta, ma non determinano quale regola impiegare. È un limite all’affermazione di sostegno corrente, non un difetto dimostrato né una capacità nuova autorizzabile con questi materiali. Non introduciamo decadimento, finestre mobili, persistenza del contesto o soglie nostre.

## 4. Sequenze manuali, senza esiti futuri
Esempi LONG in dominio orientato q: A=90, B=120, V=99, conferma q=104 a t0, scala della conferma S15=10; controllo a t0+2h, orizzonte t0+4h. Si suppongono dati completi e contatti non ambigui. Questi numeri illustrano soltanto le regole esistenti; non provano nascita/ARM del percorso.

| Sequenza osservata fino all’istante descritto | Distinzione |
|---|---|
| Dopo conferma, chiusure 106 → 102 → 108; tutti i minimi >99, contesto concorde | Arretramento compatibile col mantenimento: ripresa locale già osservata, tesi ancora aperta; non terminale soltanto perché una barra scende. Progresso massimo 4, verifica a metà orizzonte ancora pendente |
| Minimi >99 e chiusure sopra A, ma contesto 1h diventa BALANCED | Tesi strutturale aperta con una ragione iniziale non più presente: dichiarare controevidenza. Non dedurre inversione o uscita; non dire “tutto ancora confermato” |
| A t0+2h la massima chiusura osservata è 108 | Premessa non invalidata ma progresso richiesto insufficiente: STALLED. È già una decisione analitica distinta dall’invalidazione |
| Massima chiusura 110 prima di +2h, poi ritorno a 105 con minimi >99 | Requisito temporale superato, tesi aperta. Il massimo storico non dimostra sostegno rinnovato a 105. Senza nuova regola non assegnare “forte/debole” |
| Un minuto richiesto manca mentre gli ultimi prezzi noti restano sopra99 | Non valutabile dal buco; non classificare come stagnazione o cedimento |
| Minimo certificato 98,8 con B non toccato nello stesso intervallo | INVALIDATED per V. Non attendere una chiusura 15m sotto A e non confondere V locale con premessa d’impulso |

SHORT usa la trasformazione q=−prezzo e lo scambio degli estremi; le relazioni e i significati restano identici. Nessun caso è stato scelto da esiti Owner.

## 5. Conseguenza e chiusura
La spiegazione può già distinguere: conferma storica; validità residua; contesto corrente con eventuale controevidenza; controllo di progresso ancora pendente oppure terminale registrato; disponibilità dei dati. Nessuna di queste dimensioni è un ordine di entrare/uscire.

Non proponiamo un nuovo stato aggregato: le fonti non consentono di decidere un effetto ulteriore del contesto/fase o la freschezza della prova di progresso. Per modificare A servirebbe evidenza ulteriore, inclusi gli studi pianificati. Il design termina con la capacità esistente chiarita e il limite della sua interpretazione; nessuna variante, implementazione o prova è attivata.

v0.6 e HDP-001 congelati; studi INACTIVE. Review del Director documentale completata; decisione finale dell’orchestratore pendente.
