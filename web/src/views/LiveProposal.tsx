import { useEffect, useState } from "react";
import { adviserApi, CallView, LiveView, MarketViewDoc, reasonText, ScenarioState, ScenarioView } from "../adviser";
import { fmtLocal, fmtPrice, fmtTime, humanize } from "../lib/format";
import { Icon } from "../ui/Icon";
import { Badge, cx, Tone } from "../ui/primitives";
import type { IconName } from "../ui/Icon";

// Live cockpit main panel: "Che cosa propone il sistema adesso?". It shows only the authoritative backend state of the
// committed live view: entry availability is call.entry_status (already masked by the API for a non-current session),
// thesis validity is call.thesis_status, a terminated call has left view.call for view.recent_calls. Nothing is inferred
// from direction, quotes or levels. Scenario levels are never called entry, operational target or stop.

const EXPECTED_IT: Record<string, string> = {
  UP: "Rialzo", DOWN: "Ribasso", BALANCED: "Equilibrio", UNCERTAIN: "Incerta", UNAVAILABLE: "Non disponibile",
};

const ROW_IT: Record<string, string> = {
  REQUIRED_CONTEXT_UNAVAILABLE: "Il contesto 15m/1h necessario non è ancora pronto",
  OPPOSING_SCENARIOS: "Gli scenari indicano direzioni opposte",
  ONGOING_CALL: "Segue la call in corso finché la sua premessa regge",
  ARMED_SCENARIO: "Condizionale: una call solo se avviene l'innesco",
  BALANCED_RANGE: "Equilibrio in fase di compressione o rotazione",
  NO_SUPPORTED_PLAN: "Nessun piano supportato nelle condizioni attuali",
  CONDITIONAL_SCENARIO: "Condizionale: uno scenario supportato in una direzione",
  WATCH_ONLY: "Solo ipotesi in osservazione: né previsione né call",
  NO_QUALIFIED_STRUCTURE: "Nessuna struttura qualificata nelle condizioni attuali",
};

const THESIS_IT: Record<string, string> = {
  ONGOING: "ancora valida", TARGET_REACHED: "conclusa — target raggiunto", INVALIDATED: "conclusa — invalidata",
  TIME_EXPIRED: "conclusa — scaduta", UNASSESSABLE: "conclusa — non valutabile", RETIRED: "conclusa — ritirata",
};

/** Plain Italian for recorded entry reason codes; an unknown code is shown as recorded, never reinterpreted. */
const REASON_IT: Record<string, string> = {
  TOO_LATE: "tempo residuo insufficiente prima della scadenza",
  PRICE_OUTSIDE_STRUCTURAL_AREA: "prezzo fuori dall'area d'ingresso",
  NO_ROOM_AFTER_COSTS: "spazio verso il target insufficiente dopo i costi",
  AT_OR_BEYOND_INVALIDATION: "prezzo al livello di invalidazione o oltre",
  REWARD_RISK_BELOW_MINIMUM: "rapporto rendimento/rischio sotto il minimo",
  AT_OPPOSING_AREA: "prezzo in un'area contraria",
  QUOTE_STALE: "quotazione non aggiornata",
  QUOTE_UNAVAILABLE: "quotazione non disponibile",
  QUOTE_CLOCK_UNCERTAIN: "orario della quotazione incerto",
  CANDLE_CONNECTION_LOST: "connessione ai dati di mercato interrotta",
  CANDLE_CONNECTION_AWAITING_FRESH_BAR: "in attesa di dati nuovi dopo la riconnessione",
  LIVE_SESSION_STOPPED: "sessione live fermata",
  SESSION_NOT_CURRENT: "sessione non corrente",
  RECONSTRUCTED_REQUIRES_FRESH_CALL: "indicazione ricostruita: serve una nuova valutazione live",
  RECONSTRUCTED_CATCH_UP: "recupero dello storico in corso",
  TRADE_15M_NOT_READY: "contesto a 15 minuti non pronto",
  TRADE_1H_NOT_READY: "contesto a 1 ora non pronto",
  TRADE_1M_STALE: "dati a 1 minuto non aggiornati",
  THESIS_TERMINAL: "indicazione conclusa",
  CERTIFIED_TARGET_CONTACT: "contatto certificato con il target operativo della call",
};

export function reasonIt(code: string): string {
  return REASON_IT[code.split(":")[0]] ?? `motivo registrato: ${code}`;
}

function Arrow({ d }: { d: string | undefined }) {
  if (d === "UP") return <span className="dir-arrow up" aria-hidden>▲</span>;
  if (d === "DOWN") return <span className="dir-arrow down" aria-hidden>▼</span>;
  return <span className="dir-arrow flat" aria-hidden>◆</span>;
}

/** The single authoritative state of the panel (from the backend fields only). */
export function proposalState(v: LiveView | null): { key: string; text: string; tone: Tone } {
  if (!v) return { key: "NO_VIEW", text: "Nessuna valutazione in corso", tone: "neutral" };
  const c = v.call;
  if (!c) return { key: "WAITING", text: "In attesa — nessun ingresso proposto", tone: "neutral" };
  if (c.thesis_status !== "ONGOING") {
    return { key: "TERMINAL", text: "Indicazione conclusa — ingresso non disponibile", tone: "neutral" };
  }
  if (c.entry_status === "AVAILABLE" && c.presentation !== "NOT_CURRENT") {
    return { key: "AVAILABLE", text: "Ingresso disponibile secondo il sistema", tone: "pos" };
  }
  if (c.entry_status === "CLOSED") return { key: "CLOSED", text: "Ingresso non disponibile adesso", tone: "neg" };
  if (c.entry_status === "UNVERIFIED" || c.entry_status === "AVAILABLE") {
    return { key: "UNVERIFIED", text: "Non è possibile confermare la disponibilità dell'ingresso", tone: "warn" };
  }
  return { key: "UNKNOWN", text: `Stato dell'ingresso non riconosciuto (${c.entry_status}): non considerarlo disponibile`, tone: "warn" };
}

/** What the principal scenario still needs, from its recorded state; null when the system states nothing. */
/** v0.7: the engine's published trigger/destination verdict in plain Italian (the UI never computes it). */
function incompatibleIt(td: NonNullable<ScenarioState["trigger_destination"]>): string {
  return `Scenario riconosciuto, ma la condizione attuale (una chiusura a ${fmtPrice(td.threshold)}) è già alla destinazione `
    + `${fmtPrice(td.destination)} o oltre: la toccherebbe prima, quindi non può confermare una continuazione verso di essa `
    + "con i livelli attuali. Non sostiene la direzione; può tornare valido solo se il sistema pubblica una revisione "
    + "compatibile (non è promessa).";
}

