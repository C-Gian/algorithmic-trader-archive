import { useMemo, useState } from "react";
import {
  AdviserMethod, adviserApi, Lens, LiveStatus, LiveView, METHOD_STATUS, METHOD_TEXT,
  METHODS, reasonText, THESIS_TEXT,
} from "../adviser";
import { fmtPrice, fmtRecorded, fmtTime, humanize } from "../lib/format";
import { usePoll } from "../lib/usePoll";
import { Icon } from "../ui/Icon";
import { Badge, Button, Card, cx, Mono, Notice, Tone } from "../ui/primitives";
import { HistoryKey, LiveCallHistory } from "./LiveCallHistory";
import { MarketReading, ProposalPanel } from "./LiveProposal";
import { useCopyFeedback } from "./replay/MarketReplay";

// Home live cockpit (WP-009): the Owner starts/stops the local live adviser here. Every value comes from the committed
// live session view (/api/adviser/live); nothing is computed in the browser. Stopped means nothing is monitored and no
// alert is produced. Advice is for a human decision only: no orders, size, leverage or account.

// Colour map: blue = a ready technical state (labelled "Sessione"), amber = attention, grey = waiting/stopped;
// green/red are kept for direction and candles only.
const STATE_TONE: Record<string, Tone> = {
  LIVE: "info", WARMING_UP: "neutral", RECONSTRUCTING: "neutral", STARTING: "neutral", DISCONNECTED: "warn", UNRESPONSIVE: "warn",
  STOPPED: "neutral", FAILED: "warn",
};
const STATE_TEXT: Record<string, string> = {
  LIVE: "Live", WARMING_UP: "Warming up", RECONSTRUCTING: "Catching up", STARTING: "Starting",
  DISCONNECTED: "Disconnected", UNRESPONSIVE: "Not responding", STOPPED: "Stopped", FAILED: "Failed",
};

const HM = new Intl.DateTimeFormat("it-IT", { hour: "2-digit", minute: "2-digit" });

type LevelLine = { y: number; value: string; label: string; cls: string };

/** Vertical positions for the right-hand level labels: each label starts at its own line, then labels are pushed apart
 * (down, then back up from the bottom edge) so no two label blocks overlap and none leaves the chart. A label that moves
 * keeps a leader to its own line. Block height grows with the merged names of coincident levels. */
export function placeLabels(py: number[], lines: number[], minY: number, maxY: number, gap = 15, lineH = 12): number[] {
  const order = py.map((_, i) => i).sort((a, b) => py[a] - py[b]);
  const h = (i: number) => gap + lineH * (lines[i] - 1);
  const ty = py.slice();
  for (let k = 0; k < order.length; k++) {
    const i = order[k];
    ty[i] = Math.max(ty[i], minY, k ? ty[order[k - 1]] + h(order[k - 1]) : minY);
  }
  for (let k = order.length - 1; k >= 0; k--) {
    const i = order[k];
    const limit = k === order.length - 1 ? maxY - h(i) + gap : ty[order[k + 1]] - h(i);
    ty[i] = Math.min(ty[i], limit);
  }
  return ty;
}

