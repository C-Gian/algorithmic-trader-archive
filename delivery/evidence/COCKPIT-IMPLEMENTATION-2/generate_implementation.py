"""IMPLEMENTED second cockpit proposal (chart left with candles, decision panel right): images and per-state checks.

Evidence generator; renders the product UI build in web/dist (no draft patch). The six states are those of the approved
proposal, taken from its own generator (../COCKPIT-VISUAL-PROPOSAL-2/generate_proposal.py, ``states()``): real engine
states of in-memory v0.6 live sessions (mocked services) over the existing MP-005 synthetic tapes, served through the
real ``live_status`` boundary. They come from three independent sessions and are separate states, not one sequence.

Every state is checked at 1440, 1024 and 390 px against the served view: authoritative state, direction chip and
colours, admissible band only when AVAILABLE, published levels in Italian notation, candles = the view's minutes in
time order, non-overlapping level labels, no horizontal overflow, the method badge not cut, the concluded call kept
apart from the current reading. Desktop images for all six states, plus 1024 and 390 for states 2 and 5.

Usage (disposable PostgreSQL, product UI built):
    ALGOTRADER_TEST_DATABASE_URL=postgresql://... uv run python delivery/evidence/COCKPIT-IMPLEMENTATION-2/generate_implementation.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "proposal2_gen", ROOT / "delivery" / "evidence" / "COCKPIT-VISUAL-PROPOSAL-2" / "generate_proposal.py")
pg = importlib.util.module_from_spec(_spec)
sys.modules["proposal2_gen"] = pg
_spec.loader.exec_module(pg)  # also loads the episode generator and puts tests/ and tests/e2e on sys.path

import psycopg  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402
from psycopg import sql  # noqa: E402
from test_ui_smoke import Stack, it_price, no_horizontal_overflow  # noqa: E402

from algotrader import db  # noqa: E402

ep = pg.ep
VIEWPORT = {"width": 1440, "height": 1000}
WIDTHS = (1440, 1024, 390)
EXTRA_IMAGES = {"2-long-disponibile", "5-ingresso-chiuso-tesi-aperta"}
LABEL_CSS = """.live-cockpit::before { content: "Dimostrazione sintetica — cockpit implementato (dati di test, non mercato reale)";
  align-self: flex-start; padding: 4px 12px; border-radius: 999px; border: 1px solid currentColor; font-size: 13px;
  font-weight: 700; letter-spacing: .02em; opacity: .9; }"""
INFO, POS, NEG, WARN = "rgb(108, 182, 224)", "rgb(67, 200, 144)", "rgb(240, 116, 112)", "rgb(241, 154, 85)"
LABELS = """svg => [...svg.querySelectorAll('[data-testid=live-chart-label]')].map(t => { const r = t.getBBox();
  return [r.y, r.y + r.height]; }).sort((a, b) => a[0] - b[0])"""
CANDLES = "svg => [...svg.querySelectorAll('g.candle')].map(g => [g.dataset.t, g.dataset.o, g.dataset.h, g.dataset.l, g.dataset.c])"


def check(page, r: dict, width: int) -> dict:
    v = r["moment"]["view"]
    c = v["call"]
    panel = page.get_by_test_id("live-call")
    # this state's own view is rendered (two consecutive states can share data-state): its clock and last minute
    as_of = re.sub(r"(\.\d+)?(Z|\+00:00)$", " UTC", v["clock"].replace("T", " "))
    expect(page.get_by_test_id("live-price")).to_contain_text(f"as of {as_of}", timeout=15_000)
    expect(page.locator("[data-testid=live-chart] g.candle").last).to_have_attribute("data-t", v["chart"]["minutes"][-1]["t"])
    expect(panel).to_have_attribute("data-state", r["state"], timeout=15_000)
    assert no_horizontal_overflow(page), (r["name"], width)
    badge = page.get_by_test_id("live-session-method")
    assert badge.evaluate("b => b.scrollWidth <= b.clientWidth + 1 && b.getBoundingClientRect().right <= "
                          "document.documentElement.clientWidth"), (r["name"], width, "method badge cut")
    chart, dec = page.get_by_test_id("live-price").bounding_box(), panel.bounding_box()
    assert (chart["x"] + chart["width"] <= dec["x"]) if width == 1440 else (dec["y"] + dec["height"] <= chart["y"])
    chip = page.get_by_test_id("live-call-direction")
    state = page.locator("[data-testid=live-entry], [data-testid=live-no-trade]")
    expect(state.locator("svg")).to_have_count(1)
    if c:
        arrow = "▲" if c["direction"] == "LONG" else "▼"
        expect(chip).to_have_text(f"{arrow} {c['direction']}")
        expect(chip).to_have_css("background-color", POS if c["direction"] == "LONG" else NEG)
        expect(page.get_by_test_id("live-target")).to_have_text(it_price(c["target"]))
        expect(page.get_by_test_id("live-stop-guidance")).to_have_text(it_price(c["stop"]))
        fill = {"AVAILABLE": INFO, "UNVERIFIED": WARN}.get(r["state"])
        if fill:
            expect(state).to_have_css("background-color", fill)
        else:
            expect(state).not_to_have_css("background-color", INFO)
    available = r["state"] == "AVAILABLE"
    expect(page.get_by_test_id("live-admissible")).to_have_count(1 if available else 0)
    expect(page.locator(".band-admissible")).to_have_count(1 if available else 0)
    if available:
        lo, hi = c["admissible_bounds"]
        expect(page.get_by_test_id("live-admissible")).to_have_text(f"{it_price(lo)} – {it_price(hi)}")
    else:
        expect(page.locator(".sig-avail")).to_have_count(0)
    if r["state"] == "UNVERIFIED":
        expect(page.get_by_test_id("live-entry-consequence")).to_have_attribute("data-kind", "QUOTE")
    if r["name"].startswith("6-"):  # the concluded call, apart from the current reading
        expect(chip).to_have_text("▲ LONG")
        expect(page.get_by_test_id("live-call-identity")).to_contain_text("Conclusa — target raggiunto")
        expect(page.get_by_test_id("live-concluded-guidance")).to_have_attribute("data-kind", "TARGET_REACHED", timeout=15_000)
        expect(page.get_by_test_id("live-concluded-separation")).to_contain_text("non prolunga questa call")
        expect(page.get_by_test_id("live-expected")).to_have_text("Rialzo")
    if r["name"].startswith("5-"):
        expect(page.get_by_test_id("live-call-guidance")).to_have_text(
            "Il sistema indica di mantenere l'operazione con stop 99.700 e target 100.700.")
    svg = page.get_by_test_id("live-chart")
    minutes = v["chart"]["minutes"]
    got = svg.evaluate(CANDLES)
    want = [[m["t"], m["o"], m["h"], m["l"], m["c"]] for m in minutes]
    assert got == want, (r["name"], width)
    boxes = svg.evaluate(LABELS)
    assert all(a[1] <= b[0] + 0.5 for a, b in zip(boxes, boxes[1:])), (r["name"], boxes)
    return {"state": r["state"], "width": width, "candles": len(minutes), "level_labels": len(boxes)}


def main() -> None:
    rows = pg.states()
    admin = os.environ["ALGOTRADER_TEST_DATABASE_URL"]
    name = f"algotrader_impl2_{uuid.uuid4().hex[:10]}"
    with psycopg.connect(admin, autocommit=True) as c:
        c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    info = psycopg.conninfo.conninfo_to_dict(admin)
    info["dbname"] = name
    url = psycopg.conninfo.make_conninfo(**info)
    db.migrate(url)
    seen = set()
    for r in rows:
        if r["run_id"] not in seen:
            ep.persist_journal(url, r["run_id"], r["journal"])
            seen.add(r["run_id"])
    tmp = Path(tempfile.mkdtemp(prefix="cockpit-impl2-"))
    stack = Stack(url, tmp / "artifacts", tmp)
    current = {"body": ep.status_json(rows[0]["moment"], rows[0]["journal"])}
    shots, checks, errors = [], [], []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for width in WIDTHS:
                page = b.new_context(viewport={"width": width, "height": VIEWPORT["height"]},
                                     timezone_id="Europe/Rome").new_page()
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.route("**/api/adviser/live", lambda r: r.fulfill(status=200, body=current["body"],
                                                                      headers={"content-type": "application/json"}))
                page.goto(f"{stack.base}/#market")
                page.add_style_tag(content=LABEL_CSS)
                for r in rows:
                    current["body"] = ep.status_json(r["moment"], r["journal"])
                    checks.append({"name": r["name"], **check(page, r, width)})
                    if width != 1440 and r["name"] not in EXTRA_IMAGES:
                        continue
                    page.wait_for_timeout(500)
                    page.evaluate("() => window.scrollTo(0, 0)")
                    box = page.get_by_test_id("live-cockpit").bounding_box()
                    fname = f"{r['name']}{'' if width == 1440 else f'-{width}'}.png"
                    page.screenshot(path=str(OUT / fname), full_page=True,
                                    clip={"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]})
                    shots.append(fname)
                page.context.close()
            b.close()
    finally:
        stack.stop()
        with psycopg.connect(admin, autocommit=True) as c:
            c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(name)))
    assert not errors, errors
    facts = {"viewport": VIEWPORT, "widths": list(WIDTHS), "screenshots": shots, "checks": checks,
             "states": [{k: r[k] for k in ("name", "state", "run_id", "clock", "call", "recent", "expected")} for r in rows]}
    (OUT / "implementation-states.json").write_text(json.dumps(facts, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"screenshots": shots, "checks": len(checks)}, indent=1))


if __name__ == "__main__":
    main()