/** v0.7: what the published MarketView says beside incompatible scenarios - its own row and principal only, never
 * deduced from an absent principal; null when the row states nothing to translate here. */
function incompatibleReadingIt(mv: MarketViewDoc, incompatible: ScenarioState[]): string | null {
  const p = mv.principal;
  switch (mv.table_row) {
    case "CONDITIONAL_SCENARIO":
      return p && !incompatible.some((s) => s.scenario_id === p.scenario_id)
        ? `Un altro scenario (${p.direction} ${p.family}) sostiene la lettura corrente.` : null;
    case "OPPOSING_SCENARIOS":
      return "Esistono sostegni direzionali opposti: la lettura non indica una direzione unica.";
    case "REQUIRED_CONTEXT_UNAVAILABLE":
      return "Il sistema non può pubblicare una lettura direzionale corrente.";
    case "WATCH_ONLY":
      return "Nella lettura pubblicata non c'è un'aspettativa direzionale sostenuta.";
    default:
      return null;
  }
}

function restoredIt(td: NonNullable<ScenarioState["trigger_destination"]>): string {
  return `La condizione è stata rivista${td.revision_published_at ? ` alle ${fmtTime(td.revision_published_at)}` : ""}: `
    + "quella precedente era incompatibile con la destinazione; lo scenario sostiene la direzione solo da questa nuova pubblicazione.";
}

function condition(p: ScenarioView, s: ScenarioState | undefined): string | null {
  if (s?.entry_ended) return "Il tentativo d'ingresso di questo scenario si è concluso senza call; lo scenario non è invalidato.";
  if (s?.observing) return "Scenario in osservazione: serve una nuova reazione completa del prezzo.";
  if (s?.waiting?.phase === "WAIT_RESPONSE") {
    return "Scenario confermato: serve una ripresa locale del prezzo (regola esatta negli approfondimenti).";
  }
  if (s?.waiting) {
    return s.waiting.corridor
      ? `Scenario confermato: serve un ritorno del prezzo nel corridoio ${fmtPrice(s.waiting.corridor[0])} – ${fmtPrice(s.waiting.corridor[1])}.`
      : "Scenario confermato: nessun corridoio di ritorno residuo.";
  }
  const td = s?.trigger_destination;
  if (td && !td.compatible) return incompatibleIt(td);
  const status = s?.status ?? p.status ?? "ARMED";
  const k = s?.trigger_level ?? p.trigger_level;
  if (status === "ARMED" && k && td?.restored_by_revision) {
    return `Serve l'innesco: una chiusura oltre ${fmtPrice(k)}. ${restoredIt(td)}`;
  }
  if (status === "ARMED" && k) return `Serve l'innesco: una chiusura oltre ${fmtPrice(k)}.`;
  if (status === "WATCH") return "Si osserva una possibile reazione: nessun innesco ancora definito.";
  return null;
}

function ScenarioCards({ v }: { v: LiveView }) {
  const mv = v.market_view;
  return (
    <>
      {mv?.principal && (
        <div className="call-scenario" data-testid="live-scenario">
          <Badge tone={mv.principal.direction === "LONG" ? "pos" : "neg"}>{mv.principal.direction === "LONG" ? "▲" : "▼"} {mv.principal.direction} {mv.principal.family}{" "}
            {(mv.principal.status ?? "ARMED").toLowerCase()}</Badge>
          <span className="small-text">{mv.principal.antecedent}</span>
        </div>
      )}
      {(v.scenarios ?? []).filter((s) => s.entry_ended).map((s) => (
        <div className="call-waiting" key={`${s.scenario_id}-ended`} data-testid="live-entry-ended">
          <Badge tone="neutral">{s.direction} {s.family} confirmed — entry attempt ended</Badge>
          <p className="small-text">{s.entry_ended!.text} This is not a call and not an invalidation of the scenario.</p>
          <dl className="call-geo">
            <dt>Why</dt><dd>{s.entry_ended!.base === "CORRIDOR" ? "no confirming close could be inside the usable corridor"
              : "no confirming close could be inside the historical economic region"}</dd>
            <dt>Ended at</dt><dd className="mono">{fmtTime(s.entry_ended!.at)}</dd>
            <dt>Scenario</dt><dd>still {s.status.toLowerCase()} · invalid at {fmtPrice(s.invalidation_level)}</dd>
          </dl>
        </div>
      ))}
      {(v.scenarios ?? []).filter((s) => s.observing).map((s) => (
        <div className="call-waiting" key={s.scenario_id} data-testid="live-observing">
          <Badge tone="neutral">{s.direction} {s.family} — scenario under observation</Badge>
          <p className="small-text">{s.observing!.text} The previous reaction anchor
            {s.observing!.lost_anchor?.V ? ` (stop ${s.observing!.lost_anchor.V})` : ""} was touched before confirmation.
            This is not a call and not an entry: nothing to do now.</p>
          <dl className="call-geo">
            <dt>Narrative destination</dt><dd className="mono">{fmtPrice(s.destination)}</dd>
            <dt>Observation ends</dt><dd className="mono">{fmtTime(s.observing!.original_expiry)} (original deadline)</dd>
          </dl>
        </div>
      ))}
      {(v.scenarios ?? []).filter((s) => s.waiting).map((s) => (
        <div className="call-waiting" key={s.scenario_id} data-testid="live-waiting">
          <Badge tone="neutral" icon="clock">{s.direction} {s.family} confirmed — {s.waiting!.phase === "WAIT_RESPONSE"
            ? "waiting for a local recovery" : "waiting for a usable price"}</Badge>
          <p className="small-text">{s.waiting!.text} This is not a call: do not treat it as “enter now”.</p>
          {s.waiting!.response && (
            <dl className="kv-grid small-text" data-testid="live-waiting-response">
              <dt>Return reference</dt><dd className="mono">H0 {fmtPrice(s.waiting!.response.H0)} · L0 {fmtPrice(s.waiting!.response.L0)} · published {fmtTime(s.waiting!.response.published_at)}</dd>
              <dt>Call possible only if</dt><dd>{s.waiting!.response.recovery_rule}</dd>
              <dt>Ends this attempt</dt><dd>{s.waiting!.response.contradiction_rule}</dd>
            </dl>
          )}
          <dl className="call-geo">
            <dt>Usable return corridor</dt><dd className="mono">{s.waiting!.corridor ? `${fmtPrice(s.waiting!.corridor[0])} – ${fmtPrice(s.waiting!.corridor[1])}` : "none left"}</dd>
            <dt>Target now</dt><dd className="mono">{fmtPrice(s.waiting!.target_now)} <span className="muted">(at confirmation {fmtPrice(s.waiting!.target_at_confirmation)})</span></dd>
            <dt>Stop guidance if issued</dt><dd className="mono">{fmtPrice(s.waiting!.stop_V)}</dd>
            <dt>Waits until</dt><dd className="mono">{fmtTime(s.waiting!.wait_until)} · hard deadline {fmtTime(s.waiting!.hard_deadline)}</dd>
            <dt>Blockers now</dt><dd>{s.waiting!.blockers.length ? s.waiting!.blockers.map(reasonText).join(", ") : "none (waiting for a fresh minute)"}</dd>
          </dl>
        </div>
      ))}
    </>
  );
}

