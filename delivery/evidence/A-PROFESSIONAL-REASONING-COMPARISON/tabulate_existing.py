"""Descriptive counts for the A professional-reasoning comparison (12 October 2026).

Reads ONLY two artifacts already committed and reviewed; no data, replay, price or Owner stack:
* ``A-REACTION-EFFICIENCY-EXPLORATION/results.json`` (v0.6, Sep-Dec 2025): per armed A owner, the engine scenario
  transitions after its first ARM (complete to the terminal), and every owner's birth time/side;
* ``WP-012-OWNER-Q4-DIAGNOSIS/confirmations.csv`` (v0.4, Oct-Dec 2025): R, K, S15 and the scenario terminal of the 64
  A confirmations. The v0.4 anchor/confirmation rules are those of v0.6 (v0.5/v0.6 change only the entry child).

Outputs counts.json next to this script. Counts are engine records, not price outcomes or results of calls.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def v06_lifecycles() -> dict:
    owners = json.loads((EVIDENCE / "A-REACTION-EFFICIENCY-EXPLORATION" / "results.json").read_text(encoding="utf-8"))
    owners = owners["owners"]
    births = sorted((o["side"], ts(o["birth_published"])) for o in owners)
    armed = [o for o in owners if o["status"] != "NEVER_ARMED"]
    with_transition: Counter = Counter()
    confirmed_after: Counter = Counter()
    confirmed_terminal: Counter = Counter()
    unconfirmed_terminal: Counter = Counter()
    gaps = []
    for o in armed:
        ann = o["annotations_engine_after_cutoff"]
        seq = [e["transition"] for e in ann]
        with_transition.update(set(seq))
        last = ann[-1]
        if last["transition"] != "TERMINAL":
            raise SystemExit(f"{o['scenario_id']}: lifecycle without a terminal")
        end = f"{last['terminal']}:{last['reason'].split(':')[0]}"
        if "CONFIRM" not in seq:
            unconfirmed_terminal[end] += 1
            continue
        before = seq[:seq.index("CONFIRM")]
        confirmed_after["AFTER_REARM" if "REARM" in before else
                        "AFTER_REVISE" if "REVISE" in before else "ON_FIRST_ANCHOR"] += 1
        confirmed_terminal[end] += 1
        if last["terminal"] == "INVALIDATED":
            t = ts(last["clock"])
            nxt = [b for side, b in births if side == o["side"] and b > t]
            gaps.append(int((nxt[0] - t).total_seconds() // 60) if nxt else None)
    known = sorted(g for g in gaps if g is not None)
    return {
        "source": "A-REACTION-EFFICIENCY-EXPLORATION/results.json (v0.6, owners born Sep-Dec 2025)",
        "owners": len(owners), "armed": len(armed),
        "armed_owners_with_transition": dict(sorted(with_transition.items())),
        "confirmed": sum(confirmed_terminal.values()),
        "confirmed_by_anchor_history": dict(sorted(confirmed_after.items())),
        "confirmed_terminal": dict(sorted(confirmed_terminal.items())),
        "unconfirmed_terminal": dict(sorted(unconfirmed_terminal.items())),
        "after_confirmed_v_contact": {
            "count": len(gaps),
            "minutes_to_next_same_side_A_birth_sorted": known,
            "without_later_same_side_birth": sum(1 for g in gaps if g is None),
            "next_birth_within_120_min": sum(1 for g in known if g <= 120),
            "next_birth_within_240_min": sum(1 for g in known if g <= 240),
        },
    }


def q4_trigger_distance() -> dict:
    path = EVIDENCE / "WP-012-OWNER-Q4-DIAGNOSIS" / "confirmations.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    ratios = sorted(abs(Decimal(r["K_trigger"]) - Decimal(r["R"])) / Decimal(r["S15"]) for r in rows)
    n = len(ratios)
    med = (ratios[(n - 1) // 2] + ratios[n // 2]) / 2
    q = lambda x: str(x.quantize(Decimal("0.001")))  # noqa: E731
    return {
        "source": "WP-012-OWNER-Q4-DIAGNOSIS/confirmations.csv (v0.4, A confirmations Oct-Dec 2025)",
        "confirmations": n,
        "K_minus_R_over_S15": {"min": q(ratios[0]), "median": q(med), "max": q(ratios[-1]),
                               "at_most_1": sum(1 for x in ratios if x <= 1)},
        "scenario_terminal": dict(sorted(Counter(r["scenario_terminal"].split(":")[0] for r in rows).items())),
    }


def main() -> None:
    out = {"v06_sep_dec_2025": v06_lifecycles(), "v04_q4_2025": q4_trigger_distance()}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    (HERE / "counts.json").write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
