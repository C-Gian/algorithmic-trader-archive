"""A confirmations -> entry opportunities, September-December 2025 (v0.6): reconstruction from existing records only.

Reads the local 12 October v0.6 journal (identity re-checked against the committed manifest). No replay, extraction,
acquisition, evaluator, alternative entry or price search: every value comes from the scenario and child
(``entry_attempt``) records the frozen engine published, in journal order.

Population: every A scenario whose BIRTH publication is in [2025-09-01, 2026-01-01) and that has a CONFIRM (one row per
scenario, linked to its child ``<scenario>#entry``). For each, in actual order:
* the routing record of the confirmation dispatch (``core3._route_a``): levels/conditions at confirmation (geometry,
  clocks, diagnostic D/N, every computed blocker) and the code's control-flow precedence that chose its reason;
* the WAIT path when RETURN opened: temporary blockers per BLOCKERS record (emitted only when the set changes), cap
  revisions, the RETURN reference (``RESPONSE_REFERENCE``), the initial-response check (MP-005) and the local response;
* the end: ISSUE, or the child terminal with its reason, time, sequence and the blockers recorded with it.

Each end is placed in ONE of: ISSUED; 1 incompatibility already present at confirmation; 2 temporary restriction still
active when the child's timer ran out; 3 unavailability arising during the wait; 4 scenario terminal closing the child.
A sub-class keeps geometry, cost, selection/gates, new price evidence, context, ambiguity and timer apart. The source
of every reason is the record (transition, reason, blockers, seq); nothing is inferred from a terminal reason alone.

  python paths.py <run_dir> <out_dir>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EV = HERE.parent
WINDOW = ("2025-09-01T00:00:00Z", "2026-01-01T00:00:00Z")

# routing precedence of core3._route_a (structural -> target contact -> prerequisites -> non-selection -> IMMEDIATE /
# non-routable immediate -> empty corridor -> no economic region -> WAIT_OPEN)
ROUTING = {
    "AT_OPPOSING_AREA": ("1", "GEOMETRY:TARGET_INSIDE_OPPOSING_AREA"),
    "NO_TARGET": ("1", "GEOMETRY:NO_TARGET"),
    "PRE_ENTRY_TARGET_CONTACT": ("1", "GEOMETRY:TARGET_REACHED_BY_CONFIRMING_BAR"),
    "UNAVAILABLE_GEOMETRY": ("1", "GEOMETRY:UNAVAILABLE"),
    "NONSELECTION_GATE": ("1", "SELECTION_OR_GATE:NONSELECTION"),
    "IMMEDIATE_INCOMPATIBLE": ("1", "GEOMETRY_OR_COST:IMMEDIATE_NOT_ROUTABLE"),
    "EMPTY_RETURN_CORRIDOR": ("1", "GEOMETRY:EMPTY_RETURN_CORRIDOR"),
    "NO_ECONOMIC_RETURN_REGION": ("1", "COST:NO_ECONOMIC_RETURN_REGION_AT_FIXED_COST"),
}
# WAIT terminals (core3._wait_protect / _wait_step, core5 response, core6 initial check, selection)
WAITING = {
    "ORIGINAL_SETUP_DEADLINE": ("2", "TIMER:SETUP_EXPIRY_WHILE_BLOCKED"),
    "CONTEXT_FORBIDDEN_PREISSUE": ("3", "CONTEXT:WITHDRAWN_BEFORE_ISSUE"),
    "PRE_ENTRY_TARGET_CONTACT": ("3", "NEW_PRICE_EVIDENCE:TARGET_OR_CAP_REACHED_BEFORE_ENTRY"),
    "CAP_NOT_AHEAD_NOW": ("3", "NEW_PRICE_EVIDENCE:NEW_CAP_NOT_AHEAD"),
    "PRE_ENTRY_CONTACT_TIME_AMBIGUOUS": ("3", "AMBIGUITY:CONTACT_TIME"),
    "CAP_ACTIVATION_CONTACT_AMBIGUOUS": ("3", "AMBIGUITY:CAP_ACTIVATION"),
    "LOCAL_CONTACT_TIME_AMBIGUOUS": ("3", "AMBIGUITY:LOCAL_RESPONSE"),
    "EMPTY_RETURN_CORRIDOR": ("3", "GEOMETRY:CORRIDOR_EMPTIED_BY_CAP"),
    "NO_ECONOMIC_RETURN_REGION": ("3", "COST:ECONOMIC_REGION_EMPTIED_DURING_WAIT"),
    "INITIAL_RESPONSE_INCOMPATIBLE:CORRIDOR": ("3", "GEOMETRY:REFERENCE_INCOMPATIBLE_WITH_CORRIDOR"),
    "INITIAL_RESPONSE_INCOMPATIBLE:HISTORICAL_ECONOMICS": ("3", "COST:REFERENCE_INCOMPATIBLE_WITH_ECONOMIC_REGION"),
    "LOCAL_RESPONSE_CONTRADICTED": ("3", "NEW_PRICE_EVIDENCE:LOCAL_RESPONSE_CONTRADICTED"),
    "RESPONSE_NOT_ISSUABLE": ("3", "AT_RECOVERY:NOT_ISSUABLE"),
    "EVALUATION_WINDOW_ENDED": ("3", "SELECTION_OR_GATE:EVALUATION_WINDOW_ENDED"),
}
SELECTION = ("SLOT_OCCUPIED", "CONFLICTED", "PRIORITY")
RNI_CLASS = {"ECONOMICS_GEOMETRY": "GEOMETRY_OR_COST", "SELECTION": "SELECTION_OR_GATE", "OTHER_GATES": "OTHER_GATE"}
# the earlier tabulation of the same 89 first-attempt children (A2X comparison SUMMARY, row "First-attempt child")
A2X_TABLE = {"ISSUED": 1, "NO_ECONOMIC_RETURN_REGION": 22, "PRE_ENTRY_TARGET_CONTACT": 18,
             "SCENARIO_TERMINAL:DESTINATION_REACHED": 15, "INITIAL_RESPONSE_INCOMPATIBLE:HISTORICAL_ECONOMICS": 9,
             "ORIGINAL_SETUP_DEADLINE": 8, "AT_OPPOSING_AREA": 7, "CONTEXT_FORBIDDEN_PREISSUE": 4,
             "INITIAL_RESPONSE_INCOMPATIBLE:CORRIDOR": 3, "SCENARIO_TERMINAL:INVALIDATED": 2}


def head(reason: str | None) -> str:
    return (reason or "").split(":")[0]


def classify_end(phase: str, tr: str, reason: str, blockers: list[str]) -> tuple[str, str]:
    if tr == "ISSUE":
        return "ISSUED", "ISSUED"
    r = reason or ""
    if r.startswith("SCENARIO_TERMINAL:"):
        return "4", "SCENARIO:" + r.split(":")[1]
    sel = [x for x in r.split(",") if x in SELECTION]
    if tr == "REJECT" or sel:
        cat = "1" if phase == "ROUTING" else "3"
        return cat, "SELECTION_OR_GATE:" + (sel[0] if sel else "REJECTED")
    if phase == "ROUTING":
        return ROUTING.get(head(r), ("UNCLASSIFIED", "UNCLASSIFIED:" + head(r)))
    if r.startswith("INITIAL_RESPONSE_INCOMPATIBLE:"):
        return WAITING.get(":".join(r.split(":")[:2]), ("UNCLASSIFIED", "UNCLASSIFIED:" + r))
    if r.startswith("RESPONSE_NOT_ISSUABLE:"):
        prim = r.split(":", 1)[1]
        from_core5 = {"ECONOMICS_GEOMETRY": {"EMPTY_RETURN_CORRIDOR", "CLOSE_OUTSIDE_RETURN_CORRIDOR",
                                             "SIDE_PRICE_OUTSIDE_RETURN_CORRIDOR", "BLOCKED_BY_ZONE",
                                             "SIDE_PRICE_INSIDE_OPPOSING_ZONE", "NO_ECONOMIC_RETURN_REGION",
                                             "TEMPORARY_COST_BLOCKED", "NO_ROOM_AFTER_COSTS",
                                             "AT_OR_BEYOND_INVALIDATION", "REWARD_RISK_BELOW_MINIMUM",
                                             "INVALID_INPUT"},
                      "SELECTION": set(SELECTION)}
        cls = next((k for k, v in from_core5.items() if prim.split(":")[0] in v), "OTHER_GATES")
        return "3", f"AT_RECOVERY:{RNI_CLASS[cls]}:{prim}"
    return WAITING.get(head(r), ("UNCLASSIFIED", "UNCLASSIFIED:" + head(r)))


def short(reason: str | None) -> str:
    """The earlier tabulation's label of a terminal reason (for the reconciliation only)."""
    r = reason or ""
    if r.startswith("SCENARIO_TERMINAL:"):
        return ":".join(r.split(":")[:2])
    if r.startswith("INITIAL_RESPONSE_INCOMPATIBLE:"):
        return ":".join(r.split(":")[:2])
    return head(r)


