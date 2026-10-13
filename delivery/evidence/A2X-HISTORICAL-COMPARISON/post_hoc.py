"""Descriptive historical comparison v0.6 / v0.6-a2x: POST-HOC descriptive checks (amendment 2, written AFTER the
registered tabulation had been seen; not part of the registered design, changes none of its outputs).

From the saved journals and traces only (no engine run):
1. Market views: for every evaluation-window dispatch whose published views differ (envelopes removed, ids normalized),
   whether it lies inside a variant reservation interval [REVIEW_OPEN, end of the review or of its successor], and which
   top-level view fields differ.
2. Birth-step state: per direction and 15m close of the evaluation window, whether the two policies' traced latch or
   owner occupancy differ; whether any such dispatch had Q_A true (the only way the state difference could change a
   birth); where the differences lie relative to the reservation intervals.

  .venv/Scripts/python.exe delivery/evidence/A2X-HISTORICAL-COMPARISON/post_hoc.py <v06_run_dir> <a2x_run_dir> <out_json>
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from compare import WINDOW, Policy, drop_env, load, norm_ids, zt  # noqa: E402


def intervals(px: Policy) -> list[tuple[str, str, str]]:
    """(start, end, impulse) of every variant reservation: REVIEW_OPEN to REVIEW_CLOSED, or to the successor's last
    record when a successor was armed."""
    out = []
    for e in px.obs:
        r = e["record"]
        if r["category"] != "REVIEW_OPEN":
            continue
        imp = r["values"]["impulse_id"]
        rv = px.review_of(imp)
        if rv["successor"]:
            end = zt(px.scen[rv["successor"]["sid"]][-1]["record"]["env"]["clock_time"])
        else:
            end = rv["closed"]["t"] if rv["closed"] else "~"
        out.append((rv["opened"], end, imp))
    return sorted(out)


def inside(t: str, ivs) -> bool:
    return any(a <= t <= b for a, b, _ in ivs)


def views(p: Policy) -> dict[str, list[dict]]:
    out = defaultdict(list)
    for e in p.journal:
        if e["kind"] == "market_view":
            t = zt(e["record"]["env"]["clock_time"])
            if WINDOW[0] <= t < WINDOW[1]:
                out[t].append(json.loads(norm_ids(json.dumps(drop_env(e["record"]), sort_keys=True, default=str))))
    return out


def main(r6: Path, rx: Path, out: Path) -> None:
    p6, px = Policy("v0.6", *load(r6)), Policy("v0.6-a2x", *load(rx))
    ivs = intervals(px)
    v6, vx = views(p6), views(px)
    diff_t = sorted(t for t in set(v6) | set(vx) if v6.get(t) != vx.get(t))
    fields = Counter()
    for t in diff_t:
        a, b = v6.get(t, []), vx.get(t, [])
        if len(a) != len(b):
            fields["<different number of views in the dispatch>"] += 1
        for x, y in zip(a, b):
            for k in sorted(set(x) | set(y)):
                if x.get(k) != y.get(k):
                    fields[k] += 1
    view_res = {"dispatches_with_difference": len(diff_t),
                "inside_a_reservation_interval": sum(inside(t, ivs) for t in diff_t),
                "outside": [t for t in diff_t if not inside(t, ivs)],
                "differing_top_level_fields": dict(sorted(fields.items()))}

    state = {}
    for d in (1, -1):
        rows = Counter()
        qa_true_when_different = []
        outside = []
        for (t, dd), q6 in sorted(p6.qa.items()):
            if dd != d or not (WINDOW[0] <= t < WINDOW[1]):
                continue
            qx = px.qa.get((t, d))
            s6 = (q6["latch"], q6["owner"] is not None)
            sx = (qx["latch"], qx["owner"] is not None, bool(qx["reserved_for"]) or px.is_successor(qx["owner"]))
            if s6 == sx[:2]:
                rows["same"] += 1
                continue
            rows[f"v0.6 {s6[0]}/{'occupied' if s6[1] else 'free'} vs a2x {sx[0]}/"
                 f"{'reserved' if sx[2] else 'occupied' if sx[1] else 'free'}"] += 1
            if q6["qa"] is True or qx["qa"] is True:
                qa_true_when_different.append(t)
            if not inside(t, ivs):
                outside.append(t)
        state[{1: "LONG", -1: "SHORT"}[d]] = {"by_state_pair": dict(sorted(rows.items())),
                                               "qa_true_at_a_differing_dispatch": qa_true_when_different,
                                               "differing_dispatches_outside_reservation_intervals": outside}
    res = {"amendment": 2, "post_hoc": True, "reservation_intervals": len(ivs),
           "reservation_intervals_in_evaluation": sum(1 for a, _, _ in ivs if WINDOW[0] <= a < WINDOW[1]),
           "market_views": view_res, "birth_step_state": state}
    text = json.dumps(res, indent=1, sort_keys=True) + "\n"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print("sha256", hashlib.sha256(text.encode()).hexdigest())


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