// The cockpit price chart: the same component and the same view.chart.minutes fields (o/h/l/c/t), drawn as candles.
// Candle colour = that minute's own move; levels are neutral lines told apart by pattern and label, never by green/red.
function PriceChart({ v }: { v: LiveView | null }) {
  const bars = v?.chart?.minutes ?? [];
  const call = v?.call ?? null;
  const lv = v?.levels ?? {};
  const W = 440;
  const H = 300;
  const PL = 4;
  const PR = 142;
  const shapes = useMemo(() => {
    if (bars.length < 2) return null;
    const raw: LevelLine[] = [];
    const add = (val: string | null | undefined, label: string, cls: string) => {
      if (val) raw.push({ y: Number(val), value: val, label, cls });
    };
    if (call) {
      add(call.target, "target", "lvl-target");
      add(call.stop, "stop", "lvl-stop");
    }
    add(lv.nearest_resistance_near_edge, "resistenza", "lvl-res");
    add(lv.nearest_support_near_edge, "supporto", "lvl-sup");
    add(lv.box_low, "box min", "lvl-box");
    add(lv.box_up, "box max", "lvl-box");
    // coincident levels share one label ("target · resistenza") instead of overprinting
    const lines: LevelLine[] = [];
    for (const l of raw) {
      const same = lines.find((x) => x.y === l.y);
      if (same) same.label = `${same.label} · ${l.label}`;
      else lines.push({ ...l });
    }
    const all = [...bars.flatMap((b) => [Number(b.h), Number(b.l)]), ...lines.map((l) => l.y),
                 ...(call ? call.structural_area.map(Number) : [])];
    const lo = Math.min(...all);
    const hi = Math.max(...all);
    const pad = (hi - lo) * 0.06 || 1;
    const top = 10;
    const bottom = H - 26;
    const y = (p: number) => bottom - ((p - (lo - pad)) / (hi - lo + 2 * pad)) * (bottom - top);
    const step = (W - PL - PR) / bars.length;
    const x = (i: number) => PL + step * (i + 0.5);
    const bw = Math.max(1, Math.min(9, step * 0.62));
    const candles = bars.map((b, i) => {
      const o = Number(b.o);
      const c = Number(b.c);
      return { x: x(i), hi: y(Number(b.h)), lo: y(Number(b.l)), top: y(Math.max(o, c)), bot: y(Math.min(o, c)),
               up: c >= o, b };
    });
    const area = call ? { y1: y(Number(call.structural_area[1])), y2: y(Number(call.structural_area[0])) } : null;
    // the admissible band is drawn only while the backend says the entry is AVAILABLE (never as a usable-looking past level)
    const adm = call?.admissible_bounds && call.entry_status === "AVAILABLE" && call.presentation !== "NOT_CURRENT" ? { y1: y(Number(call.admissible_bounds[1])), y2: y(Number(call.admissible_bounds[0])) } : null;
    // labels pushed apart so two close levels stay readable; each label keeps a leader to its own line
    const pys = lines.map((l) => y(l.y));
    const tys = placeLabels(pys, lines.map((l) => l.label.split(" · ").length), 8, H - 8);
    const placed = lines.map((l, i) => ({ ...l, py: pys[i], ty: tys[i] }));
    const ticks = [0, Math.floor((bars.length - 1) / 2), bars.length - 1].map((i) => ({ x: x(i), t: HM.format(new Date(bars[i].t)) }));
    const lastC = Number(bars[bars.length - 1].c);
    return { candles, lines: placed, area, adm, bw, ticks, last: { y: y(lastC), c: lastC }, bottom };
  }, [bars, call, lv]);
  if (!shapes) {
    return <div className="chart-empty" data-testid="live-chart-empty">No live price yet — start the adviser to load the
      latest complete minutes.</div>;
  }
  const xr = W - PR;
  return (
    <>
      <svg viewBox={`0 0 ${W} ${H}`} className="live-chart is-candles" role="img"
           aria-label="BTC traded price, last complete minutes, as 1-minute candles" data-testid="live-chart">
        {shapes.area && <rect x={PL} width={xr - PL} y={shapes.area.y1} height={Math.max(1, shapes.area.y2 - shapes.area.y1)}
                              className="band-area"><title>area strutturale della call (storico)</title></rect>}
        {shapes.adm && (
          <g className="band-admissible-g">
            <rect x={PL} width={xr - PL} y={shapes.adm.y1} height={Math.max(2, shapes.adm.y2 - shapes.adm.y1)}
                  className="band-admissible"><title>fascia d'ingresso ammessa ora</title></rect>
          </g>
        )}
        {shapes.candles.map((k, i) => (
          <g key={i} className={cx("candle", k.up ? "up" : "down")} data-t={k.b.t} data-o={k.b.o} data-h={k.b.h} data-l={k.b.l} data-c={k.b.c}>
            <line className="wick" x1={k.x} x2={k.x} y1={k.hi} y2={k.lo} />
            <rect className="body" x={k.x - shapes.bw / 2} width={shapes.bw} y={k.top} height={Math.max(1, k.bot - k.top)} />
          </g>
        ))}
        {shapes.lines.map((l) => (
          <g key={l.label + l.y} className={cx("lvl", l.cls)} data-testid="live-chart-level" data-value={l.value}>
            <line x1={PL} x2={xr} y1={l.py} y2={l.py} />
            {Math.abs(l.ty - l.py) > 1 && <line className="leader" x1={xr} x2={xr + 6} y1={l.py} y2={l.ty} />}
            <text x={xr + 8} y={l.ty + 4} data-testid="live-chart-label">{l.label.split(" · ").map((n, i) => (
              <tspan key={n} x={xr + 8} dy={i ? 12 : 0}>{i ? `= ${n}` : `${n} ${fmtPrice(l.value)}`}</tspan>))}</text>
          </g>
        ))}
        {shapes.adm && (  // drawn over the candles so the label stays readable
          <text x={PL + 4} y={Math.max(12, shapes.adm.y1 - 4)} className="band-label">fascia ammessa ora</text>
        )}
        <g className="last-tag">
          <line x1={PL} x2={xr} y1={shapes.last.y} y2={shapes.last.y} />
        </g>
        <line x1={PL} x2={xr} y1={shapes.bottom} y2={shapes.bottom} className="axis" />
        {shapes.ticks.map((t, i) => (
          <text key={i} x={t.x} y={shapes.bottom + 16} className="tick" textAnchor={i === 0 ? "start" : i === 2 ? "end" : "middle"}>{t.t}</text>
        ))}
      </svg>
      <ul className="chart-legend" data-testid="live-chart-legend">
        <li><span className="lg-k lg-up" aria-hidden /> <span className="lg-k lg-down" aria-hidden /> candela a 1 minuto: verde vuota
          = chiusura sopra l'apertura, rossa piena = sotto (movimento di quel minuto, non la direzione della call)</li>
        <li><span className="lg-line lg-solid" aria-hidden /> target e stop della call (linee piene, con etichetta)</li>
        <li><span className="lg-line lg-dash" aria-hidden /> supporto / resistenza / box (tratteggio)</li>
        <li><span className="lg-band lg-area" aria-hidden /> area strutturale della call</li>
        {shapes.adm && <li><span className="lg-band lg-adm" aria-hidden /> fascia d'ingresso ammessa ora (solo mentre l'ingresso è disponibile)</li>}
        <li>Asse orizzontale: ora locale dei minuti completi.</li>
      </ul>
    </>
  );
}

