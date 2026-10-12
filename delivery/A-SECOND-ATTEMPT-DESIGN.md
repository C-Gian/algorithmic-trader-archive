# A — secondo tentativo sullo stesso impulso: design sperimentale
12 ottobre 2026. Base letta: `137b8af`. Proposta del Director, separata da v0.6. Nessuna implementazione, esecuzione, estrazione o valutazione sui dati. Decisione dell’orchestratore pendente.

## Decisione proposta
La seconda opportunità è definibile coerentemente **come successore distinto**, dopo INVALIDATED/V_CONTACT del primo scenario confermato, entro la scadenza originale dell’impulso. Non è la prosecuzione della vecchia conferma. La nuova evidenza è una reazione completa interamente successiva al fallimento, seguita da una chiusura di recupero successiva alla pubblicazione del nuovo anchor.

Una scelta nuova indispensabile è mantenere riservata la scoperta A nella stessa direzione durante questo riesame. Una seconda scelta è limitare anche la vita confermata del successore alla scadenza originale: riusare automaticamente conferma+4h allungherebbe la vita dell’impulso. Entrambe sono dichiarate sotto; nessuna deroga alla selezione o protezione delle call.

## 1. Fondamento e limite
La coppia 137b8af dimostra il discrimine v0.6, non che mantenerne l’impulso sia migliore. Grimes EXT-001, nelle citazioni già raccolte, descrive tentativi di ripresa falliti e pullback complessi; non fornisce profondità, durata o limiti del successore. Il design è un adattamento nostro, non una procedura di Grimes.

Regole consultate: `core3._scen_interval/_scen_end/_release_owner/_a_births/_confirm/_context_withdrawals/_select3`, `core4._a_close/_publish_anchor/_anchor_lost`, MP-002 e MP-003. Le regole RETURN v0.5/v0.6 sono riutilizzate senza modifica all’interno dell’eventuale nuovo figlio.

## 2. Impulso, tentativi e budget
- Identità immutabile dell’impulso: I0, direzione, sorgenti, Aq/Bq, S15_nascita, z, nascita tB, scadenza H0=tB+2h.
- Primo scenario S1, suo figlio e call mantengono tutti gli ID, record e terminali v0.6.
- Al primo e unico fallimento locale ammissibile si registra una possibilità di riesame collegata a I0. Non è ARMED, CONFIRMED o un ingresso.
- Successore S2 con ID distinto e parent S1/I0 nasce soltanto alla pubblicazione del primo nuovo anchor qualificato. Non si pubblica una falsa nuova nascita Q_A.
- Budget massimo: due tentativi confermabili per I0, S1 e S2. La possibilità S2 è consumata al suo ARM, anche se non conferma o il suo figlio viene respinto. Non c’è S3.
- Revisioni/riarmi dell’anchor di S2 prima della sua conferma seguono le regole locali esistenti, senza nuovi ID di tentativo né ripristino del budget. Dopo conferma S2 l’anchor è congelato; V_CONTACT termina definitivamente S2/I0.

## 3. Apertura del riesame e precedenze
A un dispatch tf, dopo aver elaborato normalmente protezioni, contatti e terminali di S1:
1. Ammissibile solo terminale esatto INVALIDATED con causa V_CONTACT di un A CONFIRMED di primo tentativo. Nessun riesame per STALLED, TIME_EXPIRED, PRICE_PREMISE_FAILED, DESTINATION_REACHED, UNASSESSABLE o terminali del solo figlio.
2. Occorre tf<H0 e che I0 possieda ancora l’owner attivo prima del fallimento. Se l’owner era già rilasciato per scadenza originale, non è riacquisito.
3. Nessun B già raggiunto, gap/staleness richiesti, o cedimento noto della premessa. B/V nello stesso intervallo resta UNASSESSABLE, mai opportunità di riesame.
4. La premessa usata per riesaminare è quella **pre-conferma**: chiusura completa 15m q<=Aq+z, non la diversa soglia post-conferma q<Aq. È una scelta dichiarata: una nuova reazione deve nuovamente soddisfare il dominio originario.
5. Contesto concorde e assenza di espansione avversa, con readiness ordinaria, devono essere disponibili al dispatch di apertura. Se non lo sono, non si crea una riserva da recuperare più tardi.

Se V_CONTACT e chiusura 15m q<=Aq+z giungono nello stesso dispatch, S1 conserva il terminale determinato dalle precedenze esistenti, ma il successore è escluso. Il test della premessa per S2 non riscrive S1.

La riserva del riesame **sostituisce prospetticamente** il rilascio dell’owner che v0.6 farebbe per V_CONTACT. S1 rimane terminale; l’occupazione appartiene a I0 e al riesame, non a S1. Nessun falso Q_A o reset del latch viene simulato.

## 4. Fatti nuovi, origine e prima disponibilità
tf è l’istante effettivo di pubblicazione del fallimento, non l’istante ipotetico del minimo dentro la barra.

