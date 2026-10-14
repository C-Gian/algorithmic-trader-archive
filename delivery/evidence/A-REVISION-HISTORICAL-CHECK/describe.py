"""Supplementary description of how the published A formulations change (NOT registered; computed after the registered
tabulation, from ``out/formulations.csv`` and ``out/scenarios.csv`` only - no journal, bar, engine or new data).

Levels in q = direction x price (a deeper LONG reaction lowers R_q; SHORT mirrored). Medians and ranges only; no group is
compared with another as evidence of an advantage.

  python describe.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from statistics import median

OUT = Path(__file__).resolve().parent / "out"


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def stats(xs: list) -> dict:
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "median": float(median(xs)), "min": float(min(xs)), "max": float(max(xs))}


def main() -> None:
    rows = list(csv.DictReader((OUT / "formulations.csv").open(encoding="utf-8")))
    scen = {r["scenario_id"]: r for r in csv.DictReader((OUT / "scenarios.csv").open(encoding="utf-8"))}
    res = {}
    for window in ("evaluation", "warmup"):
        per = defaultdict(list)
        for r in rows:
            if r["window"] == window:
                per[r["scenario_id"]].append(r)
        b_const = all(len({r["B"] for r in v}) == 1 for v in per.values())
        shift = defaultdict(lambda: defaultdict(list))
        dist = defaultdict(list)
        gap_minutes, gap_by_end = [], Counter()
        for sid, v in per.items():
            d = 1 if scen[sid]["direction"] == "LONG" else -1
            forms = [r for r in v if r["kind"] == "FORMULATION"]
            for r in forms:
                dist[r["transition"]].append((Decimal(r["B"]) - Decimal(r["T"])) * d)
            for prev, cur in zip(forms, forms[1:]):
                for k in ("K", "R", "V"):
                    shift[cur["transition"]][k].append((Decimal(cur[k]) - Decimal(prev[k])) * d)
            for r in v:
                if r["kind"] == "OBSERVATION_GAP" and r["ended_at"]:
                    gap_minutes.append((dt(r["ended_at"]) - dt(r["published_at"])).total_seconds() / 60)
                    gap_by_end[r["end_category"]] += 1
        conf_epoch = Counter(int(s["confirmed_epoch"]) for s in scen.values()
                             if s["window"] == window and s["confirmed_epoch"])
        forms_unconf = Counter(int(s["formulations"]) for s in scen.values()
                               if s["window"] == window and s["category"] == "ARMED_NEVER_CONFIRMED")
        res[window] = {
            "destination B identical across every formulation of each scenario": b_const,
            "level shift from the previous formulation, q units (deeper reaction < 0)": {
                t: {k: stats(v) for k, v in sorted(ks.items())} for t, ks in sorted(shift.items())},
            "B_q - T_q at publication, q units (<= 0: derived incompatible)": {t: stats(v) for t, v in sorted(dist.items())},
            "observation gap length, minutes (publication of the loss to its end)": stats(gap_minutes),
            "confirmed epoch (1 = first ARM)": dict(sorted(conf_epoch.items())),
            "formulations per armed never-confirmed scenario": dict(sorted(forms_unconf.items())),
        }
    text = json.dumps(res, indent=1, sort_keys=True) + "\n"
    (OUT / "supplementary.json").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
