"""Reconstruction of the cockpit box "Lettura attuale del mercato" of the Owner use session (diagnosis only).

Renders the frontend actually served by the Owner stack (build 87322ac, http://127.0.0.1:8000) with the existing E2E
technique (Playwright ``page.route`` on ``/api/adviser/live``). Inputs, saved beside this script:
- ``saved-live-payload.json``: ``GET /api/adviser/live`` after Stop, unmodified (the session's saved view);
- ``market-view-records.jsonl``: the journal ``market_view`` records 760, 772, 776, 781 of run live-20261008T0921-439cd7.
Variant "saved" serves the payload as is. Variants "record-<seq>" serve the same payload with only ``view.market_view``
replaced by that journal record (``env`` and ``uncertainty`` removed: the API does not serve them). Every non-GET
request is aborted; other GETs reach the real API read-only. The output is a reconstruction, never the Owner's screen.

Usage: python -I reconstruct_market_reading.py <this directory>
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"


def variants(d: Path) -> dict[str, dict]:
    saved = json.loads((d / "saved-live-payload.json").read_text(encoding="utf-8"))
    out = {"saved": saved}
    for line in (d / "market-view-records.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        mv = {k: v for k, v in r.items() if k not in ("env", "uncertainty")}
        p = copy.deepcopy(saved)
        p["view"]["market_view"] = mv
        out[f"record-{int(r['env']['record_id'].rsplit('-', 1)[1])}"] = p
    return out


def _handler(body: str):
    def handle(route):
        if route.request.method != "GET":
            return route.abort()
        if route.request.url.split("?")[0].endswith("/api/adviser/live"):
            return route.fulfill(status=200, body=body, headers={"content-type": "application/json"})
        return route.continue_()
    return handle


def main(d: Path) -> None:
    texts: dict[str, dict[str, str]] = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for name, payload in variants(d).items():
            body = json.dumps(payload)
            ctx = browser.new_context(viewport={"width": 1912, "height": 1100}, locale="it-IT", timezone_id="Europe/Rome")
            page = ctx.new_page()

            page.route("**/api/**", _handler(body))
            page.goto(f"{BASE}/#market")
            box = page.get_by_test_id("live-market-reading")
            box.wait_for(timeout=15_000)
            page.wait_for_timeout(2500)  # at least one poll of the served payload
            details = page.get_by_test_id("live-proposal-details")
            details.locator("summary").click()
            texts[name] = {"box": box.inner_text(), "approfondimenti": details.inner_text()}
            label = (f"RICOSTRUZIONE ({name}) — non è la schermata vista dall'Owner. Frontend 87322ac servito, "
                     + ("vista salvata della sessione (dopo Stop), market_view = record 781"
                        if name == "saved" else f"vista salvata con market_view sostituito dal record del journal {name[7:]}"))
            page.evaluate("""([label]) => {
                const box = document.querySelector('[data-testid="live-market-reading"]');
                const tag = document.createElement('div');
                tag.textContent = label;
                tag.style.cssText = 'border:2px dashed #e0a030;color:#e0a030;padding:6px 10px;margin:0 0 8px;font:600 13px sans-serif';
                box.parentNode.insertBefore(tag, box);
            }""", [label])
            # page coordinates of the label and of the box (viewport rectangle + scroll offset)
            b1, b2 = (box.evaluate("(e, prev) => { const r = (prev ? e.previousSibling : e).getBoundingClientRect();"
                                   " return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }", prev)
                      for prev in (True, False))
            x0, y0 = min(b1["x"], b2["x"]), b1["y"]
            x1, y1 = max(b1["x"] + b1["w"], b2["x"] + b2["w"]), b2["y"] + b2["h"]
            page.screenshot(path=str(d / f"market-reading-{name}.png"), full_page=True,
                            clip={"x": x0 - 4, "y": y0 - 4, "width": x1 - x0 + 8, "height": y1 - y0 + 8})
            ctx.close()
        browser.close()
    (d / "rendered-text.json").write_text(json.dumps(texts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