def build(journal: list[dict]) -> list[dict]:
    scen: dict[str, list[dict]] = defaultdict(list)
    child: dict[str, list[dict]] = defaultdict(list)
    calls: dict[str, list[str]] = defaultdict(list)
    for e in journal:
        r = e["record"]
        if e["kind"] == "scenario" and r.get("family") == "A":
            scen[r["scenario_id"]].append(e)
        elif e["kind"] == "entry_attempt" and r.get("family") == "A":
            child[r["scenario_id"]].append(e)
        elif e["kind"] == "call" and r.get("family") == "A":
            calls[r["scenario_id"]].append(r["call_id"])
    rows = []
    for sid, es in scen.items():
        es.sort(key=lambda e: e["seq"])
        born = es[0]["clock_time"]
        conf = next((e for e in es if e["record"]["transition"] == "CONFIRM"), None)
        if not (WINDOW[0] <= born < WINDOW[1]) or conf is None:
            continue
        term = next((e for e in es if e["record"]["transition"] == "TERMINAL"), None)
        cs = sorted(child.get(sid, []), key=lambda e: e["seq"])
        before = [e for e in cs if e["seq"] < conf["seq"]]
        after = [e for e in cs if e["seq"] > conf["seq"]]
        row = {"scenario_id": sid, "direction": conf["record"]["direction"], "born_at": born,
               "confirmed_at": conf["clock_time"], "confirm_seq": conf["seq"],
               "confirmed_epoch": conf["record"].get("anchor_epoch"),
               "scenario_terminal": (f"{term['record'].get('terminal_state')}:{head(term['record'].get('reason'))}"
                                     if term else "OPEN_AT_DATA_END"),
               "scenario_terminal_at": term["clock_time"] if term else None,
               "child_records_before_confirmation": len(before), "calls": calls.get(sid, []), "events": [],
               "linkage": None}
        for e in after:
            r = e["record"]
            row["events"].append({"seq": e["seq"], "clock_time": e["clock_time"], "transition": r["transition"],
                                  "state": r.get("state"), "mode": r.get("mode"), "reason": r.get("reason"),
                                  "blockers": r.get("blockers") or [], "geometry": r.get("geometry") or {},
                                  "diagnostic": r.get("diagnostic") or {}, "clocks": r.get("clocks") or {},
                                  "limiting_landmark": r.get("limiting_landmark"), "response": r.get("response"),
                                  "cap_history": r.get("cap_history") or [], "call_id": r.get("call_id")})
        ev = row["events"]
        if not ev:
            row["linkage"] = "no child record after the confirmation"
            rows.append(row)
            continue
        first = ev[0]
        if first["clock_time"] != conf["clock_time"]:
            row["linkage"] = "first child record is not in the confirmation dispatch"
        g, dg, ck = first["geometry"], first["diagnostic"], first["clocks"]
        row.update({
            "routing_record": first["transition"], "routing_mode": first["mode"], "routing_reason": first["reason"],
            "routing_blockers_all": first["blockers"],
            "conf_close": g.get("confirmation_close"), "T_confirm": g.get("T_confirm"), "V": g.get("V"),
            "K_trigger": g.get("K_trigger"), "R": g.get("R"), "target_type": g.get("target_type"),
            "I0": g.get("I0"), "corridor": g.get("corridor"), "economic_fixed_k": g.get("economic_fixed_k"),
            "economic_current": g.get("economic_current"), "K_cost": g.get("K_cost"), "G": g.get("G"),
            "Q": g.get("Q"), "margin": g.get("margin"), "in_D": dg.get("in_D"), "in_N": dg.get("in_N"),
            "exclusion": dg.get("exclusion"), "setup_expiry": ck.get("setup_expiry"),
            "hard_deadline": ck.get("hard_deadline"),
            "limiting": (first["limiting_landmark"] or {}).get("type")})
        if first["transition"] == "WAIT_OPEN":
            row["route"] = "RETURN_WAIT"
        elif first["transition"] == "ISSUE":
            row["route"] = "IMMEDIATE_ISSUED"
        elif first["transition"] == "REJECT":
            row["route"] = "IMMEDIATE_REJECTED_AT_SELECTION"
        else:
            row["route"] = "TERMINAL_AT_CONFIRMATION"
        end = ev[-1]
        row.update({"end_transition": end["transition"], "end_reason": end["reason"], "end_at": end["clock_time"],
                    "end_seq": end["seq"], "end_blockers_recorded": end["blockers"]})
        waits = ev[1:] if row["route"] == "RETURN_WAIT" else []
        blk = [x for x in waits if x["transition"] == "BLOCKERS"]
        seen = Counter(b for x in [first] + blk for b in x["blockers"])
        last_set = None
        for x in [first] + [w for w in waits if w["transition"] in ("BLOCKERS", "CAP_REVISION")]:
            last_set = x["blockers"]
        ref = next((x for x in waits if x["transition"] == "RESPONSE_REFERENCE"), None)
        row.update({
            "wait_blocker_changes": len(blk), "wait_cap_revisions": sum(x["transition"] == "CAP_REVISION" for x in waits),
            "wait_blockers_seen": dict(sorted(seen.items())) if row["route"] == "RETURN_WAIT" else {},
            "wait_last_blockers_before_end": (last_set or []) if row["route"] == "RETURN_WAIT" else [],
            "wait_ever_unblocked": ref is not None,
            "reference_at": ref["clock_time"] if ref else None,
            "reference_same_dispatch_as_end": bool(ref) and ref["clock_time"] == end["clock_time"],
            "response_outcome": ((end.get("response") or {}).get("outcome") if end.get("response") else None)})
        phase = "ROUTING" if row["route"] != "RETURN_WAIT" else "WAIT"
        cat, sub = classify_end(phase, end["transition"], end["reason"], end["blockers"])
        row["category"], row["subclass"] = cat, sub
        if cat == "4" and row["route"] == "RETURN_WAIT":
            row["note"] = "scenario terminal while waiting; last recorded blockers kept"
        rows.append(row)
    return sorted(rows, key=lambda r: (r["confirmed_at"], r["scenario_id"]))


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    route = Counter(r.get("route", "UNLINKED") for r in rows)
    cat = Counter(r.get("category", "UNLINKED") for r in rows)
    sub = Counter(f"{r.get('category')} | {r.get('subclass')}" for r in rows)
    wait = [r for r in rows if r.get("route") == "RETURN_WAIT"]
    out = {
        "confirmations": n, "routes": dict(sorted(route.items())), "end_categories": dict(sorted(cat.items())),
        "end_subclasses": dict(sorted(sub.items())),
        "routing_terminal_reasons": dict(sorted(Counter(
            head(r["routing_reason"]) for r in rows if r.get("route") == "TERMINAL_AT_CONFIRMATION").items())),
        "routing_all_blockers_of_terminals": dict(sorted(Counter(
            b for r in rows if r.get("route") == "TERMINAL_AT_CONFIRMATION" for b in r["routing_blockers_all"]).items())),
        "routing_diagnostic_D_N": dict(sorted(Counter(
            f"in_D={r.get('in_D')},in_N={r.get('in_N')},exclusion={r.get('exclusion')}" for r in rows).items())),
        "wait_open_blockers": dict(sorted(Counter(b for r in wait for b in r["routing_blockers_all"]).items())),
        "wait_blockers_seen_any_time": dict(sorted(Counter(b for r in wait for b in r["wait_blockers_seen"]).items())),
        "wait_reference_prepared": sum(1 for r in wait if r["wait_ever_unblocked"]),
        "wait_reference_then_end_same_dispatch": sum(1 for r in wait if r["reference_same_dispatch_as_end"]),
        "wait_end_by_category": dict(sorted(Counter(f"{r['category']} | {r['subclass']}" for r in wait).items())),
        "wait_end_after_reference": dict(sorted(Counter(
            f"{r['category']} | {r['subclass']}" for r in wait if r["wait_ever_unblocked"]).items())),
        "timer_ends_last_blockers": dict(sorted(Counter(
            ",".join(r["wait_last_blockers_before_end"]) or "(none recorded)" for r in rows
            if r.get("subclass", "").startswith("TIMER")).items())),
        "scenario_terminal_ends_last_blockers": dict(sorted(Counter(
            ",".join(r["wait_last_blockers_before_end"]) or "(not waiting / none)" for r in rows
            if r.get("category") == "4").items())),
        "calls": sorted(c for r in rows for c in r["calls"]),
        "earlier_tabulation_labels": dict(sorted(Counter(
            "ISSUED" if r.get("end_transition") == "ISSUE" else short(r.get("end_reason")) for r in rows).items())),
    }
    out["reconciliation"] = {
        "routes sum to the confirmations": sum(route.values()) == n,
        "end categories sum to the confirmations": sum(cat.values()) == n,
        "wait ends sum to the waits": sum(out["wait_end_by_category"].values()) == route.get("RETURN_WAIT", 0),
        "issued children = calls": cat.get("ISSUED", 0) == len(out["calls"]),
        "end reasons = the earlier tabulation (A2X comparison, 89 first-attempt children)":
            out["earlier_tabulation_labels"] == dict(sorted(A2X_TABLE.items())),
    }
    return out