function lensText(l: Lens): string {
  if (l.result === null || l.result === undefined) return "unavailable";
  if (typeof l.result === "object") {
    return Object.entries(l.result as Record<string, unknown>).map(([k, v]) => `${humanize(k)} ${String(v)}`).join(" · ");
  }
  return humanize(String(l.result));
}

function LensCard({ l }: { l: Lens }) {
  const st = String(l.status);
  const tone: Tone = st === "READY" || st === "LIVE_QUOTED" || st === "HISTORICAL_BASE" ? "info"
    : st === "UNAVAILABLE" || st === "STALE" ? "warn" : st === "LIMITED" || st.includes("UNKNOWN") || st === "NOT_COVERED" ? "pending" : "neutral";
  return (
    <div className="lens-card" data-testid={`lens-${l.lens}`}>
      <div className="lens-top">
        <span className="lens-name">{l.name}</span>
        <Badge tone={tone} icon={tone === "info" ? "cpu" : undefined}>{humanize(st)}</Badge>
      </div>
      <div className="lens-result">{lensText(l)}</div>
      <div className="lens-role">{l.role}</div>
      {l.since && <div className="lens-since mono">since {fmtTime(l.since)}</div>}
    </div>
  );
}

// A stored alert is a past event: its headline describes, in the past tense, what the recorded change type was; the
// guidance text frozen at that revision stays readable only as history. Current availability is never read from here.
const ALERT_EVENT_IT: Record<string, string> = {
  NEW_CALL: "Il sistema ha emesso una nuova call.",
  ENTRY_REOPENED: "Il sistema ha segnalato che l'ingresso era di nuovo disponibile.",
  ENTRY_WITHDRAWN: "Il sistema ha segnalato che l'ingresso non era più disponibile.",
  ENTRY_UNVERIFIED: "Il sistema ha segnalato che la disponibilità dell'ingresso non era confermabile.",
  TERMINAL: "Il sistema ha segnalato la conclusione della call.",
};
const CURRENT_IS_IN_PANEL = "La disponibilità attuale dell'ingresso si legge nel riquadro principale «Che cosa propone il "
  + "sistema adesso», che riporta lo stato attuale del sistema.";

