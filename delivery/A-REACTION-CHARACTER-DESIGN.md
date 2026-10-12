# Carattere della reazione A — design analitico separato

12 ottobre 2026. Decisione proposta al Research Architect: **autorizzabile un esperimento isolato di osservazione della candidata sotto definita; nessun filtro e nessuna v0.7.** La distinzione professionale è traducibile in una descrizione causale del percorso, non ancora in un ordinamento affidabile di qualità.

## 1. Fondamento e confronto con A

Materiali letti: `research/first_trader/RP-001A-PROCESS-TRANSLATION.md` §§fonti, A2–A7 e `knowledge/external_registry.yaml`, EXT-001/002; codice alla revisione 8762621, `core3.py` `_new_a`, `_a_births`, `_confirmations`, `core4.py` `_a_close` e catena di ereditarietà `core5.py`/`core6.py`; classificazioni di contesto/fase in `core.py`. Documenti storici RP-001 riutilizzati come ragionamento professionale, non come attuale autorizzazione o regole del prodotto.

Grimes, come documentato nei materiali già raccolti, invita a leggere sviluppo, ampiezza e rapidità della risposta; considera anche pullback complessi con tentativi di ripresa falliti. Non fornisce soglie o una regola secondo cui lentezza, sovrapposizione o irregolarità siano sempre favorevoli. “One step ahead” riguarda la risposta a un movimento in un esempio concreto: non è una formula universale della qualità dell’arretramento. Nessuna nuova rassegna, fonte o estrazione di percorsi reali.

| Aspetto | A v0.6 già dispone di | Relazione mancante o ridondanza |
|---|---|---|
| Distanza | Origine A e destinazione B dalla finestra sorgente; scala congelata, zona, estremo R, limiti strutturali e anchor | Un’altra soglia di profondità duplichererebbe principalmente l’ammissibilità geometrica. |
| Durata | `born_at`, `bars_seen`, scadenze, tempi ARM/REVISE/REARM | L’età è ricavabile; il numero di barre 15m non descrive come il percorso si distribuisce nel tempo. |
| Rapidità | Prezzi e tempi disponibili; rapidità media ricavabile da distanza/durata | Non è un’informazione indipendente se si fissano distanza e durata. Manca la distribuzione del progresso contrario durante l’episodio. |
| Efficienza | Efficienza su finestre 1h/15m per contesto e fase | Non è necessariamente l’efficienza della reazione corrente: finestra e origine diverse. |
| Alternanza | Un flag `lower_close`; nuovi estremi e revisioni di anchor | Il flag registra che una chiusura contraria è avvenuta, non ampiezza e ordine dei recuperi falliti; la storia dell’anchor registra estremi, non tutto il percorso delle chiusure. |

La vecchia proposta RP-001 comprendeva un rapporto di velocità con soglie proprie su 5m: **non è una misura corrente ereditata da A v0.6 e non viene ripristinata**. Il codice attuale arma A con reazione minima, chiusura contraria, protezione dell’origine e contesto; v0.4 aggiunge perdita/revisione prospettica dell’anchor. v0.5/v0.6 riguardano la risposta locale all’ingresso RETURN, successiva alla conferma dello scenario: non risolvono il carattere dell’arretramento precedente.

## 2. Unica candidata: profilo di sviluppo della reazione

**Una traiettoria normalizzata, senza punteggio composito PASS/FAIL.** Per uno scenario A già nato, orientare il prezzo nel verso dell’impulso (`q = d × prezzo`, d=+1 LONG, −1 SHORT), congelare i suoi A/B e I=B−A>0. Il riferimento è la nascita osservabile dello scenario, non il timestamp storico di un massimo riconosciuto più tardi.

Su ciascuna nuova barra completa trade 1m, pubblicabile soltanto a `known_at`:

- ascissa: minuti di mercato trascorsi dalla nascita dello scenario;
- ordinata: `x_j = (B − q_close,j)/I`, progresso contrario netto rispetto a B;
- estremo avverso e profondità R già esistenti restano metadati geometrici, non una seconda candidata di qualità.

Il punto iniziale è la chiusura della barra sorgente dello scenario, osservabile alla nascita. La curva usa esclusivamente barre con inizio non precedente a quel confine: una barra che lo attraversa non viene usata come nuova osservazione della reazione. Si conserva anche l’offset iniziale B−close: non si finge che l’episodio sia partito esattamente da B.

Dal **medesimo profilo**, come riassunto interpretabile per il confronto futuro, ricavare l’efficienza contraria firmata:

`E_t = (q_0 − q_n) / Σ|q_j − q_(j−1)|`.

È compresa fra −1 e +1: positiva quando prevale progresso contrario all’impulso; negativa quando prevale recupero. Non è una probabilità. In assenza di movimento il rapporto è INDEFINITO, non zero né “buona qualità”. La curva è la rappresentazione candidata; E è il suo riassunto, non un secondo segnale o voto.

**Aggiornamento:** appendere nuovi punti e ricalcolare sul solo prefisso disponibile; la storia pubblicata rimane immutabile. Stop descrittivo alla prima conferma A o alla conclusione strutturale dell’episodio. Nessuna informazione dalla successiva ripresa entra nel giudizio precedente.

**Anchor:** un nuovo R o una sostituzione locale dell’anchor viene annotato sulla curva, senza azzerarla: resettare a ogni nuovo minimo eliminerebbe proprio i recuperi falliti da descrivere. A/B restano quelli dello scenario. Un nuovo scenario crea un nuovo profilo; una correzione dei dati non riscrive silenziosamente giudizi precedenti, ma richiede una versione esplicita.