def checks(rows: list[dict]) -> dict:
    return {
        "89 confirmations, one row per scenario": len(rows) == 89 and len({r["scenario_id"] for r in rows}) == 89,
        "every child linked (records after the confirmation, first in the confirmation dispatch)":
            all(r["linkage"] is None for r in rows),
        "no child record before the confirmation": all(r["child_records_before_confirmation"] == 0 for r in rows),
        "one end per child: ISSUE or TERMINAL/REJECT, last record": all(
            r["end_transition"] in ("ISSUE", "TERMINAL", "REJECT")
            and sum(e["transition"] in ("ISSUE", "TERMINAL", "REJECT") for e in r["events"]) == 1 for r in rows),
        "every end classified": all(r["category"] != "UNCLASSIFIED" for r in rows),
        "routing reasons follow the code precedence (structural before target contact before gates before WAIT)":
            all(_precedence_ok(r) for r in rows),
    }


def _precedence_ok(r: dict) -> bool:
    if r["route"] != "TERMINAL_AT_CONFIRMATION":
        return True
    b, reason = r["routing_blockers_all"], head(r["routing_reason"])
    order = ["AT_OPPOSING_AREA", "NO_TARGET", "PRE_ENTRY_TARGET_CONTACT"]
    present = [x for x in order if x in b]
    if present:
        return reason == present[0]
    return reason in ("UNAVAILABLE_GEOMETRY", "NONSELECTION_GATE", "IMMEDIATE_INCOMPATIBLE", "EMPTY_RETURN_CORRIDOR",
                      "NO_ECONOMIC_RETURN_REGION")


