"""v0.7 historical policy study: per-period reconciliation and primary result from the run outputs (no engine).

scenario (by family, birth window) -> engine admissibility (structural CONFIRM) -> issuance (call) -> modelled entry
(PRIMARY path entered) or NO_ENTRY -> outcome (path status / exit class) -> primary result.

Primary result (registered): the sum of ``price_net`` over the PRIMARY paths with status CLOSED of every A/B/C call
issued in the evaluation window; normalized one-unit paths (N0 = 1 abstract USDT reporting unit, q = 1/E), net of the
included fees and allowances; PRICE_NET_ONLY. It is COMPLETE only when no PRIMARY path is AMBIGUOUS, CENSORED or
UNRESOLVED; otherwise only the determined subtotal is reported, with the reasons. NO_ENTRY is not a success and adds no
price_net; revisions are not opportunities. Never aggregated across periods.

  python tabulate.py <label> <run_dir> <v06_journal.jsonl.gz> <out_dir>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, localcontext
from pathlib import Path

RULES_V07 = "1f3704f4453bc3ab7528e9de916d05d64e2e0955c0ef81170c26694bf719b39f"
REGISTER_V07 = "8525ec74e2ccbaf0834137312c05aff59bae4714a76221d9f42b426ea7d5569c"
EVALUATOR_SHA = "85504d5843e144d0b86a0ee3e693c064f4d7f64e7928c1e54fb9c9e9f308615c"
FEE, ALLOW = Decimal("0.0005"), Decimal("0.0002")
UNDETERMINED = ("AMBIGUOUS", "CENSORED", "UNRESOLVED")


def dt(s: str) -> datetime:
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def ceil_minute(t: datetime) -> datetime:
    f = t.replace(second=0, microsecond=0)
    return f if f == t else f + timedelta(minutes=1)


def load_gz(p: Path) -> list[dict]:
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return [json.loads(x) for x in f]


def window(t: str, eng: dict) -> str:
    return "warmup" if dt(t) < dt(eng["eval_start"]) else "evaluation" if dt(t) < dt(eng["eval_end"]) else "tail"


def run(label: str, run_dir: Path, v06: Path) -> tuple[dict, list[dict]]:
    man = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    eng = man["engine"]["adviser"]
    journal = load_gz(run_dir / "journal.jsonl.gz")
    records = load_gz(run_dir / "records.jsonl.gz")
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    c: dict[str, bool] = {}
    hashes = {k: hashlib.sha256((run_dir / k).read_bytes()).hexdigest() for k in man["outputs_outside_git"]}
    c["outputs = the hashes recorded in the run manifest"] = hashes == man["outputs_outside_git"]
    ident = eng["identity"]
    c["engine identity = frozen v0.7; evaluator = registered"] = (
        (ident["rules_sha256"], ident["register_sha256"], ident["implementation"]) == (RULES_V07, REGISTER_V07,
                                                                                      "adviser.core.v7")
        and eng["evaluator"]["sha256"] == EVALUATOR_SHA and eng["method"] == "v0.7")
    impls = {e["record"]["env"]["method"]["implementation"] for e in journal if (e["record"].get("env") or {}).get("method")}
    c["every journal record carries adviser.core.v7"] = impls == {"adviser.core.v7"}
    # ---- scenarios by family / birth window; engine admissibility = structural CONFIRM ------------------------------
    scen: dict[str, list[dict]] = defaultdict(list)
    for e in journal:
        if e["kind"] == "scenario":
            scen[e["record"]["scenario_id"]].append(e)
    srow = {}
    for sid, es in scen.items():
        es.sort(key=lambda e: e["seq"])
        tr = [e["record"]["transition"] for e in es]
        srow[sid] = {"family": es[0]["record"]["family"], "born": es[0]["clock_time"],
                     "window": window(es[0]["clock_time"], eng), "armed": "ARM" in tr, "confirmed": "CONFIRM" in tr}
    # ---- calls and their revisions -------------------------------------------------------------------------------
    calls = {e["record"]["call_id"]: e for e in journal if e["kind"] == "call"}
    revs = Counter(e["record"]["call_id"] for e in journal if e["kind"] == "call_revision")
    paths = defaultdict(dict)
    for x in records:
        r = x["record"]
        if "variant" in r and "call_id" in r:
            paths[r["call_id"]][r["variant"]] = r
    rows = []
    cost_ok = delay_ok = True
    for cid, e in sorted(calls.items(), key=lambda kv: kv[1]["seq"]):
        r = e["record"]
        issued = r["issued_at"]
        win = window(issued, eng)
        p = paths.get(cid, {}).get("PRIMARY")
        row = {"call_id": cid, "family": r["family"], "direction": r["direction"], "issued_at": issued,
               "issue_window": win, "scenario_id": r.get("scenario_id"),
               "scenario_birth_window": (srow.get(r.get("scenario_id")) or {}).get("window"),
               "revisions": revs.get(cid, 0), "primary_status": p["status"] if p else None,
               "exit_class": p.get("exit_class") if p else None,
               "entry_price": (p.get("entry") or {}).get("price") if p else None,
               "entry_time": (p.get("entry") or {}).get("time_start") if p else None,
               "exit_price": (p.get("exit") or {}).get("price") if p else None,
               "exit_time": (p.get("exit") or {}).get("time_end") if p else None,
               "gross": p.get("gross") if p else None, "fees": p.get("fees") if p else None,
               "allowances": p.get("allowances") if p else None, "price_net": p.get("price_net") if p else None,
               "stress_price_net": p.get("stress_price_net") if p else None,
               "total_net": p.get("total_net") if p else None, "funding_status": p.get("funding_status") if p else None,
               "bounds": p.get("bounds") if p else None,
               "secondary": {v: (paths[cid][v]["status"], paths[cid][v].get("price_net"))
                             for v in ("ENTRY_DELAY_0", "ENTRY_DELAY_120", "HORIZON_ONLY") if v in paths.get(cid, {})}}
        if p and p["status"] == "CLOSED" and p.get("entry") and p.get("exit"):
            d = 1 if r["direction"] == "LONG" else -1
            with localcontext() as ctx:
                ctx.prec = 60
                ratio = Decimal(p["exit"]["price"]) / Decimal(p["entry"]["price"])
                g, fe, al = d * (ratio - 1), FEE * (1 + ratio), ALLOW * (1 + ratio)
                tol = Decimal("1e-20")
                cost_ok &= (abs(g - Decimal(p["gross"])) < tol and abs(fe - Decimal(p["fees"])) < tol
                            and abs(al - Decimal(p["allowances"])) < tol
                            and abs(Decimal(p["gross"]) - Decimal(p["fees"]) - Decimal(p["allowances"])
                                    - Decimal(p["price_net"])) < tol)
        if p and p.get("entry"):
            delay_ok &= dt(p["entry"]["time_start"]) >= ceil_minute(dt(issued) + timedelta(seconds=60))
            delay_ok &= p["profile"]["entry_delay_seconds"] == 60 and p["profile"]["exit_delay_seconds"] == 60
        rows.append(row)
    c["costs: gross, fees (5 bps/leg) and allowances (2 bps/leg) recomputed from the fills; net = gross - fees - "
      "allowances"] = cost_ok
    c["PRIMARY: entry at/after ceil-minute(issue + 60 s); profile entry/exit delay 60 s"] = delay_ok
    ev_calls = [x for x in rows if x["issue_window"] == "evaluation"]
    c["exactly one PRIMARY path per evaluation-window call; none for calls outside the window"] = (
        all(x["primary_status"] is not None for x in ev_calls)
        and all(x["primary_status"] is None for x in rows if x["issue_window"] != "evaluation"))
    c["no call issued in the tail"] = not any(x["issue_window"] == "tail" for x in rows)
    # ---- v0.6 parity of calls on the same pack -------------------------------------------------------------------
    v06 = [e for e in load_gz(v06) if e["kind"] == "call"]
    key = lambda r: (r["call_id"], r["issued_at"], r["family"], r["direction"])  # noqa: E731
    c["v0.7 calls identical to the v0.6 calls of the same pack (id, issue time, family, direction)"] = (
        sorted(key(e["record"]) for e in v06) == sorted(key(e["record"]) for e in calls.values()))
    # ---- funnel per family and primary result ---------------------------------------------------------------------
    fam = {}
    for f in "ABC":
        sc = [s for s in srow.values() if s["family"] == f and s["window"] == "evaluation"]
        fc = [x for x in ev_calls if x["family"] == f]
        st = Counter(x["primary_status"] for x in fc)
        closed = [x for x in fc if x["primary_status"] == "CLOSED"]
        fam[f] = {"scenarios_born_in_evaluation": len(sc), "armed": sum(s["armed"] for s in sc),
                  "confirmed_engine_admissible": sum(s["confirmed"] for s in sc),
                  "calls_issued_in_evaluation": len(fc),
                  "of_which_scenario_born_before_evaluation": sum(1 for x in fc if x["scenario_birth_window"] != "evaluation"),
                  "call_revisions_not_opportunities": sum(x["revisions"] for x in fc),
                  "primary_entered": sum(1 for x in fc if x["entry_price"] is not None),
                  "primary_status": dict(sorted(st.items())),
                  "closed_exit_classes": dict(sorted(Counter(x["exit_class"] for x in closed).items())),
                  "closed_sum_price_net": str(sum((Decimal(x["price_net"]) for x in closed), Decimal(0)))}
    allc = [x for x in ev_calls]
    closed = [x for x in allc if x["primary_status"] == "CLOSED"]
    undet = [x for x in allc if x["primary_status"] in UNDETERMINED]
    total = sum((Decimal(x["price_net"]) for x in closed), Decimal(0))
    primary = {"unit": "normalized one-unit hypothetical paths (N0 = 1 abstract USDT reporting unit, q = 1/E); "
                       "sum of per-path price_net fractions; not a return on Owner capital, not compounded",
               "costs_included": "fees 0.0005 x (1 + X/E) and allowances 0.0002 x (1 + X/E) per path (5 + 2 bps/leg)",
               "funding": "PRICE_NET_ONLY (funding coverage EMPTY_UNKNOWN); total_net unavailable",
               "calls": len(allc), "closed": len(closed), "no_entry": sum(1 for x in allc if x["primary_status"] == "NO_ENTRY"),
               "undetermined": {s: sum(1 for x in undet if x["primary_status"] == s) for s in UNDETERMINED},
               "complete": not undet, "sum_price_net_closed": str(total),
               "result": (str(total) if not undet else f"SUBTOTAL_ONLY {total} (undetermined paths: "
                          + ", ".join(f"{x['call_id']} {x['primary_status']}" for x in undet) + ")")}
    rp = ((report.get("outcomes") or {}).get("PRIMARY")) or {}
    c["report v7 PRIMARY section = this tabulation (paths, no entry, closed sum)"] = (
        rp.get("paths") == len(allc) and rp.get("no_entry") == primary["no_entry"]
        and Decimal(rp.get("sum_price_net") or "0") == total)
    c["reconciliation: calls = closed + no entry + undetermined"] = (
        len(allc) == len(closed) + primary["no_entry"] + len(undet))
    out = {"label": label, "windows": {"warmup_start": eng["warmup_start"], "eval_start": eng["eval_start"],
                                       "eval_end": eng["eval_end"], "tail_end": eng["tail_end"],
                                       "clock_end": eng["clock_end"]},
           "run": {k: man[k] for k in ("pack_id", "pack_manifest_sha256", "cache_id", "feed_content_identity",
                                       "build", "events_applied", "journal_entries", "records", "elapsed_seconds")},
           "families": fam, "calls_outside_evaluation": [x["call_id"] for x in rows if x["issue_window"] != "evaluation"],
           "primary": primary, "report_primary": {k: rp.get(k) for k in ("paths", "no_entry", "target_exits",
                                                                       "stop_exits", "sum_price_net",
                                                                       "sum_stress_price_net", "total_net",
                                                                       "ambiguous", "censored", "unresolved")},
           "checks": c, "all_pass": all(c.values())}
    return out, rows


def calls_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = list(rows[0]) if rows else ["call_id"]
    w.writerow(cols)
    for r in rows:
        w.writerow([json.dumps(r[k], sort_keys=True) if isinstance(r[k], (dict, list)) else r[k] for k in cols])
    return buf.getvalue()


if __name__ == "__main__":
    label, run_dir, v06, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    res, rows = run(label, run_dir, v06)
    out.mkdir(parents=True, exist_ok=True)
    files = {"results.json": json.dumps(res, indent=1, sort_keys=True, default=str) + "\n", "calls.csv": calls_csv(rows)}
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
        print(name, hashlib.sha256(text.encode()).hexdigest())
    print("ALL PASS" if res["all_pass"] else "CHECK FAILURE")
