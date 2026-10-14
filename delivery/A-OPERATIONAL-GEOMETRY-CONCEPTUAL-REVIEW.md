# A — coerenza concettuale della geometria operativa

14 ottobre 2026. Verifica concettuale autorizzata; nessuna nuova elaborazione storica, implementazione o prova economica. Riferimento letto: `7e48f7e`.

## Raccomandazione conclusiva

**Non emerge un conflitto concettuale che motivi una modifica. Chiudere il controllo e conservare la geometria corrente, con efficacia e adeguatezza congiunta non dimostrate.** I livelli non descrivono tutti la medesima estensione: articolano aspettativa, ostacolo operativo, protezione e prezzo accettabile. Possono comporsi coerentemente come condizioni congiunte, senza garantire un ingresso dopo ogni conferma. La diagnosi documenta restrittività ricorrente, non dimostra una contraddizione né identifica quale vincolo sostituire.

## Origine e funzione

| Oggetto | Origine corrente | Funzione e attribuzione |
|---|---|---|
| B | Estremo favorevole delle sorgenti dell'impulso A, congelato alla nascita; monitorato dal primo ARM | Destinazione narrativa del recupero. Il ritorno verso l'estremo è un adattamento del processo professionale di continuazione, non una destinazione numerica fornita da Grimes. |
| Target operativo T | Alla conferma: bordo vicino della prima zona opposta ammissibile davanti al prezzo; prezzo dentro una zona impedisce la proposta. In WAIT il cap può solo restringersi secondo le regole esistenti. | Uscita conservativa riferita a un ostacolo, distinta da B. Può essere più vicina della destinazione narrativa: non autorizza a trattare successo della call e raggiungimento di B come lo stesso evento. La selezione delle zone e il bordo sono convenzioni del progetto. |
| V | Estremo contrario R della reazione meno la fascia z nel dominio direzionale, arrotondato operativamente secondo la precisione esistente; congelato alla conferma | Invalidazione locale dell'ancora e protezione operativa, distinta dalla premessa più ampia dell'impulso. Il principio di invalidazione delimitata ha sostegno professionale; livello esatto, fascia e trattamento sono nostri. |
| Corridoio RETURN | Dominio direzionale: da max(R arrotondato, V operativo + tick) a min(K arrotondato, T − tick); congelato alla conferma, ulteriormente limitabile dal cap | Vincolo sul prezzo di esecuzione entro la reazione già riconosciuta. Non è un target, uno stop o un secondo pattern. La scelta R–K è nostra; non ogni prezzo del corridoio è economicamente ammissibile. |
| Regione economica | Intersezione del corridoio con spazio netto positivo e rapporto reward/risk minimo, usando T/cap e V operativi e l'envelope di costo | Condizione di convenienza geometrica secondo la politica, non evidenza di continuazione. Costo storico e rapporto minimo sono convenzioni, non regole dimostrate dalla fonte. |
| Riferimento locale RETURN | Prima barra 1m utilizzabile, poi recupero del suo estremo favorevole senza violazione contraria | Evidenza aggiuntiva locale. Non modifica V né allarga corridoio/target; la sua utilità rimane non validata, come nel confronto RETURN chiuso. |

Sorgenti statiche: `core3.py` (_target3, _real_levels, _corridor, _route_a, _return_gates), `core4.py` (nascita/anchor congelato), `geometry.py`; specifica MP-004 §4 e §6. Le versioni successive ereditano questi livelli nel perimetro già documentato. RP-001A è una fonte storica di attribuzione, non la specifica numerica corrente: dichiara esplicitamente che le fonti non forniscono target rule, entry band o soglie BTC. Il testo originale professionale non è stato riletto in questo step.

## Coerenza e scala

La catena richiesta è: recupero condizionale dell'impulso → ingresso limitato al corridoio → possibile percorso verso un ostacolo operativo → protezione all'ancora locale. Una parte del movimento narrativo può essere sufficiente per il target operativo. La presenza di un ostacolo più vicino riduce il guadagno utilizzabile senza confutare automaticamente la destinazione B.

I diversi orologi (struttura 15m, risposta 1m, contesto 1h) non costituiscono da soli una contraddizione: descrivono ruoli diversi nel medesimo scenario. Non dimostrano però che una singola risposta 1m sia adeguata rispetto al rischio fino a V o al movimento fino a T. Questa è un'incertezza sulla motivazione/efficacia della composizione, non una prova che le regole richiedano due movimenti incompatibili.

Il rischio economico è calcolato fino a V, non fino al minimo della barra RETURN; il rendimento è calcolato fino al target operativo/cap, non sostituito con B per far superare il gate. Pertanto una ripresa locale può essere reale ma insufficiente per emettere: evidenza favorevole ed eseguibilità restano predicate distinte.

## Esempi manuali discriminanti

Esempi schematici di geometria, non tape ammessi dal motore né casi storici. LONG; SHORT si ottiene riflettendo l'asse dei prezzi e gli estremi. Nessun nuovo valore proposto per le regole.

1. **Composizione coerente.** B=120, T=110, V=98, R=100, K=105: il corridoio è [100,105], salvo precisione. Un riferimento con minimo 101, massimo 102 e chiusura interna prepara una risposta che può recuperare 102+tick ancora entro il corridoio. L'ingresso rimane condizionato all'economia e ai gate correnti. T prima di B significa uscita conservativa, non aspettativa opposta.
2. **Restrizione economica.** Medesima destinazione narrativa, ma una zona opposta porta T vicino al corridoio. Il residuo fino a T può non remunerare rischio fino a V e costi. L'astensione è coerente: B lontana non consente di ignorare l'ostacolo operativo. Non occorre attendere un esito per riconoscere questa distinzione.
3. **Regione RETURN possibile, risposta non emettibile.** Con il corridoio dell'esempio 1, una barra può chiudere a 103 ma avere massimo 109. Se tutti gli altri gate rendessero quel ritorno utilizzabile, la risposta richiederebbe almeno 109+tick, fuori da [100,105]. Il contratto rifiuta questo riferimento; non promette che ogni barra utilizzabile abbia una risposta emettibile. È un'incompatibilità di quel riferimento, non una contraddizione universale: l'esempio 1 conserva una possibilità.

Questi esempi separano possibilità logica e adeguatezza empirica. Non cercano una geometria che faccia entrare nei 12 casi e non dimostrano frequenza o utilità.

## Decisione e limiti

Mantenere l'insieme come candidata restrittiva. Non emerge una singola decisione metodologica sostitutiva sufficientemente motivata da sottoporre ad approvazione. Non accreditare la coerenza come validazione: rimane aperto se la composizione renda opportunità utili, e le diagnosi già disponibili mostrano che spesso non ne rende emettibili.

La conclusione non riapre RETURN, E o a2x e non attiva ulteriori diagnosi. v0.6 e gli studi congelati invariati. Review del Director: lettura statica dei riferimenti indicati e confronto concettuale; nessuna riesecuzione, nuovo conteggio, consultazione prezzi, accesso Owner o verifica CI.
