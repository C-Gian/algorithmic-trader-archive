"""Live cockpit arrangement and palette (E2E, synthetic payloads only): the risks introduced by the approved second visual
proposal. Chart left / decision panel right on desktop, panel first at 1024 and 390 px, no horizontal overflow and the
method badge never cut; a SHORT available entry (filled red direction chip + filled blue availability) is told apart
from an action error (amber, never red) and a concluded LONG call (dashed grey chip, no availability block) from an
available entry; the candles keep the OHLC values, the time order and the levels of ``view.chart.minutes`` and
``view.call``/``view.levels``; level labels never overlap; state texts keep their symbol and readable contrast."""

from __future__ import annotations

import json
import re

import pytest
from playwright.sync_api import expect

from test_live_call_history_e2e import call_view, live
from test_ui_smoke import browser, evidence_dir, no_horizontal_overflow, stack  # noqa: F401

pytestmark = [pytest.mark.e2e, pytest.mark.db]

INFO, POS, NEG, WARN = "rgb(108, 182, 224)", "rgb(67, 200, 144)", "rgb(240, 116, 112)", "rgb(241, 154, 85)"

# minutes with real candles (rising and falling), one minute apart, and levels close enough to collide
MINUTES = [{"t": f"2026-10-10T09:{i:02d}:00Z", "o": o, "h": h, "l": lo, "c": c} for i, (o, h, lo, c) in enumerate([
    ("100000.0", "100120.0", "99950.0", "100100.0"), ("100100.0", "100180.0", "100020.0", "100040.0"),
    ("100040.0", "100260.0", "100030.0", "100250.0"), ("100250.0", "100300.0", "100100.0", "100120.5"),
    ("100120.5", "100400.0", "100110.0", "100380.0"), ("100380.0", "100390.0", "100200.0", "100210.0"),
    ("100210.0", "100500.0", "100200.0", "100480.0"), ("100480.0", "100560.0", "100300.0", "100320.0"),
    ("100320.0", "100330.0", "100000.0", "100010.0"), ("100010.0", "100060.0", "99980.0", "100030.0"),
])]
LEVELS = {"nearest_resistance_near_edge": "100700.0", "nearest_support_near_edge": "99712.0",
          "box_low": "99800.0", "box_up": "100690.0"}


def long_available(entry: str = "AVAILABLE") -> dict:
    c = call_view("c1", 1, entry=entry)
    c.update(target="100700.0", stop="99700.0", structural_area=["99900.0", "100050.0"],
             admissible_bounds=["99950.0", "100049.9"])
    st = live("live-R1", "S1", c)
    st["view"].update(levels=LEVELS, chart={"minutes": MINUTES, "m15": []})
    return st


def short_available() -> dict:
    c = call_view("c2", 1)
    c.update(direction="SHORT", target="99300.0", stop="100300.0", structural_area=["99950.0", "100100.0"],
             admissible_bounds=["99960.0", "100090.0"])
    st = live("live-R1", "S1", c)
    st["view"]["market_view"]["expected_direction"] = "DOWN"
    st["view"]["chart"] = {"minutes": MINUTES, "m15": []}
    return st


def long_concluded() -> dict:
    return live("live-R1", "S1", None, recent=[{"call_id": "c1", "family": "A", "direction": "LONG",
                                                "issued_at": "2026-10-10T09:00:00Z", "terminal": "TARGET_REACHED",
                                                "reason": "CERTIFIED_TARGET_CONTACT", "terminal_at": "2026-10-10T09:40:00Z",
                                                "origin": "LIVE"}])


# WCAG contrast of an element's text on its composited background (ancestors' backgrounds, alpha included)
CONTRAST = """el => {
  const parse = (s) => {
    let m = s.match(/rgba?\\(([^)]+)\\)/);
    if (m) { const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = s.match(/color\\(srgb ([^)]+)\\)/);
    if (m) { const p = m[1].split(/[ /]+/).filter(Boolean).map(Number); return [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1]; }
    return [0, 0, 0, 0];
  };
  const chain = [];
  for (let n = el; n; n = n.parentElement) chain.push(parse(getComputedStyle(n).backgroundColor));
  let bg = [10, 13, 18];
  for (const c of chain.reverse()) bg = bg.map((x, i) => c[3] * c[i] + (1 - c[3]) * x);
  const fg = parse(getComputedStyle(el).color);
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const fgc = fg.slice(0, 3).map((x, i) => fg[3] * x + (1 - fg[3]) * bg[i]);
  const [a, b] = [lum(fgc), lum(bg)].sort((x, y) => y - x);
  return (a + 0.05) / (b + 0.05);
}"""

