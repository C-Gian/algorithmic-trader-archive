"""Market-reading box in three linked steps (presentation only, E2E on served payloads).

The recorded states of the Owner use session of 12 October 2026 (saved view and journal records 760/772/776/781,
``delivery/evidence/LIVE-V06-USE-SESSION/reconstruction``) must read: what is observed (1h context, 15m phase), what is
concluded (expected direction and recorded reason, Incerta and Equilibrio kept distinct) and that no condition was
published, with no invented trigger. The already available scenario cases keep their published condition with its
values. Risks covered: field distinction, condition fidelity, missing/unknown data, no false operational condition.
With ``ALGOTRADER_EVIDENCE_DIR`` set, the session states are saved as images labelled RICOSTRUZIONE."""

from __future__ import annotations

import copy
import json

import pytest
from playwright.sync_api import Page, expect

from test_live_proposal_e2e import armed_v02_view, waiting_view
from test_ui_smoke import ROOT, browser, evidence_dir, stack  # noqa: F401

pytestmark = [pytest.mark.e2e, pytest.mark.db]

REC = ROOT / "delivery" / "evidence" / "LIVE-V06-USE-SESSION" / "reconstruction"
NO_SCENARIO = "Non c'è ancora uno scenario attivo. Il sistema non ha pubblicato una condizione specifica da attendere per un ingresso."
NO_EVENT = "Non è indicato un evento specifico che farebbe cambiare questa lettura."
# unsupported wording: invented waits, future sideways promises, operational entry language
FORBIDDEN = ("rottura", "conferme", "lateral", "range", "innesco", "Serve ", "corridoio", "Ingresso disponibile")


def saved() -> dict:
    return json.loads((REC / "saved-live-payload.json").read_text(encoding="utf-8"))