const QUOTE_TITLES: [string, string][] = [
  ["QUOTE_STALE", "Ingresso non verificabile — attendi una quotazione aggiornata."],
  ["QUOTE_UNAVAILABLE", "Ingresso non verificabile — manca una quotazione utilizzabile."],
  ["QUOTE_CLOCK_UNCERTAIN", "Ingresso non verificabile — l'orario della quotazione è incerto."],
];
const CONNECTION = new Set(["CANDLE_CONNECTION_LOST", "CANDLE_CONNECTION_AWAITING_FRESH_BAR"]);
const WAIT_AGAIN = "Adesso il sistema non presenta un ingresso utilizzabile: occorre attendere che ne confermi di nuovo " +
  "la disponibilità (“Ingresso disponibile secondo il sistema”). La tesi della call è un'informazione separata.";

/** Practical consequence of UNVERIFIED, from the recorded reasons only: what waiting can (or cannot) resolve. */
export function unverifiedExplanation(c: CallView): { title: string; body: string; kind: string } {
  const codes = c.entry_reasons.map((r) => r.split(":")[0]);
  if (c.presentation === "NOT_CURRENT" || codes.includes("SESSION_NOT_CURRENT") || codes.includes("LIVE_SESSION_STOPPED")) {
    return { kind: "NOT_CURRENT", title: "Ingresso non verificabile — la sessione live non è corrente.",
      body: "Questa è l'ultima valutazione salvata, non una proposta attuale: adesso il sistema non presenta un ingresso " +
            "utilizzabile e non può confermarne la disponibilità finché la sessione non è corrente." };
  }
  const quote = QUOTE_TITLES.filter(([k]) => codes.includes(k));
  if (codes.length && quote.length && codes.every((k) => QUOTE_TITLES.some(([q]) => q === k))) {
    return { kind: "QUOTE", title: quote[0][1], body: WAIT_AGAIN };
  }
  if (codes.length && codes.every((k) => CONNECTION.has(k))) {
    return { kind: "CONNECTION", title: "Ingresso non verificabile — dati di mercato non aggiornati.", body: WAIT_AGAIN };
  }
  return { kind: "OTHER", title: "Ingresso non verificabile.",
    body: "Adesso il sistema non presenta un ingresso utilizzabile. Finché non ne conferma di nuovo la disponibilità, " +
          "non considerarlo disponibile." };
}

const itNum = fmtPrice;
function fmtPriceOr(x: string | null | undefined, none: string): string {
  return x === null || x === undefined || x === "" ? none : fmtPrice(x);
}

export type GuidanceKind = "HOLD" | "ENTRY_VALID" | "ENTRY_UNVERIFIED" | "TARGET_REACHED" | "EXIT" | "UNKNOWN" | "MISSING";

/** Plain Italian for the system texts the engine actually writes (``_entry_guidance``/``_terminal_guidance``), with the
 * values taken from the recognised text. Anything else is declared unrecognised: no operational instruction is shown,
 * and nothing is ever derived from the thesis, the expected direction or the levels. */
export function readGuidance(g: string | null | undefined): { kind: GuidanceKind; text: string } {
  if (!g) return { kind: "MISSING", text: "Il sistema non ha registrato un testo per questa call: nessuna indicazione è mostrata." };
  let m = g.match(/^Thesis ongoing but new entry is closed now \(([^)]*)\)\. If following this call: hold with stop (\S+), target (\S+)\.$/);
  if (m) return { kind: "HOLD", text: `Il sistema indica di mantenere l'operazione con stop ${itNum(m[2])} e target ${itNum(m[3])}.` };
  m = g.match(/^Entry still valid now inside the admissible part of (\S+)–(\S+); stop (\S+), target (\S+), hard deadline (\S+)\.$/);
  if (m) {
    return { kind: "ENTRY_VALID", text: `Il testo del sistema riguarda l'ingresso: valido ora nella parte ammessa di ${itNum(m[1])}–${itNum(m[2])}, ` +
      `con stop ${itNum(m[3])}, target ${itNum(m[4])} e scadenza ${fmtLocal(m[5])}. Non contiene un'indicazione specifica per chi ha già aperto.` };
  }
  if (g === "Thesis ongoing; current entry cannot be verified (no fresh quote). Do not treat as ready now.") {
    return { kind: "ENTRY_UNVERIFIED", text: "Il testo del sistema riguarda l'ingresso: tesi in corso, ma l'ingresso attuale non è " +
      "verificabile (nessuna quotazione aggiornata) e non va considerato pronto ora. Non contiene un'indicazione specifica per chi ha già aperto." };
  }
  if (g === "Target reached: the call's guidance is complete.") {
    return { kind: "TARGET_REACHED", text: "Target della call raggiunto: l'indicazione è conclusa." };
  }
  if (g === "Invalidation level touched: the thesis is invalid; exit guidance if following this call.") {
    return { kind: "EXIT", text: "Livello di invalidazione toccato: la tesi non è più valida; per chi segue questa call il sistema indica l'uscita." };
  }
  if (g === "Hard deadline reached: exit guidance if following this call.") {
    return { kind: "EXIT", text: "Scadenza raggiunta: per chi segue questa call il sistema indica l'uscita." };
  }
  if (g === "Cannot be assessed any more (data gap/ambiguity): exit guidance if following this call; no safety is assumed for unseen intervals.") {
    return { kind: "EXIT", text: "Non più valutabile (lacuna o ambiguità nei dati): per chi segue questa call il sistema indica l'uscita; " +
      "nessuna sicurezza è presunta per gli intervalli non osservati." };
  }
  m = g.match(/^Thesis retired \(([^)]*)\): exit guidance if following this call\. This is guidance withdrawal, not a statement about any position\.$/);
  if (m) {
    return { kind: "EXIT", text: `Tesi ritirata (${m[1]}): per chi segue questa call il sistema indica l'uscita. ` +
      "È il ritiro dell'indicazione, non un'affermazione su una posizione." };
  }
  return { kind: "UNKNOWN", text: "Testo del sistema non riconosciuto: nessuna indicazione operativa è mostrata. " +
    "Il testo originale è negli approfondimenti." };
}

