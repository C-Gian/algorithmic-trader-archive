# Market reading of the use session: where the explanation gap lies

**Executor localization (2026-10-12, base `ab8d080`).** No product change. The only data are the records already examined in the [diagnosis](MARKET-READING-DIAGNOSIS.md): journal `market_view` records 760, 772, 776 and 781, and the session's saved view ([`reconstruction/`](reconstruction/)). To read what the reason texts assert, I also read the code that writes them (`compute_view`, `src/algotrader/adviser/core3.py:1692–1749`, inherited by `adviser.core.v6`) and the frozen MP-002 §4 table. No acquisition, session or economic evaluation was run. v0.6 and HDP-001 are frozen; the studies are INACTIVE.

Gian's feedback: he understands that *Incerta* gives no clear direction. He wants to know what the system observed, why the direction stays uncertain, and what is missing before a possible entry, with a simple presentation and the layout unchanged.

## 1. Incerta and Equilibrio, point by point

| | **Incerta** (760: 11:22–12:00 Rome; 781: 13:30–13:45) | **Equilibrio** (772: 12:00–12:30; 776: 12:30–13:30) |
|---|---|---|
| **1. Observations available** | `observed_context` BALANCED. `phase` EXPANSION (760) / TRANSITION (781). `levels`: support near-edge 83469.545 / 83293.785, resistance 84259.275 / 83568.935, last close 83640.7 / 83412.0. For 781 only, the saved-view lenses: momentum BALANCED since 00:00 UTC; volatility TRANSITION; events coverage UNKNOWN | `observed_context` BALANCED. `phase` ROTATION (772) / COMPRESSION (776). `levels`: support 83233.995 / 83293.785, resistance 84259.275, last close 83521.7 / 83468.7. Lenses at those instants: not attested (only the final saved view has lenses) |
| **2. Recorded reason** linking observations to the reading | `reasons`: "observed BALANCED/EXPANSION" (TRANSITION in 781) "; missing antecedent: no born A impulse or compression box scenario". `table_row` NO_QUALIFIED_STRUCTURE, `expected_direction` UNCERTAIN | `reasons`: "balanced 1h context in rotation" (compression in 776) "; no qualified box". `table_row` BALANCED_RANGE, `expected_direction` BALANCED |
| **3. Recorded entry condition** | **None.** `principal` null, `watch` [], `scenarios` [], `attempts` [], `box` null, `call` null: no scenario, so there is no trigger level, entry area or confirmation to wait for | **None**, same fields and values |
| **4. Recorded condition that would change the reading** | **None.** `alternatives`, `counterevidence`, `watch` and `blockers` are empty; `horizon_minutes` is null. The reason names what is missing *now* (an A-impulse or compression-box scenario); it does not state when one would be born | **None**, same fields. "no qualified box" says only that no box exists, so no numeric boundary is defined (MP-002 §4: "otherwise no invented numeric boundary") |

**Method rule, not in the record.** With BALANCED context and no scenario, the phase alone separates the two states (MP-002 §4; `core3.py:1730–1736`): COMPRESSION or ROTATION gives Equilibrio, any other phase gives Incerta. The rule is frozen and the values agree with it, but no field states it as a condition for a change. The same applies to the lens role texts in the saved view ("A needs UP for LONG … C needs BALANCED", "COMPRESSION gates box birth"): these are general role descriptions, not conditions recorded for this state.

## 2. Proposed short Italian wording (supported content only)

Each line shows its source field and value. Nothing turns *Incerta* into an expected sideways range, and the absence of a call is never shown as an absence of reading.

**Incerta** (values of record 781; 760 differs only in phase and levels):

| Proposed line | Source field = value |
|---|---|
| Lettura: direzione **incerta**. Il sistema ha una lettura, ma non indica una direzione. | `expected_direction` = UNCERTAIN |
| Osservato: contesto a 1 ora in equilibrio; fase di transizione. | `observed_context` = BALANCED; `phase` = TRANSITION (760: ESPANSIONE) |
| Perché incerta: nessuna struttura qualificata. Non è nato né uno scenario di impulso (famiglia A) né uno di box di compressione. | `table_row` = NO_QUALIFIED_STRUCTURE; `reasons[0]` = "…missing antecedent: no born A impulse or compression box scenario" |
| Ingresso: nessuno scenario attivo, quindi nessuna condizione d'ingresso definita. | `principal` = null; `watch` = []; `scenarios` = []; `call` = null |
| Che cosa cambierebbe la lettura: non indicato dal sistema. | `alternatives` = `counterevidence` = `watch` = []; `horizon_minutes` = null |

**Equilibrio** (values of record 776; 772 differs only in phase and levels):

| Proposed line | Source field = value |
|---|---|
| Lettura: direzione attesa **equilibrio**, senza un orizzonte indicato. | `expected_direction` = BALANCED; `horizon_minutes` = null |
| Osservato: contesto a 1 ora in equilibrio; fase di compressione. | `observed_context` = BALANCED; `phase` = COMPRESSION (772: ROTAZIONE) |
| Perché: contesto equilibrato in compressione. Nessun box qualificato, quindi nessun limite di prezzo definito. | `table_row` = BALANCED_RANGE; `reasons[0]` = "balanced 1h context in compression; no qualified box" |
| Ingresso: nessuno scenario attivo, quindi nessuna condizione d'ingresso definita. | as for Incerta |
| Che cosa cambierebbe la lettura: non indicato dal sistema. | as for Incerta |

Not proposed, because they lack support in the record:
- a future trigger or an "attendere X" line;
- a probability or duration;
- "lateralità" for Incerta;
- for Equilibrio, the method rule "it becomes Incerta if the phase leaves compression or rotation".

## 3. Outcome

| Gian's question | Outcome |
|---|---|
| What the system observed | **Information present, correctable in the explanation.** `observed_context` and `phase` are in every record; today they appear only as raw codes outside the box |
| Why the direction stays uncertain (or is Equilibrio) | **Information present, correctable in the explanation.** `table_row` plus `reasons` give the recorded link. Today the reason is English system text in the collapsed *Approfondimenti*, with internal terms |
| Whether an entry condition exists | **Information present (as an absence), correctable.** No scenario, so no entry condition: this can be said plainly without inventing a trigger |
| What is missing before a possible entry / what would change the reading | **Missing informational link, to submit to Astra.** The record names only the missing antecedent (Incerta) or the missing box (Equilibrio). No field records the condition under which a scenario would be born or the reading would change: `watch`, `alternatives` and `counterevidence` are empty. The method knows the rule (MP-002 §4, scenario-birth rules), but the MarketView does not emit it. Deriving it in the frontend would be inventing it there |

**Question for Astra (not activated by the executor).** For the no-scenario states (NO_QUALIFIED_STRUCTURE, BALANCED_RANGE without a box), FOUNDATION §4 asks the view to expose "what would change it". Should the MarketView carry an explicit, causally recorded statement of what is missing and what would change the reading, for example the antecedent conditions of families A, B and C or the phase rule? From which rule sources, and under which method/contract version, given that v0.6 is frozen?

**Possible without Astra** (after Gian's go-ahead, within the box, layout unchanged): the Italian lines of §2. They use only recorded fields.