def with_record(seq: int) -> dict:
    for line in (REC / "market-view-records.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["env"]["record_id"] == f"market_view-{seq:08d}":
            p = saved()
            p["view"]["market_view"] = {k: v for k, v in r.items() if k not in ("env", "uncertainty")}
            return p
    raise KeyError(seq)


def with_mv(base: dict, **kw) -> dict:
    p = copy.deepcopy(base)
    p["view"]["market_view"].update(kw)
    return p


def _open(browser, stack, cur: dict) -> Page:  # noqa: F811
    ctx = browser.new_context(viewport={"width": 1600, "height": 1100}, locale="it-IT", timezone_id="Europe/Rome")
    page = ctx.new_page()
    page.route("**/api/adviser/live", lambda r: r.fulfill(status=200, body=json.dumps(cur["body"]),
                                                          headers={"content-type": "application/json"}))
    page.goto(f"{stack.base}/#market")
    return page


def _show(page: Page, cur: dict, body: dict, expected: str) -> None:
    cur["body"] = body
    expect(page.get_by_test_id("live-expected")).to_have_text(expected, timeout=10_000)


def _no_false_condition(box) -> None:
    for w in FORBIDDEN:
        expect(box).not_to_contain_text(w)


def _snapshot(page: Page, evidence_dir, name: str, label: str) -> None:  # noqa: F811
    box = page.get_by_test_id("live-market-reading")
    page.evaluate("""([label]) => {
        document.querySelectorAll('[data-reconstruction-label]').forEach((e) => e.remove());
        const box = document.querySelector('[data-testid="live-market-reading"]');
        const tag = document.createElement('div');
        tag.dataset.reconstructionLabel = '1';
        tag.textContent = label;
        tag.style.cssText = 'border:2px dashed #e0a030;color:#e0a030;padding:6px 10px;margin:0 0 8px;font:600 13px sans-serif';
        box.parentNode.insertBefore(tag, box);
    }""", [label])
    page.get_by_test_id("live-reading-tech").locator("summary").click()
    r = page.evaluate("""() => { const b = document.querySelector('[data-testid="live-market-reading"]');
        const t = b.previousSibling.getBoundingClientRect(), r = b.getBoundingClientRect();
        return {x: Math.min(t.x, r.x) + scrollX, y: t.y + scrollY, w: Math.max(t.width, r.width), h: r.bottom - t.y}; }""")
    page.screenshot(path=str(evidence_dir / f"{name}.png"), full_page=True,
                    clip={"x": r["x"] - 4, "y": r["y"] - 4, "width": r["w"] + 8, "height": r["h"] + 8})
    page.get_by_test_id("live-reading-tech").locator("summary").click()


def test_session_states_read_observation_conclusion_and_no_published_condition(stack, browser, evidence_dir):  # noqa: F811
    cur = {"body": saved()}
    page = _open(browser, stack, cur)
    box = page.get_by_test_id("live-market-reading")
    cases = [
        # (variant, body, expected, context, phase, row, reason, image label)
        ("saved", saved(), "Incerta", "in equilibrio", "transizione", "Nessuna struttura qualificata",
         "Manca il presupposto: non è nato nessuno scenario di impulso (famiglia A) o di box di compressione.",
         "vista salvata della sessione (dopo Stop), market_view = record 781; valida 13:30–13:45 Roma"),
        ("record-760", with_record(760), "Incerta", "in equilibrio", "espansione", "Nessuna struttura qualificata",
         "Manca il presupposto: non è nato nessuno scenario di impulso (famiglia A) o di box di compressione.",
         "vista salvata con market_view = record 760 (ricostruzione parziale); 11:22–12:00 Roma"),
        ("record-772", with_record(772), "Equilibrio", "in equilibrio", "rotazione", "Equilibrio in fase di compressione o rotazione",
         "Contesto a 1 ora in equilibrio con fase di rotazione; nessun box qualificato, quindi nessun limite di prezzo indicato.",
         "vista salvata con market_view = record 772 (ricostruzione parziale); 12:00–12:30 Roma"),
        ("record-776", with_record(776), "Equilibrio", "in equilibrio", "compressione", "Equilibrio in fase di compressione o rotazione",
         "Contesto a 1 ora in equilibrio con fase di compressione; nessun box qualificato, quindi nessun limite di prezzo indicato.",
         "vista salvata con market_view = record 776 (ricostruzione parziale); 12:30–13:30 Roma"),
    ]
    for name, body, exp, ctx, ph, row, reason, label in cases:
        _show(page, cur, body, exp)
        expect(page.get_by_test_id("live-observed-context")).to_contain_text(f"Contesto a 1 ora: {ctx}")
        expect(page.get_by_test_id("live-observed-phase")).to_contain_text(f"Fase a 15 minuti: {ph}")
        expect(page.get_by_test_id("live-direction")).to_contain_text(row)
        expect(page.get_by_test_id("live-reason")).to_have_text(f"Perché: {reason}")
        expect(page.get_by_test_id("live-no-scenario")).to_have_text(NO_SCENARIO)
        expect(page.get_by_test_id("live-no-revision-event")).to_contain_text(NO_EVENT)
        expect(page.get_by_test_id("live-condition")).to_have_count(0)
        _no_false_condition(box)
        # Incerta is never turned into a forecast sideways range; Equilibrio keeps its own conclusion
        expect(page.get_by_test_id("live-conclusion")).to_have_text(
            "Il sistema non indica una direzione: la lettura resta incerta." if exp == "Incerta"
            else "Il sistema legge il mercato in equilibrio: non indica né un rialzo né un ribasso.")
        # MarketView, call and current availability stay apart: the call panel keeps its own waiting state
        expect(page.get_by_test_id("live-no-trade")).to_have_text("In attesa — nessun ingresso proposto")
        if evidence_dir:
            _snapshot(page, evidence_dir, f"market-reading-v2-{name}",
                      f"RICOSTRUZIONE ({name}) — non è la schermata vista dall'Owner. Riquadro aggiornato; {label}")
    page.context.close()


def test_fields_stay_distinct_and_missing_or_unknown_values_are_declared(stack, browser):  # noqa: F811
    cur = {"body": saved()}
    page = _open(browser, stack, cur)
    box = page.get_by_test_id("live-market-reading")
    # observed context and conclusion come from different fields: an UP context does not become an UP reading
    _show(page, cur, with_mv(saved(), observed_context="UP"), "Incerta")
    expect(page.get_by_test_id("live-observed-context")).to_contain_text("Contesto a 1 ora: in rialzo")
    expect(page.get_by_test_id("live-conclusion")).to_have_text("Il sistema non indica una direzione: la lettura resta incerta.")
    # missing / unknown observed values and an unknown reason text are declared, never mapped to a neighbour
    p = with_mv(saved(), phase="SOMETHING_NEW", reasons=["a reason text this build does not know"])
    del p["view"]["market_view"]["observed_context"]
    _show(page, cur, p, "Incerta")
    expect(page.get_by_test_id("live-observed-context")).to_contain_text("non indicato dal sistema")
    expect(page.get_by_test_id("live-observed-phase")).to_contain_text("valore non riconosciuto (SOMETHING_NEW)")
    expect(page.get_by_test_id("live-reason")).to_have_text(
        "La motivazione è registrata solo come testo tecnico (vedi i termini tecnici qui sotto).")
    page.get_by_test_id("live-reading-tech").locator("summary").click()
    expect(page.get_by_test_id("live-reading-tech")).to_contain_text("a reason text this build does not know")
    # an absent scenario list is unknown, not empty: no "no scenario" sentence
    p = saved()
    del p["view"]["scenarios"]
    _show(page, cur, p, "Incerta")
    expect(page.get_by_test_id("live-no-scenario")).to_have_count(0)
    expect(page.get_by_test_id("live-no-condition")).to_have_text(
        "Il sistema non ha pubblicato una condizione specifica da attendere per un ingresso.")
    _no_false_condition(box)
    # a scenario exists without a published condition: only the missing datum is declared
    p = saved()
    p["view"]["scenarios"] = [{"scenario_id": "C-9", "family": "C", "family_text": "x", "direction": "SHORT",
                               "status": "CONFIRMED", "antecedent": "a", "trigger_level": None, "invalidation_level": None,
                               "destination": None, "destination_type": "LANDMARK", "original_expiry": None,
                               "confirmed_at": None, "confirmed_deadline": None, "progress_check_at": None, "owner": None,
                               "discovery_owner": None, "entry_state": "PENDING", "call_id": None}]
    _show(page, cur, p, "Incerta")
    expect(page.get_by_test_id("live-no-scenario")).to_have_count(0)
    expect(page.get_by_test_id("live-waiting-scenario")).to_have_text(
        "Scenario SHORT C (confermato): il sistema non ha pubblicato una condizione specifica per questo scenario.")
    expect(page.get_by_test_id("live-no-revision-event")).to_have_count(0)
    page.context.close()


def test_published_conditions_keep_their_values(stack, browser):  # noqa: F811
    cur = {"body": waiting_view()}
    page = _open(browser, stack, cur)
    # existing cases with a scenario and a published condition (no new episode): values and precision unchanged
    _show(page, cur, waiting_view(), "Rialzo")
    expect(page.get_by_test_id("live-condition")).to_contain_text("ripresa locale")
    expect(page.get_by_test_id("live-scenario-levels")).to_contain_text("99.700")
    expect(page.get_by_test_id("live-no-scenario")).to_have_count(0)
    expect(page.get_by_test_id("live-no-revision-event")).to_have_count(0)
    _show(page, cur, armed_v02_view(), "Ribasso")
    expect(page.get_by_test_id("live-condition")).to_have_text("Serve l'innesco: una chiusura oltre 99.500.")
    expect(page.get_by_test_id("live-no-scenario")).to_have_count(0)
    # a box with a published boundary keeps it exactly (Italian grouping only)
    p = with_mv(saved(), expected_direction="BALANCED", table_row="BALANCED_RANGE", phase="ROTATION",
                reasons=["balanced 1h context in rotation; rotation inside [83293.785, 83568.935]"])
    _show(page, cur, p, "Equilibrio")
    expect(page.get_by_test_id("live-reason")).to_have_text(
        "Perché: Contesto a 1 ora in equilibrio con fase di rotazione; il prezzo ruota dentro il box 83.293,785 – 83.568,935.")
    page.context.close()