const PERSPECTIVES = "Due prospettive ipotetiche: l'app non sa se hai aperto un'operazione.";
const NO_POSITION = "Se non hai ancora aperto un'operazione";
const FOLLOWING = "Se hai già aperto un'operazione su questa call";

function EntryFacts({ c, available }: { c: CallView; available: boolean }) {
  const reasons = c.entry_reasons.length ? c.entry_reasons.map(reasonIt).join("; ") : "nessun motivo registrato";
  return (
    <dl className="call-geo proposal-facts">
      {available ? (
        <><dt>Fascia d'ingresso ammessa ora</dt>
          <dd className="mono" data-testid="live-admissible">{c.admissible_bounds ? `${fmtPrice(c.admissible_bounds[0])} – ${fmtPrice(c.admissible_bounds[1])}` : "non indicata dal sistema"}</dd></>
      ) : (
        <><dt>Motivo</dt><dd data-testid="live-entry-reasons">{reasons}</dd></>
      )}
    </dl>
  );
}

/** The perspective of someone already following the call: what the recorded system text says, in plain Italian. */
function CallUpdate({ c, v }: { c: CallView; v: LiveView }) {
  const notCurrent = c.presentation === "NOT_CURRENT";
  const r = notCurrent ? { kind: "NOT_CURRENT", text: "Sessione non corrente: l'ultimo testo salvato non è presentato come " +
    "indicazione attuale (resta negli approfondimenti e nella cronologia)." } : readGuidance(c.guidance);
  return (
    <>
      <div className="persp-guidance" data-testid="live-call-guidance" data-kind={r.kind}>{r.text}</div>
      {!notCurrent && (
        <div className="small-text muted" data-testid="live-call-guidance-basis">In base al testo registrato dal sistema alla
          valutazione del {fmtLocal(v.clock)}; l'originale è negli approfondimenti.</div>
      )}
    </>
  );
}

/** A terminated call, for someone who was following it: its recorded conclusion (read-only call API), never extended by
 * the current market reading and never turned into an instruction the recorded text does not give. */
function ConcludedCall({ v, t, expected }: { v: LiveView; t: LiveView["recent_calls"][number]; expected: string }) {
  const key = `${v.run_id}|${t.call_id}|${t.terminal_at}`;
  const [rec, setRec] = useState<{ key: string; target: string | null; text: string | null; at: string | null } | null>(null);
  useEffect(() => {
    if (!v.run_id) return;
    let live = true;
    adviserApi.call(v.run_id, t.call_id).then((d) => {
      const last = [...d.revisions].reverse().find((r) => r.thesis_status === t.terminal);
      if (live) setRec({ key, target: d.call?.target ?? null, text: last?.guidance ?? null, at: last?.env.published_at ?? null });
    }).catch(() => { if (live) setRec({ key, target: null, text: null, at: null }); });
    return () => { live = false; };
  }, [key]);  // eslint-disable-line react-hooks/exhaustive-deps
  const r = rec?.key === key ? rec : null;  // never shown under another call or run
  const reading = r ? (r.text ? readGuidance(r.text)
    : { kind: "MISSING", text: "Testo registrato alla conclusione non disponibile: nessuna indicazione operativa è mostrata." }) : null;
  return (
    <div className="stack-sm" data-testid="live-call-concluded" data-terminal={t.terminal}>
      <div className="persp-guidance" data-testid="live-concluded-guidance" data-kind={reading?.kind ?? "LOADING"}>
        {reading ? reading.text : "…"}</div>
      <p data-testid="live-last-terminal">Ultima indicazione: {t.direction} {t.family},{" "}
        {THESIS_IT[t.terminal] ?? t.terminal} ({fmtLocal(t.terminal_at)}).</p>
      <dl className="call-geo proposal-facts persp-facts">
        <dt>Motivo registrato</dt><dd data-testid="live-concluded-reason">{reasonIt(t.reason)}</dd>
        {t.terminal === "TARGET_REACHED" && (
          <><dt>Target operativo della call</dt>
            <dd className="mono" data-testid="live-concluded-target">{r ? (r.target ? `${fmtPrice(r.target)} — raggiunto` : "non disponibile") : "…"}</dd></>
        )}
      </dl>
      <p className="small-text" data-testid="live-concluded-separation">
        {expected !== "UNAVAILABLE" ? `La successiva aspettativa (${(EXPECTED_IT[expected] ?? expected).toLowerCase()}) non prolunga questa call: ` +
          "è una valutazione nuova del mercato." : "La lettura attuale del mercato non prolunga questa call: è una valutazione nuova."}</p>
      {r?.text && (
        <details className="more" data-testid="live-concluded-original">
          <summary><Icon name="chevron" size={14} className="summary-chevron" /> Testo originale registrato ({fmtLocal(r.at)})</summary>
          <div className="more-body"><span className="mono small-text" data-testid="live-concluded-text">{r.text}</span></div>
        </details>
      )}
    </div>
  );
}

// Colour map: blue = new entry available, amber = attention / not verifiable,
// grey = waiting, closed entry, history and conclusion; green/red only for the call direction. Always icon + text.
const SIGNAL: Record<string, { cls: string; icon: IconName }> = {
  AVAILABLE: { cls: "sig-avail", icon: "check" }, CLOSED: { cls: "sig-muted", icon: "pause" },
  UNVERIFIED: { cls: "sig-attn", icon: "alert" }, UNKNOWN: { cls: "sig-attn", icon: "alert" },
  TERMINAL: { cls: "sig-muted", icon: "stop" }, WAITING: { cls: "sig-muted", icon: "clock" }, NO_VIEW: { cls: "sig-muted", icon: "clock" },
};