Origine della nuova formazione: O=prima frontiera 15m >=tf. Sono ammesse soltanto barre complete trade 15m con start>=O, rese disponibili a un dispatch successivo a tf. La barra contenente il contatto, anche se chiude dopo tf, è esclusa dalla nuova reazione. Se tf coincide esattamente con una frontiera, la barra che inizia lì è interamente successiva ed è ammissibile.

Conseguenze:
- nessun vecchio minimo, massimo, lower_close, barra di recupero o CONFIRM è riutilizzato come fatto nuovo;
- A/B e contesto storico restano riferimenti dell’impulso, non nuova conferma;
- mentre si attende la prima barra interamente nuova, contatti B, copertura e premessa continuano a essere sorvegliati;
- il contatto V non arma S2.

Su barre interamente nuove:
- R2 è il minimo trasformato cumulativo, anchor la barra più recente che realizza quel minimo (inclusi i pareggi, convenzione esistente);
- è richiesta almeno una chiusura contraria: per la prima nuova barra, c<o; per le successive, c<chiusura della precedente nuova barra. Prima barra o precedente chiusura nuova sono il riferimento causale; il lower_close di S1 non è ereditato;
- R2<R1 congelato del tentativo fallito, R2<Bq−0,25·S15_nascita e R2>Aq+z;
- contesto/readiness e gate di espansione sono quelli ordinari A, applicati ora.

Questa scelta è più restrittiva del riarmo v0.4: richiede una barra **interamente** post-fallimento. Può perdere opportunità rapide. Non si recuperano retroattivamente per far funzionare la coppia 137b8af.

Al primo rispetto di queste condizioni, prima di H0, S2 nasce ARMED con K2=high_q della nuova barra anchor e V2=R2−z. La prima disponibilità è il dispatch che pubblica l’ARM, con cursor e sorgenti espliciti. Nessuna conferma nello stesso dispatch dell’ARM.

## 5. Nuova conferma, geometria e clocks
Aq/Bq/S15_nascita/z e H0 non cambiano. R2/K2/V2 possono essere rivisti prospetticamente prima della conferma secondo MP-003, senza alterare S1. La destinazione rimane Bq.

La conferma C2 richiede una barra completa 1m con start>=pubblicazione dell’anchor attivo, ammessa a un cursor successivo, close_q>=K2+tick e nessun contatto V2 o B certificato/ambiguo secondo le precedenze esistenti. Nessun prezzo di recupero precedente è “riscoperto”.

**Clocks nuovi indispensabili:**
- S2 pre-conferma e confermato termina entro H0, senza conferma+4h;
- al momento di C2 deve restare almeno il minimo residuo d’ingresso ordinario A (30 minuti). Altrimenti S2 termina senza opportunità confermata; non prorogare H0;
- controllo di progresso dello scenario a C2+(H0−C2)/2, riferimento close_C2 e S15_C2; soglia esistente 0,5 della scala;
- hard deadline della nuova call=H0; controllo call a issue2+(H0−issue2)/2, con riferimenti della call; min_residual e altri gate ordinari ancora applicati all’emissione;
- orizzonti descrittivi sono limitati al residuo reale, mai quattro ore garantite.

Sono modifiche sperimentali esplicite ai clocks, necessarie a rispettare il divieto di prolungare I0; non si presentano come riuso identico di v0.6.

## 6. Chiusura del riesame/successore
Precedenza: protezioni e conclusione S1 restano immutate; per il nuovo riesame prima expiry/carenza dati, poi contatti B e ambiguità, poi chiusura premessa e gate correnti, infine formazione/ARM/CONFIRM/selezione.

Prima di conferma S2, chiudono definitivamente la possibilità:
- H0 raggiunto (anche uguaglianza: timer precede ARM/CONFIRM);
- B raggiunto prima della nuova conferma;
- chiusura 15m q<=Aq+z;
- gap/staleness 1m/15m richiesti o contesto non disponibile;
- gate di contesto/espansione contrari secondo le regole pre-conferma;
- chiusura di S2 secondo il suo ciclo locale, senza S3.

R2<=Aq+z rende la reazione non armabile. Poiché R2 è cumulativo, una barra successiva non cancella l’escursione: nessuna selezione opportunistica di un anchor più alto. Il riesame termina comunque ai gate/clock previsti.

Dopo C2 valgono contatti V2/B, premessa confermata, progresso, disponibilità e H0. Il contesto è nuovamente controevidenza e non un automatico stop, come per un A confermato; nessuna regola nuova di “tesi indebolita”.