function HistoricalAlert({ a }: { a: LiveStatus["alerts"][number] }) {
  return (
    <div className="hist-alert" data-testid="historical-alert" data-change-type={a.change_type} data-alert-key={a.alert_key}>
      <span className="hist-alert-time mono small-text" data-testid="alert-time">{fmtRecorded(a.created_at)}</span>
      <span className="hist-alert-event" data-testid="alert-event">
        {ALERT_EVENT_IT[a.change_type] ?? `Il sistema ha registrato un cambiamento (${humanize(a.change_type)}).`}</span>
      <details className="hist-alert-recorded" data-testid="alert-recorded">
        <summary>Testo registrato a quell'ora</summary>
        <p className="hist-alert-text" data-testid="alert-recorded-text">{a.summary}</p>
        <p className="muted small-text" data-testid="alert-recorded-note">Fasce d'ingresso, livelli e scadenze in questo
          testo si riferiscono a quell'evento passato: non indicano un ingresso utilizzabile adesso.</p>
      </details>
    </div>
  );
}

function Timeline({ st, onHistory }: { st: LiveStatus; onHistory: (callId: string) => void }) {
  const v = st.view;
  const items: { at: string; kind: string; text: string; alert: LiveStatus["alerts"][number] | null; callId?: string; dir?: string }[] = [
    ...st.alerts.map((a) => ({ at: a.created_at, kind: humanize(a.change_type), text: a.summary, alert: a })),
    ...(v?.recent_calls ?? []).map((c) => ({ at: c.terminal_at, kind: `${c.family} ${THESIS_TEXT[c.terminal] ?? c.terminal}`,
                                             text: reasonText(c.reason), alert: null, callId: c.call_id, dir: c.direction })),
    ...(v?.notes ?? []).slice(-6).map((n) => ({ at: n.at, kind: humanize(n.event), text: "", alert: null })),
  ].sort((a, b) => (a.at < b.at ? 1 : -1)).slice(0, 14);
  if (!items.length) return <p className="muted small-text">No material change yet.</p>;
  return (
    <>
      {items.some((x) => x.alert) && (
        <p className="muted small-text alerts-pointer" data-testid="timeline-current-pointer">Gli avvisi sono eventi registrati nel passato.
          {" "}{CURRENT_IS_IN_PANEL}</p>
      )}
      <ol className="change-timeline" data-testid="live-timeline">
        {items.map((x, i) => (
          <li key={i} className={cx(x.alert && "tl-alert", x.alert && !x.alert.acknowledged && "is-new")}>
            {x.alert ? <HistoricalAlert a={x.alert} /> : (
              <>
                <span className="mono small-text">{fmtTime(x.at).slice(11, 19)}</span>
                <span className="tl-kind">{x.dir && <span className={cx("tl-dir", x.dir === "LONG" ? "dir-long" : "dir-short")}>
                  {x.dir === "LONG" ? "▲" : "▼"} {x.dir}</span>} {x.kind}</span>
                <span className="tl-text">{x.text}</span>
              </>
            )}
            {x.alert && !x.alert.acknowledged && (
              <button type="button" className="link-btn" onClick={() => void adviserApi.ack(x.alert!.alert_key)}>dismiss</button>
            )}
            {x.callId && v?.run_id && (
              <button type="button" className="link-btn" onClick={() => onHistory(x.callId!)}
                      data-testid="timeline-call-history-open">history</button>
            )}
          </li>
        ))}
      </ol>
    </>
  );
}

