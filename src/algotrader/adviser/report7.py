"""v0.7 adviser evaluation report section (``adviser.report.v7``), built from COMMITTED records only.

It is the v0.6 report unchanged (v0.7 keeps every operational rule: calls, entries, selection and terminals) plus one
descriptive section on the trigger/destination compatibility, counted from the PUBLISHED records only (nothing is
recomputed from prices or levels):

* incompatible publications: A scenario records whose published antecedent states that the current recovery condition
  is incompatible with its destination (by transition), and the distinct scenarios concerned;
* MarketView publications that list an ARMED scenario among the observed hypotheses (not directional support);
* restorations: an A scenario whose incompatible publication is followed by a REVISE/REARM publishing a compatible
  condition (support restored only from that publication).

Nothing here is a frequency, an accuracy or a profit measure; more or fewer directional readings are not improvement.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from . import methods
from . import report6 as r6

REPORT_VERSION = "adviser.report.v7"
INCOMPATIBLE = "current recovery condition incompatible with its destination"


def trigger_destination(journal: list[dict]) -> dict[str, Any]:
    by_tr: Counter = Counter()
    scen: set[str] = set()
    last_incompatible: dict[str, bool] = {}
    restored: list[dict] = []
    views = 0
    for e in journal:
        r = e["record"]
        if e["kind"] == "scenario" and r.get("family") == "A":
            inc = str(r.get("antecedent") or "").startswith(INCOMPATIBLE) and r["transition"] != "TERMINAL"
            sid = r["scenario_id"]
            if inc:
                by_tr[r["transition"]] += 1
                scen.add(sid)
            elif last_incompatible.get(sid) and r["transition"] in ("REVISE", "REARM"):
                restored.append({"scenario_id": sid, "at": r["env"]["clock_time"], "transition": r["transition"],
                                 "trigger_level": r.get("trigger_level"), "destination": r.get("destination")})
            if r["transition"] in ("ARM", "REVISE", "REARM", "ANCHOR_LOST", "TERMINAL", "CONFIRM"):
                last_incompatible[sid] = inc
        elif e["kind"] == "market_view" and any(w.get("status") == "ARMED" for w in r.get("watch") or ()):
            views += 1
    return {"unit": "published records (not independent observations, not durations)",
            "incompatible_publications": sum(by_tr.values()),
            "incompatible_publications_by_transition": dict(sorted(by_tr.items())),
            "scenarios_with_an_incompatible_publication": len(scen),
            "market_views_without_support_from_an_armed_scenario": views,
            "restored_by_a_compatible_revision": len(restored), "restoration_examples": restored[:5],
            "note": ("Counted from the published antecedents and MarketView records only. An incompatible condition "
                     "would reach its destination before it could confirm; v0.7 states it and does not count the "
                     "scenario as directional support. Calls, entries, selection and terminals are those of v0.6.")}


def build(*, engine: dict, journal: list[dict], records: list[dict], view: dict | None, status: str,
          clock_end_reached: bool) -> dict[str, Any]:
    out = r6.build(engine=engine, journal=journal, records=records, view=view, status=status,
                   clock_end_reached=clock_end_reached)
    rel = methods.get("v0.7")
    out.update(report_version=REPORT_VERSION,
               method={"method": "v0.7", "model": engine["adviser"]["identity"]["model"], "status": rel.status,
                       "status_label": rel.status_label, "economic_usefulness": "UNVALIDATED"},
               trigger_destination=trigger_destination(journal),
               gates_note="v0.7 gate statistics are in the entry_attempt records (unchanged from v0.6)")
    if status == "completed":
        out["conclusion"] = {
            "verdict": "REPORTED_FOR_DIRECTOR_REVIEW",
            "text": ("v0.7 results are reported for Director diagnosis; no registered evidence criterion applies. v0.7 "
                     "changes the explanation and the market reading only (an A condition that would already reach "
                     "its destination is not counted as directional support); calls, entries, selection and terminals "
                     "are those of v0.6, so a v0.6/v0.7 comparison on the same pack must show identical calls.")}
    return out


def render_markdown(a: dict[str, Any]) -> list[str]:
    lines = r6.render_markdown(a)
    status_label = a["method"].get("status_label") or "engineering review pending"
    lines[1] = (f"## Adviser evaluation — Candidate v0.7 (trigger/destination compatibility over MP-005; {status_label}; "
                "hypothetical, no orders)")
    td = a.get("trigger_destination")
    if not td:
        return lines
    return lines + [
        "", "#### Trigger/destination compatibility (published records only)",
        f"- Incompatible publications: {td['incompatible_publications']} "
        f"({td['incompatible_publications_by_transition'] or '{}'}) · scenarios concerned: "
        f"{td['scenarios_with_an_incompatible_publication']}",
        f"- MarketView publications without support from an armed scenario: "
        f"{td['market_views_without_support_from_an_armed_scenario']}",
        f"- Support restored by a compatible revision: {td['restored_by_a_compatible_revision']}",
        f"- {td['note']}"]