**Insufficienza:** una singola variazione rende E matematicamente disponibile ma poco informativo (spesso ±1); mostrarlo come prefisso breve, non forte evidenza. Nessun riempimento di minuti mancanti; un buco rende il percorso incompleto e non confrontabile nel test principale. Quote, volumi, mark/index e stati futuri non contribuiscono alla candidata.

**Interpretazione consentita:** a geometria e tempo confrontabili, una discesa che progredisce coerentemente contro l’impulso è una risposta contraria più organizzata; una sequenza con sovrapposizioni descrive recuperi e arretramenti alternati. La rapidità iniziale si vede nella curva, anche quando la velocità media finale è uguale.

**Interpretazione eccessiva:** E alto = reversal certo; E basso = continuazione certa; irregolare = cattivo; veloce = invalidato; mancanza di movimento = accumulo. Un pullback complesso può essere sano, ma ripetuti recuperi falliti possono anche anticipare cedimento. Nessuna modifica automatica a MarketView, gate, trigger, call o dimensionamento è proposta.

Scelte nostre dichiarate: chiusure 1m, confine alla nascita A, normalizzazione sull’impulso congelato, assenza di reset alle revisioni. Grimes non prescrive queste formule. Restano aperti l’età minima interpretabile, il punto di osservazione dell’esperimento e la regola di comparabilità; non si cercano valori sugli esiti.

## 3. Pochi percorsi manuali

Numeri inventati. Impulso A=100, B=110, chiusura al confine 110; sei osservazioni equispaziate. Questi sono esempi aritmetici del profilo, **non fixture complete di A**: non attestano readiness o superamento di tutti i gate. Per i confronti si stipulano stessa durata, estremi di barra e limiti geometrici; la condizione di recupero pubblicata non è ancora soddisfatta al cutoff. La compatibilità OHLC/lifecycle dovrà essere verificata prima di un eventuale esperimento, senza alterare i gate.

| Percorso delle chiusure, dopo 110 | Netto contrario | Variazione totale | E | Lettura descrittiva |
|---|---:|---:|---:|---|
| 109,5; 109; 108; 107; 106,5; 106 | 4 | 4 | 1 | Progresso contrario continuo; indebolisce la semplice narrativa di pausa innocua, senza dimostrare reversal. |
| 109; 107; 109; 106,5; 108; 106 | 4 | 12 | 1/3 | Stessa distanza finale e durata, ma alternanza sostanziale; non basta a scegliere fra correzione complessa e recuperi inefficaci. |
| 106; 106; 106; 106; 106; 106 | 4 | 4 | 1 | Stesso E del primo ma caduta iniziale e successiva stasi: il solo riassunto perde informazione. La curva conserva questa differenza; non si aggiunge un secondo filtro. |

**Controesempio:** dopo il primo percorso il prezzo può recuperare e continuare verso B; dopo il secondo può rompere la premessa strutturale. Questo contraddice l’ordinamento deterministico E alto = fallimento / E basso = successo, non l’osservazione della loro diversa risposta. I futuri alternativi non entrano nel calcolo e non sono risultati economici.

## 4. Unico confronto futuro interpretabile

Domanda: **a parità ragionevole di contesto, geometria e durata, un maggiore progresso contrario organizzato prima della conferma si associa a una minore probabilità di ritorno alla destinazione B prima del cedimento della premessa?**

Una sola osservazione per episodio a un’età fissa prospettica dalla nascita A, da congelare prima degli esiti. Popolazione: episodi ancora aperti e non confermati a quell’età. E del prefisso è l’esposizione continua; risultato osservabile: contatto con B prima della violazione della premessa A+zona, entro la scadenza strutturale originale. Ordine intrabar non risolvibile → ambiguo, non successo scelto arbitrariamente; scadenza senza evento → censura/nessun esito, da trattare esplicitamente. Non è un trade, un profitto o il target economico.

Confronto associativo condizionato, con una sola relazione E→esito: rendere comparabili contesto e fase, dimensione dell’impulso rispetto alla scala congelata, profondità R/I, retracciamento della chiusura, distanze residue da B e dalla premessa, zona relativa, età/scadenza e stato dell’anchor. Senza questa comparabilità si rischia di misurare solo distanze diverse. Nessuna richiesta di indipendenza statistica fra descrittori dello stesso percorso.

Assunzioni e limiti: sufficiente sovrapposizione fra episodi comparabili; dipendenza fra episodi da rispettare; nessuna selezione dei nove stop/due target; esiti delle call non usati per scegliere l’età. Sopravvivenza fino al punto fisso limita l’estimando: non descrive episodi già confermati o terminati prima. Se E non varia dopo il controllo della geometria, o non distingue l’esito con incertezza accettabile, la candidata non dimostra valore aggiunto. Il confronto E non esaurisce tutta la curva: non si passa automaticamente ad altri riassunti dopo un fallimento.

Prima di eseguire restano da congelare età di osservazione, gestione di censura/ambiguità, comparabilità e requisito minimo di evidenza. Sono decisioni dell’esperimento, non nuova formalizzazione del concetto. Il design consente di decidere ora se autorizzare quella prova isolata; non autorizza l’esecuzione.

## 5. Chiusura della review

La candidata è causalmente calcolabile e distingue sviluppo a geometria simile. Non elimina l’ambiguità professionale, non produce un ranking certo e non è attribuita a Grimes. La domanda empirica è unica, prospettica e diversa dalla semplice ammissibilità geometrica. **Propongo un esperimento isolato osservativo su questo design, se autorizzato da Astra; nessun filtro prima dell’evidenza.**

Nessuna implementazione, estrazione Owner, acquisizione, backtest o apertura di periodi protetti. v0.6 e HDP-001 congelati; studi INACTIVE.