function DirChip({ dir, ended }: { dir: string; ended?: boolean }) {
  return (
    <span className={cx("dir-chip", dir === "LONG" ? "dir-long" : "dir-short", ended && "is-ended")} data-testid="live-call-direction">
      {dir === "LONG" ? "▲" : "▼"} {dir}</span>
  );
}

/** One strip with the call's identity and its operational levels (shown once). */
function CallStrip({ c, t, unverified }: { c: CallView | null; t: LiveView["recent_calls"][number] | undefined; unverified: boolean }) {
  if (c) {
    return (
      <div className="call-strip" data-testid="live-call-identity">
        <div className="strip-head">
          <DirChip dir={c.direction} />
          <div className="strip-id">
            <span className="strip-title">Call {c.family} · {c.family_text}</span>
            <span className="small-text strip-sub">{c.direction === "LONG" ? "Indicazione di acquisto: il sistema si aspetta un rialzo del prezzo."
              : "Indicazione di vendita: il sistema si aspetta un ribasso del prezzo."} Emessa {fmtLocal(c.issued_at)}.</span>
          </div>
        </div>
        <dl className="strip-levels">
          <div><dt>Target operativo</dt><dd className="mono" data-testid="live-target">{fmtPrice(c.target)}</dd></div>
          <div><dt>Stop indicato</dt><dd className="mono" data-testid="live-stop-guidance">{fmtPrice(c.stop)}</dd></div>
          <div><dt>Scadenza dell'indicazione</dt><dd data-testid="live-deadline">{fmtLocal(c.hard_deadline)}</dd></div>
          <div><dt>Orizzonte atteso</dt><dd>{c.expected_minutes ? `${c.expected_minutes[0]}–${c.expected_minutes[1]} min` : "non indicato"}</dd></div>
          <div><dt>Tesi</dt><dd data-testid="live-thesis">{THESIS_IT[c.thesis_status] ?? c.thesis_status}</dd></div>
        </dl>
        {unverified && <p className="small-text muted" data-testid="live-call-levels-note">Livelli della call già emessa: target e stop
          da soli non sono una proposta d'ingresso attuale.</p>}
      </div>
    );
  }
  if (t) {
    return (
      <div className="call-strip is-ended" data-testid="live-call-identity">
        <div className="strip-head">
          <DirChip dir={t.direction} ended />
          <div className="strip-id">
            <span className="strip-title">Call {t.family} <span className="sig-chip sig-muted"><Icon name="stop" size={13} />
              Conclusa — {(THESIS_IT[t.terminal] ?? t.terminal).replace(/^conclusa — /, "")}</span></span>
            <span className="small-text strip-sub">Ultima call, conclusa {fmtLocal(t.terminal_at)}. Non è più un'indicazione attiva.</span>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="call-strip is-none" data-testid="live-call-identity">
      <span className="sig-chip sig-muted"><Icon name="clock" size={13} /> Nessuna call emessa in questo momento</span>
    </div>
  );
}

// "Lettura attuale del mercato" box, three linked steps (presentation only, fields of the served view):
// 1. what is observed: market_view.observed_context (1h) and market_view.phase (15m), plain Italian of the engine's own
//    classes (core.py _derive_1h/_derive_15m); 2. what it concludes: expected_direction, conditional, table_row and the
//    recorded reason, translated only for reason texts the engine writes (core.py/core3.py compute_view), otherwise kept
//    as technical text; 3. what it is waiting for: the condition published for a scenario (condition()), never a trigger
//    derived here. "No scenario" is said only when every published scenario list is present and empty; the absence of a
//    call is never used for it. Unknown or missing values are declared, not guessed.

const CONTEXT_IT: Record<string, [string, string | null]> = {
  UP: ["in rialzo", "nelle ultime ore il prezzo è salito in modo ampio e regolare"],
  DOWN: ["in ribasso", "nelle ultime ore il prezzo è sceso in modo ampio e regolare"],
  BALANCED: ["in equilibrio", "nelle ultime ore il prezzo non si è mosso in modo abbastanza ampio e regolare in una direzione"],
  UNAVAILABLE: ["non disponibile", "dati a 1 ora insufficienti o non aggiornati"],
};

const PHASE_IT: Record<string, [string, string | null]> = {
  EXPANSION: ["espansione", "il prezzo si muove in modo ampio e regolare"],
  COMPRESSION: ["compressione", "le escursioni recenti si sono ristrette, senza un movimento regolare"],
  REACTION: ["reazione", "il prezzo si muove contro il contesto a 1 ora"],
  ROTATION: ["rotazione", "il prezzo oscilla senza progredire, sia a 1 ora sia a 15 minuti"],
  TRANSITION: ["transizione", "il movimento non corrisponde a nessuna delle altre fasi riconosciute"],
  UNAVAILABLE: ["non disponibile", "dati insufficienti o non aggiornati per classificarla"],
};

const CONCLUSION_IT: Record<string, string> = {
  UP: "Il sistema indica un rialzo.",
  DOWN: "Il sistema indica un ribasso.",
  BALANCED: "Il sistema legge il mercato in equilibrio: non indica né un rialzo né un ribasso.",
  UNCERTAIN: "Il sistema non indica una direzione: la lettura resta incerta.",
  UNAVAILABLE: "Il sistema non può formare una lettura con i dati attuali.",
};

const STATUS_IT: Record<string, string> = { WATCH: "in osservazione", ARMED: "armato", CONFIRMED: "confermato" };

/** One observed class in plain Italian: missing and unrecognized values are declared, never mapped to a neighbour. */
function observed(table: Record<string, [string, string | null]>, value: string | null | undefined): [string, string | null] {
  if (value === null || value === undefined || value === "") return ["non indicato dal sistema", null];
  return table[value] ?? [`valore non riconosciuto (${value})`, null];
}

/** The recorded reason in plain Italian, only for the exact texts the engine writes; null keeps it technical. */
export function readingReasonIt(r: string): string | null {
  let m: RegExpMatchArray | null;
  if (/^observed \w+\/\w+; missing antecedent: no born A impulse or compression box scenario$/.test(r)) {
    return "Manca il presupposto: non è nato nessuno scenario di impulso (famiglia A) o di box di compressione.";
  }
  if ((m = r.match(/^balanced 1h context in (compression|rotation); no qualified box$/))) {
    return `Contesto a 1 ora in equilibrio con fase di ${m[1] === "compression" ? "compressione" : "rotazione"}; `
      + "nessun box qualificato, quindi nessun limite di prezzo indicato.";
  }
  if ((m = r.match(/^balanced 1h context in (compression|rotation); rotation inside \[([^,\]]+), ([^\]]+)\]$/))) {
    return `Contesto a 1 ora in equilibrio con fase di ${m[1] === "compression" ? "compressione" : "rotazione"}; `
      + `il prezzo ruota dentro il box ${fmtPrice(m[2])} – ${fmtPrice(m[3])}.`;
  }
  if (/^observed \w+\/\w+ without a supported prospective plan$/.test(r)) {
    return "Con questo contesto e questa fase il metodo non ha un piano supportato.";
  }
  if (/^(supported armed\/confirmed|valid armed) scenarios point in opposite directions/.test(r)) {
    return "Ci sono scenari attivi in direzioni opposte.";
  }
  if (/^the ongoing call is opposed by a valid armed scenario$/.test(r)) {
    return "La call in corso ha contro uno scenario armato valido.";
  }
  if ((m = r.match(/^observed hypotheses without current directional support: (.+) \(not a forecast, not a call\)$/))) {
    const items = m[1].split(/, (?=[ABC] (?:LONG|SHORT) )/).map((x) => {
      const it = x.match(/^([ABC]) (LONG|SHORT) (WATCH|ARMED|CONFIRMED)( \(recovery condition incompatible with its destination\))?$/);
      if (!it) return x;
      return `${it[2]} ${it[1]} ${STATUS_IT[it[3]] ?? it[3]}${it[4] ? " con condizione incompatibile con la destinazione" : ""}`;
    });
    return `Ci sono solo ipotesi osservate senza sostegno direzionale attuale: ${items.join(", ")}. Non sono una previsione né una call.`;
  }
  if ((m = r.match(/^([ABC]) (LONG|SHORT) armed, not counted as directional support: current recovery condition incompatible with its destination: the required complete 1m close (>=|<=) (\S+) is at or beyond the destination ([^,\s]+),/))) {
    return `Lo scenario ${m[2]} ${m[1]} è riconosciuto, ma la sua condizione attuale (chiusura a 1 minuto ${m[3] === ">=" ? "≥" : "≤"} `
      + `${fmtPrice(m[4])}) è già alla destinazione ${fmtPrice(m[5])} o oltre: non può confermare una continuazione verso di essa `
      + "con i livelli attuali, quindi non conta come sostegno direzionale.";
  }
  if (/^only conditional WATCH hypotheses: /.test(r)) {
    return "Ci sono solo ipotesi in osservazione: non sono una previsione né una call.";
  }
  if ((m = r.match(/^([ABC]) (LONG|SHORT) (armed|confirmed)(:| )/))) {
    return `Uno scenario ${m[2]} della famiglia ${m[1]} è ${m[3] === "armed" ? "armato" : "confermato"}.`;
  }
  if ((m = r.match(/^ongoing ([ABC]) (LONG|SHORT) toward /))) {
    return `È in corso una call ${m[2]} della famiglia ${m[1]} finché la sua premessa regge.`;
  }
  return null;
}