## 7. Convivenza col sistema ordinario
- Durante riserva e S2 fino a H0/terminale, nessuna nuova nascita A ordinaria **nella stessa direzione** può usare lo slot discovery di I0. È un cambiamento deliberato rispetto a v0.6: evita che ordinario e successore rivendichino contemporaneamente il movimento. Non pretende che ogni Q_A vero descriva lo stesso impulso.
- Al rilascio, riparte il latch ordinario NEED_FALSE → falso osservato a/dopo rilascio → vero. Nessun falso retroattivo. Opposta direzione, B e C seguono i propri gate, ownership e conflitti.
- Si conserva la capacità massima ordinaria di scenari; la riserva deve essere contata esplicitamente, non storage invisibile illimitato.
- C2 passa attraverso la stessa selezione, slot, priorità e routing IMMEDIATE/RETURN, senza privilegio. Un rifiuto consuma il figlio; non crea un terzo tentativo.
- Call S1 non si riapre, non cambia V/T/H e non viene sostituita retroattivamente.
- Nessuna ipotesi sulla posizione reale: il prodotto non la conosce. Il terminale di guidance non certifica un’uscita eseguita. L’eventuale call S2 è un’indicazione distinta soggetta ai gate ordinari, non ordine di rientro o compensazione.

## 8. Sequenze manuali
Dominio q. LONG: A=97000, B=100900, S15_nascita=2000, z=200, R1=99900, V1=99700; nascita03:30, H0=05:30. S1 confermato04:01, V1 contattato e invalidato04:02. Si suppongono contesto concorde, dati completi e assenza di call precedente. Sono sequenze di design, non test del motore.

1. **Ammissibile.** O=04:15. La barra [04:15,04:30) apre99800, high100050, low99650, close99750: nuova chiusura contraria, R2 sottoR1 e sopra97200. Alle04:30 ARM S2, K2=100050,V2=99450. Una successiva barra [04:30,04:31) chiude100050,1, low99750, high100060: C2 distinto; restano59min. Nessuna call garantita. Progresso C2 alle05:00:30, H0sempre05:30.

   SHORT speculare p=200000−q: A_p=103000,B_p=99100,R1_p=100100,V1_p=100300. Nuova barra open100200, high100350, low99950, close100250. K2_p=99950,V2_p=100550; recupero close99949,9. ConfermaSHORT e stessi clocks.

2. **Fallimento senza fatti nuovi.** Dopo04:02 solo prezzi dentro il vecchio corridoio; barra contenente il contatto esclusa. Le nuove barre non hanno chiusura contraria oppure nessun minimo nuovo sottoR1. Vecchio K superato non conferma nulla. NessunS2; si attende una reazione qualificata entroH0. InSHORT si invertono le disuguaglianze, senza nuova logica.

3. **Premessa ceduta.** Prima diARM, una nuova chiusura15m q=97200 o inferiore. Riserva conclusa, nessunS2, anche se il prezzo recupera dopo. SHORT: close_p>=102800. Se il cedimento era nel dispatch04:02, la riserva non nasce.

4. **Scadenza prima della conferma.** ARM S2 alle05:15; nessuna nuova conferma entroH0. Un recupero disponibile alle05:30 viene dopo la precedenza del timer: EXPIRED, nonC2. Inoltre una conferma alle05:10 non ha30minresidui e non crea un’opportunità confermata: esplicita esclusione, non proroga. SHORTidentico.

5. **Disponibilità persa.** Gap dopo04:02 e prima della nuova formazione: riesameUNASSESSABLE. Il riempimento storico successivo non lo riapre. Distinto dalla mancanza di una reazione.

## 9. Scelte aggiuntive e conflitti dichiarati
| Scelta | Natura / conseguenza |
|---|---|
| UnsoloS2, soloV_CONTACT | Contenimento autorizzato, non regola professionale dimostrata |
| Origine su prima frontiera15m dopo pubblicazione | Adaptation causale conservativa; la coppiaoriginaria non garantisceS2 |
| lower_close solo su dati nuovi, prima barra c<o | Nuova convenzione esplicita, non riuso del flagstorico |
| Premessa pre-conferma Aq+z, geometria cumulativa nuova | Riapplicazione del dominio d’ammissibilità del tentativo, più restrittivo della premessa confermata |
| Riserva discovery e latch alrilascio | Modifica reale del rinnovoA; può ritardare un nuovoimpulsoordinario nella stessa direzione |
| Tutti i clocksS2 entroH0 e30minresidui aC2 | Conflitto risoltoesplicitamente con conferma+4h di v0.6; nessun allungamento |
| Routing/slot invariati, nuovaidentità | Nessuna promessa di call; nessuna riapertura del vecchio child |

**Verdetto:** proposta definibile, ma non ottenibile cambiando soltanto il terminale V. Richiede owner dell’impulso distinto dal tentativo, nuovi legami d’identità e clocks espliciti. Queste sono le decisioni metodologiche da approvare prima di implementare. Se non sono accettate, il design non va “semplificato” prorogando l’impulso o riaprendo S1.

Nessun beneficio, frequenza o risultato economico stimato. v0.6 e studi congelati invariati e INACTIVE.