export function LiveCockpit() {
  const poll = usePoll(adviserApi.live, 1500);
  const st = poll.data;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, runCopy] = useCopyFeedback();
  // WP-011: the method is chosen explicitly before Start; a running session keeps its pinned method
  const [method, setMethod] = useState<AdviserMethod>("v0.2");
  const v = st?.view && st.view.chart ? st.view : null;
  const state = st?.state ?? "STOPPED";
  const running = !!st?.running;
  const act = async (fn: () => Promise<LiveStatus>) => {
    setBusy(true);
    try {
      await fn();
      await poll.refresh();
      setError(null);
    } catch (e) {
      setError((e as Error).message.replace(/^\d+ /, ""));
    } finally {
      setBusy(false);
    }
  };
  const copy = () => void runCopy(() => adviserApi.analysis());
  // the history of one call, fixed to the run + call it was opened from (never re-pointed at a newer call/session)
  const [history, setHistory] = useState<HistoryKey | null>(null);
  const openHistory = (callId: string) => {
    if (!v?.run_id) return;
    setHistory({ runId: v.run_id, callId, sessionId: st?.session?.session_id ?? null });
    window.setTimeout(() => document.querySelector("[data-testid=live-call-history]")?.scrollIntoView({ block: "nearest" }), 0);
  };
  const newAlerts = (st?.alerts ?? []).filter((a) => !a.acknowledged);
  return (
    <section className="live-cockpit" data-testid="live-cockpit">
      <div className="live-bar">
        <div className="live-bar-main">
          <span className="tech-label">Sessione</span>
          <Badge tone={STATE_TONE[state] ?? "neutral"} dot testid="live-state">{STATE_TEXT[state] ?? humanize(state)}</Badge>
          <span className="live-msg" data-testid="live-message">{st?.message ?? "Loading…"}</span>
          {v?.last_receipt && <span className="muted small-text mono">last receipt {fmtTime(v.last_receipt)}</span>}
          {st?.session && <Badge tone="neutral" className="method-badge" testid="live-session-method">{METHOD_TEXT[st.session.method ?? "v0.2"] ?? st.session.method}</Badge>}
        </div>
        <div className="live-bar-actions">
          {running ? (
            <>
              <Button variant="secondary" icon="refresh" onClick={() => act(adviserApi.reassess)} disabled={busy}
                      data-testid="live-reassess" title="Run the current assessment now (never rewrites history)">Reassess now</Button>
              <Button variant="secondary" icon="stop" onClick={() => act(adviserApi.stop)} disabled={busy || !!st?.session?.stop_requested}
                      data-testid="live-stop-button">{st?.session?.stop_requested ? "Stopping…" : "Stop live adviser"}</Button>
            </>
          ) : (
            <>
              <label className="small-text live-method" data-testid="live-method">
                <span>Method</span>
                <select className="control" value={method}
                        onChange={(e) => setMethod(e.target.value as AdviserMethod)}
                        data-testid="live-method-select" disabled={busy}>
                  {METHODS.map((m) => (
                    <option key={m} value={m}>{METHOD_TEXT[m]} ({METHOD_STATUS[m].text.toLowerCase()})</option>))}
                </select>
              </label>
              <Button icon="play" onClick={() => act(() => adviserApi.start(method))} disabled={busy} data-testid="live-start"
                      className="btn-lg">Start live adviser</Button>
            </>
          )}
          <Button variant="secondary" icon={copied === "copied" ? "check" : "copy"} onClick={copy} data-testid="copy-analysis">
            {copied === "copied" ? "Copied" : copied === "copying" ? "Copying…" : copied === "error" ? "Copy failed"
              : "Copy analysis for chat"}</Button>
        </div>
      </div>
      {error && <Notice tone="warn" title="Could not change the live adviser">{error}</Notice>}
      {newAlerts.length > 0 && (
        <Notice tone="neutral" icon="pulse" testid="live-alerts"
                title={newAlerts.length > 1 ? `${newAlerts.length} avvisi registrati non ancora letti`
                  : "1 avviso registrato non ancora letto"}>
          <p className="small-text alerts-pointer" data-testid="alerts-current-pointer">Sono eventi passati, mostrati con l'ora in cui
            sono stati registrati. {CURRENT_IS_IN_PANEL}</p>
          {newAlerts.slice(0, 3).map((a) => <HistoricalAlert key={a.alert_key} a={a} />)}
        </Notice>
      )}
      {v?.stale_session && (
        <Notice tone="warn" title={state === "STOPPED" ? "Stopped" : "Not current advice"} testid="live-not-current">
          {state === "STOPPED" ? "The last view below is from the stopped session and is not current advice."
            : `The session is ${humanize(state).toLowerCase()}: the view below is not current and no entry is presented as usable now.`}
        </Notice>
      )}
      <div className="cockpit-main">
        <div className="cockpit-chart">
          <Card title="BTC price · last complete minutes" icon="market" testid="live-price"
                eyebrow={v?.clock ? `as of ${fmtTime(v.clock)} · ${v.origin === "LIVE" ? "live receipts" : "reconstructed history"}` : "no data yet"}
                actions={<Badge tone={v?.origin === "LIVE" ? "info" : "pending"} icon="cpu">{v?.origin === "LIVE" ? "Dati LIVE" : "NOT LIVE"}</Badge>}>
            <PriceChart v={v} />
          </Card>
          <MarketReading v={v} />
        </div>
        <div className="cockpit-decision">
          <ProposalPanel v={v} onHistory={openHistory} />
        </div>
      </div>
      {history && (
        <LiveCallHistory key={`${history.runId}|${history.callId}`} sel={history} view={v}
                         sessionId={st?.session?.session_id ?? null} onClose={() => setHistory(null)} />
      )}
      <div className="cockpit-lower">
        <Card title="What changed" icon="pulse" testid="live-changes">
          {st ? <Timeline st={st} onHistory={openHistory} /> : null}
        </Card>
        <div className="lens-grid" data-testid="live-lenses">
          {(v?.lenses ?? []).map((l) => <LensCard key={l.lens} l={l} />)}
          {!v && <p className="muted small-text">Lens results appear once the adviser has assessed the market. Several lenses
            are not majority votes: each has a stated role.</p>}
        </div>
      </div>
      <details className="more" data-testid="live-technical">
        <summary><Icon name="chevron" size={14} className="summary-chevron" /> Technical details
          <span className="summary-hint">identity, readiness, armed scenarios, catch-up and connection</span></summary>
        <div className="more-body">
          {st?.session && (
            <div className="kv-grid">
              <span>Session</span><Mono>{st.session.session_id}</Mono>
              <span>Continuity epoch</span><Mono>{v?.run_id ?? "—"}</Mono>
              <span>Heartbeat age</span><Mono>{st.session.heartbeat_age_seconds?.toFixed(1) ?? "—"} s</Mono>
              <span>Catch-up</span><Mono>{JSON.stringify(st.session.progress)}</Mono>
              <span>Connection</span><Mono>{JSON.stringify(st.session.connection)}</Mono>
              <span>Identity</span><Mono>{String((st.session.identity as Record<string, string> | null)?.identity_sha256 ?? "—").slice(0, 16)}</Mono>
            </div>
          )}
          <ul className="check-list">
            {(v?.readiness ?? []).map((r) => <li key={r.name}><span className="mono">{r.name}</span> <Badge tone={r.status === "READY" ? "info" : "warn"}>{r.status}</Badge> <span className="muted">{r.latest_ref ?? ""}</span></li>)}
          </ul>
          {(v?.attempts ?? []).length > 0 && (
            <ul className="check-list" data-testid="live-attempts">
              {v!.attempts.map((a) => <li key={a.attempt_id}><span className="mono">{a.attempt_id.slice(0, 28)}</span> {a.family} {a.direction} {humanize(a.status)} trigger {a.trigger_level ?? "—"} invalidation {a.invalidation_level ?? "—"}</li>)}
            </ul>
          )}
          <p className="muted small-text">{st?.notice}</p>
        </div>
      </details>
    </section>
  );
}