/** A published scenario (principal, alternative, watch or listed) with the condition it states, if any. */
function ScenarioWait({ p, s }: { p: ScenarioView; s: ScenarioState | undefined }) {
  const status = s?.status ?? p.status;
  return (
    <li data-testid="live-waiting-scenario">
      Scenario {p.direction} {p.family}{status ? ` (${STATUS_IT[status] ?? status})` : ""}:{" "}
      {condition(p, s) ?? "il sistema non ha pubblicato una condizione specifica per questo scenario."}
    </li>
  );
}

/** The current market reading, shown under the chart: a market assessment, never the call. Without a view the
 * direction is declared unavailable, never inferred. */
export function MarketReading({ v }: { v: LiveView | null }) {
  const mv = v?.market_view ?? null;
  const d = mv?.expected_direction ?? "UNAVAILABLE";
  const p = mv?.principal ?? null;
  const ps = p ? (v?.scenarios ?? []).find((s) => s.scenario_id === p.scenario_id) : undefined;
  const [ctxText, ctxGloss] = observed(CONTEXT_IT, mv?.observed_context);
  const [phText, phGloss] = observed(PHASE_IT, mv?.phase);
  const reasons = mv?.reasons ?? [];
  const reasonsIt = reasons.map(readingReasonIt);
  // published scenario lists other than the principal (an absent list is unknown, never "empty")
  const listed: ScenarioView[] = [
    ...(mv?.alternatives ?? []),
    ...(mv?.watch ?? []),
  ];
  const states = v?.method === "v0.2" ? null : v?.scenarios;
  const others: { p: ScenarioView; s: ScenarioState | undefined }[] = [
    ...listed.map((x) => ({ p: x, s: (states ?? []).find((s) => s.scenario_id === x.scenario_id) })),
    ...(states ?? []).filter((s) => s.scenario_id !== p?.scenario_id && !listed.some((x) => x.scenario_id === s.scenario_id))
      .map((s) => ({ p: s as unknown as ScenarioView, s })),
    ...((v?.method === "v0.2" ? v?.attempts : []) ?? []).filter((a) => a.attempt_id !== p?.scenario_id)
      .map((a) => ({ p: { scenario_id: a.attempt_id, family: a.family, direction: a.direction, status: a.status,
                          trigger_level: a.trigger_level } as unknown as ScenarioView, s: undefined })),
  ];
  const listsKnown = !!mv && Array.isArray(mv.alternatives)
    && (v?.method === "v0.2" ? Array.isArray(v?.attempts) : Array.isArray(v?.scenarios));
  const ongoingCall = !!v?.call || !!mv?.ongoing_call_id;
  const noScenario = !p && others.length === 0 && listsKnown && !ongoingCall;
  const noRevisionEvent = !p && others.length === 0;
  const incompatible = (states ?? []).filter((s) => s.trigger_destination && !s.trigger_destination.compatible);
  const incompatibleReading = mv && incompatible.length > 0 ? incompatibleReadingIt(mv, incompatible) : null;
  const restored = ps?.trigger_destination?.restored_by_revision ? ps.trigger_destination : null;
  return (
    <section className="decision-market" data-testid="live-market-reading">
      <div className="market-head">
        <span className="persp-title">Lettura attuale del mercato</span>
        <span className="muted small-text">È una valutazione del mercato, non la call: non dice se entrare.</span>
      </div>
      <div className="mr-steps">
        <div className="mr-step" data-testid="live-observes">
          <div className="mr-step-title">Che cosa osserva</div>
          {mv ? (
            <ul className="mr-list">
              <li data-testid="live-observed-context">Contesto a 1 ora: <b>{ctxText}</b>{ctxGloss && <span className="muted"> — {ctxGloss}</span>}</li>
              <li data-testid="live-observed-phase">Fase a 15 minuti: <b>{phText}</b>{phGloss && <span className="muted"> — {phGloss}</span>}</li>
            </ul>
          ) : <p className="small-text muted">Nessuna osservazione pubblicata.</p>}
        </div>
        <div className="mr-step" data-testid="live-concludes">
          <div className="mr-step-title">Che cosa ne conclude</div>
          <div className="proposal-dir market-dir" data-testid="live-direction">
            <Arrow d={d} />
            <span>Direzione attesa: <b data-testid="live-expected" className={d === "UP" ? "dir-long" : d === "DOWN" ? "dir-short" : undefined}>
              {EXPECTED_IT[d] ?? d}</b>{mv?.conditional ? " (condizionale)" : ""}</span>
            {mv && <span className="muted small-text">· {ROW_IT[mv.table_row] ?? humanize(mv.table_row)}</span>}
          </div>
          {mv && <p className="small-text" data-testid="live-conclusion">{CONCLUSION_IT[d] ?? `Lettura non riconosciuta (${d}).`}</p>}
          {mv && incompatible.length > 0 && (
            <p className="small-text" data-testid="live-incompatible">
              {incompatible.map((s) => `Scenario ${s.direction} ${s.family}: ${incompatibleIt(s.trigger_destination!)}`).join(" ")}
              {incompatibleReading && ` ${incompatibleReading}`}
            </p>)}
          {mv && restored && (
            <p className="small-text" data-testid="live-restored">Scenario {p!.direction} {p!.family}: {restoredIt(restored)}</p>)}
          {mv && (
            <p className="small-text" data-testid="live-reason">
              {reasons.length === 0 ? "Il sistema non ha registrato una motivazione testuale per questa lettura."
                : reasonsIt.every((x) => x === null) ? "La motivazione è registrata solo come testo tecnico (vedi i termini tecnici qui sotto)."
                : `Perché: ${reasonsIt.filter((x) => x !== null).join(" ")}${reasonsIt.some((x) => x === null)
                  ? " Altre motivazioni sono registrate solo come testo tecnico." : ""}`}
            </p>
          )}
        </div>
        <div className="mr-step" data-testid="live-waiting-for">
          <div className="mr-step-title">Che cosa sta aspettando</div>
          {!v ? <p className="small-text muted">Nessuna valutazione in corso.</p>
            : p ? (
              <dl className="market-facts" data-testid="live-scenario-levels">
                <div><dt>Scenario</dt><dd>{p.direction} {p.family}</dd></div>
                <div><dt>Destinazione dello scenario</dt>
                  <dd><span className="mono">{fmtPriceOr(ps?.destination ?? p.destination ?? p.conditional_target, "non indicata")}</span> <span className="muted">(non è un target operativo)</span></dd></div>
                <div><dt>Invalidazione dello scenario</dt>
                  <dd><span className="mono">{fmtPriceOr(ps?.invalidation_level ?? p.invalidation_level, "non indicata")}</span> <span className="muted">(livello strutturale, non è uno stop)</span></dd></div>
                <div><dt>Orizzonte atteso</dt><dd>{mv?.horizon_minutes ? `${mv.horizon_minutes[0]}–${mv.horizon_minutes[1]} min` : "non indicato"}</dd></div>
                <div className="span-all"><dt>Condizione ancora necessaria</dt><dd data-testid="live-condition">{condition(p, ps) ?? "il sistema non ha pubblicato una condizione specifica per questo scenario"}</dd></div>
              </dl>
            ) : others.length > 0 ? (
              <ul className="mr-list small-text" data-testid="live-waiting-others">
                {others.slice(0, 4).map((x) => <ScenarioWait key={x.p.scenario_id} p={x.p} s={x.s} />)}
              </ul>
            ) : ongoingCall ? (
              <p className="small-text" data-testid="live-ongoing-call">È in corso una call: ingresso e aggiornamenti sono nel pannello
                «Che cosa propone il sistema adesso».</p>
            ) : noScenario ? (
              <p className="small-text" data-testid="live-no-scenario">Non c'è ancora uno scenario attivo. Il sistema non ha pubblicato
                una condizione specifica da attendere per un ingresso.</p>
            ) : <p className="small-text" data-testid="live-no-condition">Il sistema non ha pubblicato una condizione specifica da attendere
                per un ingresso.</p>}
        </div>
      </div>
      {mv && (
        <details className="more mr-tech" data-testid="live-reading-tech">
          <summary><Icon name="chevron" size={14} className="summary-chevron" /> Termini tecnici della lettura</summary>
          <div className="more-body stack-sm small-text">
            {noRevisionEvent && (
              <p data-testid="live-no-revision-event">Non è indicato un evento specifico che farebbe cambiare questa lettura. È un limite
                della spiegazione disponibile: non significa che la lettura non possa cambiare.</p>
            )}
            <dl className="call-geo">
              <dt>Contesto 1h</dt><dd className="mono">{mv.observed_context ?? "—"}</dd>
              <dt>Fase 15m</dt><dd className="mono">{mv.phase ?? "—"}</dd>
              <dt>Lettura</dt><dd className="mono">{d}{mv.conditional ? " · conditional" : ""} · {mv.table_row}</dd>
              {reasons.length > 0 && <><dt>Motivazione (testo del sistema)</dt><dd className="mono">{reasons.join(" | ")}</dd></>}
              {(mv.counterevidence ?? []).length > 0 && <><dt>Elementi contrari registrati</dt><dd className="mono">{mv.counterevidence.join(" | ")}</dd></>}
              {(mv.blockers ?? []).length > 0 && <><dt>Dati mancanti</dt><dd className="mono">{mv.blockers.join(" | ")}</dd></>}
            </dl>
          </div>
        </details>
      )}
      {v && <p className="muted small-text">Lettura qualitativa, non una probabilità.</p>}
    </section>
  );
}