# geometry of the chart in SVG units, read back from the rendered marks
CHART = """svg => {
  const candles = [...svg.querySelectorAll('g.candle')].map(g => {
    const w = g.querySelector('line.wick'), b = g.querySelector('rect.body');
    return {t: g.dataset.t, o: g.dataset.o, h: g.dataset.h, l: g.dataset.l, c: g.dataset.c, up: g.classList.contains('up'),
            x: +w.getAttribute('x1'), wy1: +w.getAttribute('y1'), wy2: +w.getAttribute('y2'),
            by: +b.getAttribute('y'), bh: +b.getAttribute('height')};
  });
  const levels = [...svg.querySelectorAll('[data-testid=live-chart-level]')].map(g => ({
    value: g.dataset.value, cls: g.getAttribute('class'), y: +g.querySelector('line').getAttribute('y1'),
    label: (() => { const t = g.querySelector('[data-testid=live-chart-label]'); const r = t.getBBox();
                    return {text: t.textContent, y: r.y, h: r.height}; })()}));
  return {candles, levels, height: svg.viewBox.baseVal.height};
}"""


def test_layout_palette_chart_and_widths(stack, browser, evidence_dir):  # noqa: F811
    cur = {"body": long_available()}
    errors: list[str] = []
    for width in (1440, 1024, 390):
        ctx = browser.new_context(viewport={"width": width, "height": 1000}, timezone_id="Europe/Rome")
        page = ctx.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.route("**/api/adviser/live", lambda r: r.fulfill(status=200, body=json.dumps(cur["body"]),
                                                              headers={"content-type": "application/json"}))
        page.route("**/api/adviser/live/reassess", lambda r: r.fulfill(status=409, body=json.dumps(
            {"detail": "synthetic refusal"}), headers={"content-type": "application/json"}))
        panel = page.get_by_test_id("live-call")

        def show(body: dict, state: str) -> None:
            cur["body"] = body
            expect(panel).to_have_attribute("data-state", state, timeout=15_000)

        def check_width(tag: str) -> None:
            assert no_horizontal_overflow(page), (width, tag)
            badge = page.get_by_test_id("live-session-method")
            expect(badge).to_be_visible()
            fits = badge.evaluate("b => b.scrollWidth <= b.clientWidth + 1 && b.getBoundingClientRect().right <= "
                                  "document.documentElement.clientWidth")
            assert fits, (width, tag, "method badge cut")
            chart = page.get_by_test_id("live-price").bounding_box()
            dec = panel.bounding_box()
            if width == 1440:
                assert chart["x"] + chart["width"] <= dec["x"] and chart["width"] < dec["width"], (tag, chart, dec)
            else:  # the decision panel comes first on narrower screens
                assert dec["y"] + dec["height"] <= chart["y"], (width, tag, chart, dec)

        page.goto(f"{stack.base}/#market")

        # LONG available: filled green chip, filled blue availability with its symbol; band shown in the chart
        show(long_available(), "AVAILABLE")
        chip = page.get_by_test_id("live-call-direction")
        expect(chip).to_have_text("▲ LONG")
        expect(chip).to_have_css("background-color", POS)
        entry = page.get_by_test_id("live-entry")
        expect(entry).to_have_text("Ingresso disponibile secondo il sistema")
        expect(entry).to_have_css("background-color", INFO)
        expect(entry.locator("svg")).to_have_count(1)
        expect(page.get_by_test_id("live-admissible")).to_have_text("99.950 – 100.049,9")
        expect(page.get_by_test_id("live-target")).to_have_text("100.700")
        expect(page.get_by_test_id("live-stop-guidance")).to_have_text("99.700")
        expect(page.locator(".band-admissible")).to_have_count(1)
        check_width("long-available")

        if width == 1440:
            g = page.get_by_test_id("live-chart").evaluate(CHART)
            cs = g["candles"]
            # every minute drawn once, in time order left to right, with its own OHLC values and colour
            assert [(c["t"], c["o"], c["h"], c["l"], c["c"]) for c in cs] == [
                (m["t"], m["o"], m["h"], m["l"], m["c"]) for m in MINUTES]
            assert all(a["x"] < b["x"] for a, b in zip(cs, cs[1:]))
            for c in cs:
                assert c["up"] == (float(c["c"]) >= float(c["o"])), c
                assert c["wy1"] <= c["by"] + 0.01 and c["by"] + c["bh"] <= c["wy2"] + 1.01, c  # body inside the wick
            by_h = sorted(cs, key=lambda c: float(c["h"]))
            assert by_h[-1]["wy1"] < by_h[0]["wy1"]  # a higher price is drawn higher
            # levels: the published values, merged when equal, ordered by price on the vertical axis
            lv = g["levels"]
            assert sorted(x["value"] for x in lv) == sorted(["100700.0", "99700.0", "99712.0", "99800.0", "100690.0"])
            merged = next(x for x in lv if x["value"] == "100700.0")
            assert merged["label"]["text"] == "target 100.700= resistenza" and "lvl-target" in merged["cls"]
            by_v = sorted(lv, key=lambda x: float(x["value"]), reverse=True)
            assert all(a["y"] < b["y"] for a, b in zip(by_v, by_v[1:]))
            # labels never overlap and stay inside the chart, even for levels a few points apart
            boxes = sorted((x["label"] for x in lv), key=lambda b: b["y"])
            assert all(a["y"] + a["h"] <= b["y"] + 0.5 for a, b in zip(boxes, boxes[1:])), boxes
            assert boxes[0]["y"] >= 0 and boxes[-1]["y"] + boxes[-1]["h"] <= g["height"], boxes
            expect(page.get_by_test_id("live-chart")).to_contain_text("stop 99.700")
            expect(page.get_by_test_id("live-chart")).to_contain_text("supporto 99.712")
            page.get_by_test_id("live-price").screenshot(path=str(evidence_dir / "layout-chart-levels.png"))

        # SHORT available vs an action error: red only for the direction, blue for availability, amber for the error
        show(short_available(), "AVAILABLE")
        expect(chip).to_have_text("▼ SHORT")
        expect(chip).to_have_css("background-color", NEG)
        expect(entry).to_have_css("background-color", INFO)
        expect(entry).to_have_text("Ingresso disponibile secondo il sistema")
        page.get_by_test_id("live-reassess").click()
        err = page.locator(".notice", has_text="Could not change the live adviser")
        expect(err).to_be_visible()
        expect(err).to_contain_text("synthetic refusal")
        expect(err).to_have_class(re.compile(r"(^| )tone-warn( |$)"))
        expect(err.locator("svg").first).to_have_css("color", WARN)
        expect(page.get_by_test_id("live-stop-button")).not_to_have_css("background-color", NEG)
        check_width("short-available")
        if width == 1440:
            page.get_by_test_id("live-cockpit").screenshot(path=str(evidence_dir / "layout-short-vs-error.png"))
        page.reload()

        # LONG concluded vs available: dashed grey chip and "Conclusa", no availability block, no band
        show(long_concluded(), "WAITING")
        expect(chip).to_have_text("▲ LONG")
        assert chip.evaluate("c => getComputedStyle(c).backgroundColor") in ("rgba(0, 0, 0, 0)", "transparent")
        expect(chip).to_have_css("border-top-style", "dashed")
        expect(page.get_by_test_id("live-call-identity")).to_contain_text("Conclusa — target raggiunto")
        expect(page.locator(".sig-avail")).to_have_count(0)
        expect(page.locator(".band-admissible")).to_have_count(0)
        expect(page.get_by_test_id("live-no-trade")).to_have_text("In attesa — nessun ingresso proposto")
        expect(page.get_by_test_id("live-concluded-separation")).to_contain_text("non prolunga questa call")
        expect(page.get_by_test_id("live-market-reading")).to_contain_text("non dice se entrare")
        check_width("long-concluded")

        # every state text keeps its symbol and a readable contrast (WCAG AA 4.5:1)
        for body, state in ((long_available(), "AVAILABLE"), (long_concluded(), "WAITING"),
                            (long_available("CLOSED"), "CLOSED"), (long_available("UNVERIFIED"), "UNVERIFIED")):
            show(body, state)
            st = page.locator("[data-testid=live-entry], [data-testid=live-no-trade]")
            expect(st.locator("svg")).to_have_count(1)
            for loc in (st, chip, page.get_by_test_id("live-state"), page.get_by_test_id("live-session-method"),
                        page.get_by_test_id("live-expected")):
                r = loc.evaluate(CONTRAST)
                assert r >= 4.5, (width, state, loc, r)
            if state == "UNVERIFIED":
                expect(st).to_have_css("background-color", WARN)
        ctx.close()
    assert not errors, errors