def rows_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = ["scenario_id", "direction", "born_at", "confirmed_at", "confirm_seq", "confirmed_epoch", "route",
            "routing_record", "routing_mode", "routing_reason", "routing_blockers_all", "conf_close", "T_confirm", "V",
            "K_trigger", "R", "target_type", "limiting", "I0", "corridor", "economic_fixed_k", "K_cost", "G", "Q",
            "margin", "in_D", "in_N", "exclusion", "setup_expiry", "hard_deadline", "wait_blocker_changes",
            "wait_cap_revisions", "wait_blockers_seen", "wait_last_blockers_before_end", "reference_at",
            "reference_same_dispatch_as_end", "response_outcome", "end_transition", "end_reason", "end_at", "end_seq",
            "end_blockers_recorded", "category", "subclass", "scenario_terminal", "scenario_terminal_at", "calls",
            "linkage"]
    w.writerow(cols)
    for r in rows:
        vals = []
        for c in cols:
            v = r.get(c)
            vals.append(json.dumps(v, sort_keys=True) if isinstance(v, (list, dict)) else v)
        w.writerow(vals)
    return buf.getvalue()


def main(run: Path, out: Path) -> None:
    m = json.loads((EV / "A-REACTION-EFFICIENCY-EXPLORATION/run_manifest.json").read_text(encoding="utf-8"))
    jp = run / "journal.jsonl.gz"
    if hashlib.sha256(jp.read_bytes()).hexdigest() != m["outputs_outside_git"]["journal.jsonl.gz"]:
        raise SystemExit("journal differs from the committed manifest: stop")
    with gzip.open(jp, "rt", encoding="utf-8") as f:
        journal = [json.loads(x) for x in f]
    rows = build(journal)
    res = {"input": {"journal_sha256": m["outputs_outside_git"]["journal.jsonl.gz"], "entries": len(journal)},
           "checks": checks(rows), "tables": summarize(rows)}
    res["all_pass"] = all(res["checks"].values()) and all(res["tables"]["reconciliation"].values())
    out.mkdir(parents=True, exist_ok=True)
    files = {"results.json": json.dumps(res, indent=1, sort_keys=True) + "\n", "paths.csv": rows_csv(rows),
             "sequences.json": json.dumps(rows, indent=1, sort_keys=True) + "\n"}
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
        print(name, hashlib.sha256(text.encode()).hexdigest())
    print("ALL PASS" if res["all_pass"] else "CHECK OR RECONCILIATION FAILURE")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