export function ProposalPanel({ v, onHistory }: { v: LiveView | null; onHistory: (callId: string) => void }) {
  const st = proposalState(v);
  const mv = v?.market_view ?? null;
  const c = v?.call ?? null;
  const available = st.key === "AVAILABLE";
  const d = mv?.expected_direction ?? "UNAVAILABLE";
  const lastTerminal = [...(v?.recent_calls ?? [])].sort((a, b) => (a.terminal_at < b.terminal_at ? 1 : -1))[0];
  const sig = SIGNAL[st.key] ?? SIGNAL.UNKNOWN;
  const notCurrent = c?.presentation === "NOT_CURRENT" || (!!v?.stale_session && !c);
  return (
    <section className="decision" data-testid="live-call" data-state={st.key}>
      <header className="decision-head">
        <div className="eyebrow">Che cosa propone il sistema adesso</div>
        <div className="decision-meta">
          {notCurrent && <span className="sig-chip sig-tech" data-testid="live-call-not-current"><Icon name="cpu" size={13} />
            Sessione non corrente: disponibilità non verificabile</span>}
          {c && !notCurrent && <Badge tone={c.origin === "LIVE" ? "info" : "pending"} icon="cpu">{c.origin === "LIVE" ? "Origine: call live" : "Ricostruita — non operativa"}</Badge>}
          {v && <span className="proposal-updated" data-testid="live-updated">Ultimo aggiornamento: {fmtLocal(v.clock)}</span>}
        </div>
      </header>
      {!v && (
        <div className={cx("persp-state", sig.cls)} data-testid="live-no-view"><Icon name={sig.icon} size={20} /> <span>{st.text}</span></div>
      )}
      {!v && <p className="proposal-note">Avvia l'adviser live per valutare il mercato. Da fermo non viene monitorato nulla.</p>}
      {v && (
        <>
          <CallStrip c={c} t={c ? undefined : lastTerminal} unverified={st.key === "UNVERIFIED"} />
          <p className="small-text muted" data-testid="live-perspectives-note">{PERSPECTIVES}</p>
          <div className="persp-row">
            <div className="persp-title" data-testid="live-new-entry-title">{NO_POSITION}</div>
            <div className="persp-body">
              <div className={cx("persp-state", sig.cls)} data-testid={c ? "live-entry" : "live-no-trade"}>
                <Icon name={sig.icon} size={20} /> <span>{st.text}</span></div>
              {c && st.key === "UNVERIFIED" && (() => {
                const x = unverifiedExplanation(c);
                return (
                  <div className="proposal-consequence persp-consequence" data-testid="live-entry-consequence" data-kind={x.kind}>
                    <b>{x.title}</b><p>{x.body}</p>
                  </div>
                );
              })()}
              {c && <EntryFacts c={c} available={available} />}
            </div>
          </div>
          <div className="persp-row" data-testid="live-call-update">
            <div className="persp-title" data-testid="live-section-following">{FOLLOWING}</div>
            <div className="persp-body">
              {c ? <CallUpdate c={c} v={v} />
                : lastTerminal ? <ConcludedCall v={v} t={lastTerminal} expected={d} />
                : <p className="small-text muted">Nessuna call emessa da seguire in questo momento.</p>}
            </div>
          </div>
        </>
      )}
      {v && (
        <p className="proposal-note">È l'indicazione del sistema, non una tua operazione: l'app non sa se hai aperto posizioni.
          Lo stop è un'indicazione, non un ordine.</p>
      )}

      {v && (
        <details className="more proposal-more" data-testid="live-proposal-details">
          <summary><Icon name="chevron" size={14} className="summary-chevron" /> Approfondimenti
            <span className="summary-hint">motivazioni, dettagli tecnici e cronologia</span></summary>
          <div className="more-body stack-sm">
            {mv && (
              <dl className="call-geo">
                <dt>Lettura</dt><dd className="mono">{d}{mv.conditional ? " · conditional" : ""} · {mv.table_row}</dd>
                <dt>Contesto 1h osservato</dt><dd className="mono">{mv.observed_context}</dd>
                <dt>Fase</dt><dd className="mono">{mv.phase}</dd>
                <dt>Valutazione (UTC)</dt><dd className="mono">{fmtTime(v.clock)}</dd>
              </dl>
            )}
            {(mv?.reasons.length ?? 0) > 0 && (
              <div><div className="adv-section-title">Motivazioni (testo del sistema)</div>
                <ul className="dir-reasons">{mv!.reasons.map((r) => <li key={r}>{r}</li>)}</ul></div>
            )}
            {(mv?.counterevidence.length ?? 0) > 0 && (
              <div><div className="adv-section-title">Controevidenze (testo del sistema)</div>
                <ul className="dir-counter">{mv!.counterevidence.map((r) => <li key={r}>{r}</li>)}</ul></div>
            )}
            {c && (
              <dl className="call-geo" data-testid="live-call-technical">
                <dt>Testo del sistema</dt><dd data-testid="live-guidance">{c.guidance}</dd>
                <dt>Codici registrati</dt><dd className="mono">{c.entry_status}{c.entry_reasons.length ? ` · ${c.entry_reasons.join(", ")}` : ""}</dd>
                <dt>Area strutturale (storico)</dt><dd className="mono">{fmtPrice(c.structural_area[0])} – {fmtPrice(c.structural_area[1])}</dd>
                {!available && c.admissible_bounds && (
                  <><dt>Ultima fascia calcolata (non utilizzabile ora)</dt><dd className="mono">{fmtPrice(c.admissible_bounds[0])} – {fmtPrice(c.admissible_bounds[1])}</dd></>
                )}
                <dt>Famiglia</dt><dd>{c.family} · {c.family_text} · target {humanize(c.target_type)}</dd>
                <dt>Emessa (UTC)</dt><dd className="mono">{fmtTime(c.issued_at)} a {c.issue_reference}</dd>
                <dt>Scadenza (UTC)</dt><dd className="mono">{fmtTime(c.hard_deadline)}</dd>
                <dt>Minuti residui alla valutazione</dt><dd className="mono">{c.remaining_minutes}</dd>
                <dt>Revisione</dt><dd className="mono">r{c.revision}</dd>
              </dl>
            )}
            {c && v.run_id && (
              <button type="button" className="link-btn" onClick={() => onHistory(c.call_id)} data-testid="live-call-history-open">
                Show this call's recorded history (revision r{c.revision})</button>
            )}
            <ScenarioCards v={v} />
          </div>
        </details>
      )}
    </section>
  );
}
