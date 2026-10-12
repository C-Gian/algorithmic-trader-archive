"""A reaction directional efficiency: descriptive exploration of E, September-December 2025 (exposed development data).

Reads ONLY the outputs of the single offline v0.6 processing (``run_v06_offline.py``): the professional journal and
the admitted trade 1m bars (``available_time``). Conventions are those registered in ``REGISTRATION.md`` before any
outcome was produced; the measure and the outcome classifier are the identified functions of the feasibility script
(``../A-REACTION-EFFICIENCY-FEASIBILITY/feasibility.py`` at ``6a0f22a``: ``Bar1``, ``tq``, ``agg15``, ``prefix_at``,
``outcome``), imported unchanged. Only E is kept at exact rational precision (the feasibility ``efficiency`` rounds to
5 decimals for display; rounding never decides a tie here).

* Population: every A owner (scenario id ``AL-``/``AS-``) whose BIRTH is published in [2025-09-01, 2026-01-01), LONG
  and SHORT. One observation per owner, at its first ARM publication (the cutoff). No selection by later
  confirmation, call or entry; REVISE/REARM create nothing.
* E at the cutoff: (q0 - qn) / sum |qj - q(j-1)| over the admitted 1m closes (start >= origin, end <= cutoff,
  known_at <= cutoff), q = d * price, q0 = source bar close. Statuses VALUE / UNDEFINED_ZERO_DENOMINATOR /
  INSUFFICIENT_DATA / INCOMPLETE_MISSING_MINUTE.
* Stratum: (age in 15m bars, phase, class of dB/S15, class of dP/S15); class k = floor(x / 0.25), i.e.
  [0.25 k, 0.25 (k + 1)), lower edge included, upper excluded, anchored at zero (negative k allowed); exact
  arithmetic; S15 frozen at birth.
* Outcome: ``outcome()`` with Bq, premise (15m close_q <= Aq + z) and horizon (birth + 120 min) frozen at the cutoff.
* Somers' D of Y on E, standard sign: pairs in the same stratum; E ties excluded and counted; Y ties in the
  denominator; d = (sum C - sum D) / (sum C + sum D + sum T); no denominator -> NOT_ESTIMABLE.

Run from the repository root:
  .venv/Scripts/python.exe delivery/evidence/A-REACTION-EFFICIENCY-EXPLORATION/explore_e.py <run_out_dir>
  .venv/Scripts/python.exe delivery/evidence/A-REACTION-EFFICIENCY-EXPLORATION/explore_e.py --selftest
"""

from __future__ import annotations

import bisect
import csv
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "A-REACTION-EFFICIENCY-FEASIBILITY"))

import feasibility as F  # noqa: E402  (identified functions, unchanged)
from feasibility import Bar1, agg15, outcome, prefix_at, tq  # noqa: E402

D = Decimal
MIN, M15 = timedelta(minutes=1), timedelta(minutes=15)
HORIZON = timedelta(minutes=120)
BIN = Fraction(1, 4)
POP_START = datetime.fromisoformat("2025-09-01T00:00:00+00:00")
POP_END = datetime.fromisoformat("2026-01-01T00:00:00+00:00")
Y_OF = {"B_BEFORE_PREMISE_FAILURE": 1, "PREMISE_FAILURE_BEFORE_B": 0, "HORIZON_OBSERVED_NO_B": 0}


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def iso(t):
    return F.iso(t)


def fmt(x: Fraction | None, n: int = 12) -> str | None:
    if x is None:
        return None
    return str((D(x.numerator) / D(x.denominator)).quantize(D(1).scaleb(-n)))


# ----------------------------------------------------------------------------------------------------------------------
# inputs
# ----------------------------------------------------------------------------------------------------------------------

def read_run(out: Path):
    """Stream the journal keeping A scenario records, market views and calls; read the trade bars."""
    scen: dict[str, list[dict]] = defaultdict(list)
    views: list[tuple[datetime, int, str | None, str | None]] = []
    calls: list[dict] = []
    with gzip.open(out / "journal.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            k = e["kind"]
            if k == "scenario" and e["record"]["scenario_id"][:3] in ("AL-", "AS-"):
                scen[e["record"]["scenario_id"]].append(e)
            elif k == "market_view":
                r = e["record"]
                views.append((dt(e["clock_time"]), e["seq"], r.get("phase"), r.get("observed_context")))
            elif k == "call":
                r = e["record"]
                calls.append({"clock": e["clock_time"], "call_id": r.get("call_id"),
                              "scenario_id": r.get("scenario_id")})
    bars, gaps = [], []
    with gzip.open(out / "trade_bars.csv.gz", "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["kind"] == "bar":
                bars.append(Bar1(dt(r["start"]), dt(r["end"]), dt(r["available_time"]), D(r["open"]), D(r["high"]),
                                 D(r["low"]), D(r["close"])))
            else:
                gaps.append(dt(r["start"]))
    bars.sort(key=lambda b: b.start)
    return scen, views, calls, bars, sorted(gaps)


# ----------------------------------------------------------------------------------------------------------------------
# per owner
# ----------------------------------------------------------------------------------------------------------------------

def e_exact(q0: Decimal, qs: list[Decimal]) -> dict:
    if not qs:
        return {"status": "INSUFFICIENT_DATA", "E": None, "n": 0}
    tv = sum((abs(b - a) for a, b in zip([q0] + qs, qs)), D(0))
    if tv == 0:
        return {"status": "UNDEFINED_ZERO_DENOMINATOR", "E": None, "n": len(qs)}
    return {"status": "VALUE", "E": Fraction(q0 - qs[-1]) / Fraction(tv), "n": len(qs), "net": str(q0 - qs[-1]),
            "tv": str(tv)}


class Bars:
    def __init__(self, bars: list[Bar1], gaps: list[datetime]) -> None:
        self.bars, self.starts, self.gaps = bars, [b.start for b in bars], gaps

    def window(self, a: datetime, b: datetime):
        i, j = bisect.bisect_left(self.starts, a), bisect.bisect_left(self.starts, b)
        gi, gj = bisect.bisect_left(self.gaps, a), bisect.bisect_left(self.gaps, b)
        return self.bars[i:j], self.gaps[gi:gj]


def observe_owner(sid: str, recs: list[dict], views, calls, bx: Bars) -> dict:
    d = 1 if sid.startswith("AL-") else -1
    side = "LONG" if d > 0 else "SHORT"
    births = [e for e in recs if e["record"]["transition"] == "BIRTH"]
    birth = births[0]
    born = dt(birth["clock_time"])
    rec = birth["record"]
    lifecycle = [{"clock": e["clock_time"], "transition": e["record"]["transition"], "reason": e["record"]["reason"],
                  "terminal": e["record"]["terminal_state"]} for e in recs]
    out = {"scenario_id": sid, "side": side, "birth_published": iso(born), "births_recorded": len(births)}
    origin = born.replace(second=0, microsecond=0)  # end of the source 15m bar (modeled availability = bar end)
    out["origin"] = iso(origin)
    out["origin_on_15m_grid"] = origin.minute % 15 == 0 and origin == dt(sid.split("-", 1)[1].rsplit("-", 1)[0]) + M15
    arms = [e for e in recs if e["record"]["transition"] == "ARM"]
    out["arm_records"] = len(arms)
    if not arms:
        last = lifecycle[-1]
        out["status"] = "NEVER_ARMED"
        out["never_armed_end"] = (f"{last['terminal']}:{last['reason']}" if last["terminal"] else
                                  f"OPEN_AT_CLOCK_END:{last['transition']}")
        out["lifecycle"] = lifecycle
        return out
    arm = arms[0]
    cut = dt(arm["clock_time"])
    ar = arm["record"]
    horizon = born + HORIZON
    lo_t, hi_t = origin - 2 * HORIZON, horizon + 2 * HORIZON
    bars, gaps = bx.window(lo_t, hi_t)
    src = [agg15(bars, origin - M15 * (k + 1)) for k in range(7)]
    out["status"] = "ARMED"
    out["cutoff"] = iso(cut)
    out["checks"] = {
        "first_arm_equals_destination_monitoring_from": str(ar.get("destination_monitoring_from")) in (iso(cut),
                                                                                                        str(cut)),
        "horizon_equals_original_expiry": dt(str(ar["original_expiry"])) == horizon,
        "only_birth_before_cutoff": [x["transition"] for x in lifecycle if dt(x["clock"]) < cut] == ["BIRTH"],
        "source_bars_complete": all(x is not None for x in src),
    }
    if not out["checks"]["source_bars_complete"]:
        out["status"] = "EXCLUDED_SOURCE_INCOMPLETE"
        return out
    aq = min(x[2] if d > 0 else -x[1] for x in src)
    bq = max(x[1] if d > 0 else -x[2] for x in src)
    z, s15 = D(rec["setup"]["zone_halfwidth"]), D(rec["setup"]["s15"])
    q0 = d * src[0][3]
    out["checks"]["Aq_matches_record"] = aq == d * D(rec["setup"]["impulse_A"])
    out["checks"]["Bq_matches_record"] = bq == d * D(rec["setup"]["impulse_B"])
    out.update({"q0": str(q0), "Aq": str(aq), "Bq": str(bq), "zone": str(z), "s15_birth": str(s15),
                "Iq": str(bq - aq)})
    use, missing, crossing = prefix_at(bars, gaps, origin, cut)
    ee = e_exact(q0, [tq(b, d)[3] for b in use])
    if missing:
        ee = {"status": "INCOMPLETE_MISSING_MINUTE", "E": None, "n": len(use), "missing": missing}
    out["checks"]["E_bars_causal"] = all(b.start >= origin and b.end <= cut and b.known_at <= cut for b in use)
    out["checks"]["no_bar_crossing_origin"] = not crossing
    out["E_status"] = ee["status"]
    out["E"] = ee["E"]
    out["E_display"] = fmt(ee["E"], 5)
    out["E_n_bars"] = ee["n"]
    out["E_net_q"], out["E_path_q"] = ee.get("net"), ee.get("tv")
    out["E_last_bar_known_at"] = iso(use[-1].known_at) if use else None
    qc = tq(use[-1], d)[3] if use else None
    pq = aq + z
    view = None
    i = bisect.bisect_right(views, (cut, float("inf"))) - 1
    if i >= 0:
        view = views[i]
    age = int((cut.replace(second=0, microsecond=0) - origin) / M15)
    out["checks"]["age_equals_bars_seen"] = str(age) == str(ar["setup"].get("bars_seen"))
    out["phase"] = view[2] if view else None
    out["phase_view_clock"] = iso(view[0]) if view else None
    out["context_at_cutoff"] = view[3] if view else None
    if qc is not None:
        db, dp = Fraction(bq - qc) / Fraction(s15), Fraction(qc - pq) / Fraction(s15)
        out.update({"age_bars": age, "dB_s15": fmt(db, 6), "dP_s15": fmt(dp, 6),
                    "class_dB": math.floor(db / BIN), "class_dP": math.floor(dp / BIN),
                    "I_s15_descriptive": fmt(Fraction(bq - aq) / Fraction(s15), 6),
                    "R_depth_I_descriptive": fmt(Fraction(bq - d * D(str(ar["reaction_level"]))) / Fraction(bq - aq),
                                                 6)})
    out["frozen_at_cutoff"] = {"Bq": str(bq), "premise_q_15m_close_at_or_below": str(pq), "horizon": iso(horizon)}
    oc = outcome(bars, gaps, d, cut, horizon, bq, pq)
    out["outcome"] = oc
    out["outcome_class"] = oc["class"]
    out["outcome_kind"] = oc.get("kind")
    out["Y"] = Y_OF.get(oc["class"])
    out["annotations_engine_after_cutoff"] = [x for x in lifecycle if dt(x["clock"]) > cut]
    out["annotations_calls"] = [c for c in calls if c["scenario_id"] == sid]
    return out


# ----------------------------------------------------------------------------------------------------------------------
# population flow and the single analysis
# ----------------------------------------------------------------------------------------------------------------------

def key_of(o: dict):
    return (o["age_bars"], o["phase"], o["class_dB"], o["class_dP"])


def somers(eps: list[dict]) -> dict:
    strata: dict[tuple, list[dict]] = defaultdict(list)
    for o in eps:
        strata[key_of(o)].append(o)
    rows, pairs = [], []
    contrib: set[str] = set()
    for k in sorted(strata, key=lambda x: tuple(str(v) for v in x)):
        g = sorted(strata[k], key=lambda o: o["scenario_id"])
        c = dd = t = et = 0
        for a, b in combinations(g, 2):
            if a["E"] == b["E"]:
                et += 1
                continue
            s = (a["E"] - b["E"]) * (a["Y"] - b["Y"])
            kind = "C" if s > 0 else ("D" if s < 0 else "T")
            c, dd, t = c + (kind == "C"), dd + (kind == "D"), t + (kind == "T")
            contrib.update((a["scenario_id"], b["scenario_id"]))
            pairs.append({"stratum": k, "a": a["scenario_id"], "b": b["scenario_id"], "type": kind,
                          "a_window": (a["birth_published"], a["frozen_at_cutoff"]["horizon"]),
                          "b_window": (b["birth_published"], b["frozen_at_cutoff"]["horizon"]),
                          "sides": "".join(sorted((a["side"][0], b["side"][0]))),
                          "months": tuple(sorted((a["birth_published"][:7], b["birth_published"][:7])))})
        ys = Counter(o["Y"] for o in g)
        rows.append({"stratum": {"age_bars": k[0], "phase": k[1], "class_dB": k[2], "class_dP": k[3]},
                     "n": len(g), "Y1": ys.get(1, 0), "Y0": ys.get(0, 0), "distinct_E": len({o["E"] for o in g}),
                     "Y_varies": len(ys) > 1, "C": c, "D": dd, "T": t, "E_tied_pairs_excluded": et,
                     "episodes": [o["scenario_id"] for o in g]})
    sc, sd, st = sum(r["C"] for r in rows), sum(r["D"] for r in rows), sum(r["T"] for r in rows)
    den = sc + sd + st
    for r in rows:
        r["weight"] = None if den == 0 else fmt(Fraction(r["C"] + r["D"] + r["T"], den), 6)
    d = None if den == 0 else Fraction(sc - sd, den)
    return {"strata": rows, "pairs": pairs, "contributing": sorted(contrib), "C": sc, "D": sd, "T": st,
            "denominator": den, "status": "NOT_ESTIMABLE" if den == 0 else "VALUE",
            "d_exact": None if d is None else f"{d.numerator}/{d.denominator}", "d": fmt(d, 6)}


def overlaps(a: tuple[str, str], b: tuple[str, str]) -> bool:
    return dt(a[0]) < dt(b[1]) and dt(b[0]) < dt(a[1])


def describe(eps_all: list[dict], sm: dict) -> dict:
    flow: dict[str, object] = {}
    flow["A_owners_born_in_window"] = len(eps_all)
    flow["by_side"] = dict(Counter(o["side"] for o in eps_all))
    never = [o for o in eps_all if o["status"] == "NEVER_ARMED"]
    flow["never_armed"] = len(never)
    flow["never_armed_by_end"] = dict(Counter(o["never_armed_end"] for o in never).most_common())
    armed = [o for o in eps_all if o["status"] != "NEVER_ARMED"]
    flow["armed"] = len(armed)
    flow["excluded_source_incomplete"] = sum(o["status"] == "EXCLUDED_SOURCE_INCOMPLETE" for o in armed)
    obs = [o for o in armed if o["status"] == "ARMED"]
    flow["E_status"] = dict(Counter(o["E_status"] for o in obs))
    ev = [o for o in obs if o["E_status"] == "VALUE"]
    flow["E_value"] = len(ev)
    flow["outcome_class_all_armed"] = dict(Counter(
        f"{o['outcome_class']}" + (f"/{o['outcome_kind']}" if o.get("outcome_kind") else "") for o in obs))
    flow["outcome_class_E_value"] = dict(Counter(
        f"{o['outcome_class']}" + (f"/{o['outcome_kind']}" if o.get("outcome_kind") else "") for o in ev))
    elig = [o for o in ev if o["Y"] is not None]
    flow["excluded_after_E_outcome_not_Y"] = len(ev) - len(elig)
    flow["eligible"] = len(elig)
    flow["eligible_Y1_Y0"] = [sum(o["Y"] == 1 for o in elig), sum(o["Y"] == 0 for o in elig)]
    singletons = [r for r in sm["strata"] if r["n"] == 1]
    flow["strata"] = len(sm["strata"])
    flow["strata_singleton"] = len(singletons)
    flow["strata_multi"] = len(sm["strata"]) - len(singletons)
    flow["strata_multi_without_Y_variation"] = sum(1 for r in sm["strata"] if r["n"] > 1 and not r["Y_varies"])
    flow["strata_multi_without_E_variation"] = sum(1 for r in sm["strata"] if r["n"] > 1 and r["distinct_E"] == 1)
    flow["episodes_contributing"] = len(sm["contributing"])
    flow["episodes_without_usable_comparison"] = len(elig) - len(sm["contributing"])
    flow["E_tied_pairs_excluded"] = sum(r["E_tied_pairs_excluded"] for r in sm["strata"])
    flow["reconciliation"] = {
        "born = never_armed + armed": len(eps_all) == len(never) + len(armed),
        "armed = source_incomplete + observed": len(armed) == flow["excluded_source_incomplete"] + len(obs),
        "observed = sum(E_status)": len(obs) == sum(flow["E_status"].values()),
        "E_value = eligible + excluded_outcome": len(ev) == len(elig) + flow["excluded_after_E_outcome_not_Y"],
        "eligible = sum(stratum n)": len(elig) == sum(r["n"] for r in sm["strata"]),
        "eligible = contributing + without_comparison": len(elig) == len(sm["contributing"]) +
        flow["episodes_without_usable_comparison"],
        "pairs = C + D + T": len(sm["pairs"]) == sm["denominator"],
    }
    # temporal concentration and overlap (descriptive; pairs are not independent observations)
    byid = {o["scenario_id"]: o for o in elig}
    contrib = [byid[s] for s in sm["contributing"]]
    conc = {"contributing_by_birth_month": dict(sorted(Counter(o["birth_published"][:7] for o in contrib).items())),
            "eligible_by_birth_month": dict(sorted(Counter(o["birth_published"][:7] for o in elig).items())),
            "contributing_by_iso_week": dict(sorted(Counter(
                "%d-W%02d" % dt(o["birth_published"]).isocalendar()[:2] for o in contrib).items()))}
    per_ep = Counter()
    for p in sm["pairs"]:
        per_ep[p["a"]] += 1
        per_ep[p["b"]] += 1
    conc["pairs_per_contributing_episode_top10"] = per_ep.most_common(10)
    conc["pairs_by_month_pair"] = {f"{a}|{b}": dict(Counter(p["type"] for p in sm["pairs"] if p["months"] == (a, b)))
                                   for a, b in sorted({p["months"] for p in sm["pairs"]})}
    ov = [p for p in sm["pairs"] if overlaps(p["a_window"], p["b_window"])]
    conc["pairs_with_overlapping_observation_windows"] = {"n": len(ov), "by_type": dict(Counter(p["type"] for p in ov)),
                                                          "by_sides": dict(Counter(p["sides"] for p in ov))}
    conc["pairs_by_sides"] = {s: dict(Counter(p["type"] for p in sm["pairs"] if p["sides"] == s))
                              for s in sorted({p["sides"] for p in sm["pairs"]})}
    ov_ep = sum(1 for o in elig if any(overlaps((o["birth_published"], o["frozen_at_cutoff"]["horizon"]),
                                                (x["birth_published"], x["frozen_at_cutoff"]["horizon"]))
                                       for x in elig if x is not o))
    conc["eligible_episodes_overlapping_another_eligible"] = ov_ep
    top = sorted(sm["strata"], key=lambda r: -(r["C"] + r["D"] + r["T"]))[:5]
    conc["top5_strata_share_of_pairs"] = None if not sm["denominator"] else fmt(
        Fraction(sum(r["C"] + r["D"] + r["T"] for r in top), sm["denominator"]), 6)
    return {"flow": flow, "concentration_and_overlap": conc}


def explore(scen, views, calls, bars, gaps) -> dict:
    bx = Bars(bars, gaps)
    owners = []
    dup_birth = []
    for sid, recs in sorted(scen.items()):
        b = [e for e in recs if e["record"]["transition"] == "BIRTH"]
        if len(b) != 1:
            dup_birth.append(sid)
        if not b:
            continue
        born = dt(b[0]["clock_time"])
        if POP_START <= born < POP_END:
            owners.append(observe_owner(sid, recs, views, calls, bx))
    obs = [o for o in owners if o["status"] == "ARMED"]
    elig = [o for o in obs if o["E_status"] == "VALUE" and o["Y"] is not None]
    sm = somers(elig)
    desc = describe(owners, sm)
    checks = {
        "one_birth_per_owner": not dup_birth,
        "one_observation_per_owner": len({o["scenario_id"] for o in owners}) == len(owners),
        "per_owner_checks_all_true": {k: sum(1 for o in obs if not o["checks"].get(k)) for k in
                                      sorted({k for o in obs for k in o["checks"]})},
        "origin_on_15m_grid_and_matches_id": sum(1 for o in owners if not o["origin_on_15m_grid"]),
        "horizon_within_authorized_tail": all(dt(o["frozen_at_cutoff"]["horizon"]) <= dt("2026-01-01T06:05:00Z")
                                              for o in obs),
        "trade_gaps_in_input": len(gaps),
        "reconciliation_all_true": all(desc["flow"]["reconciliation"].values()),
    }
    return {"owners": owners, "somers": sm, **desc, "checks": checks}


# ----------------------------------------------------------------------------------------------------------------------
# outputs
# ----------------------------------------------------------------------------------------------------------------------

def jsonable(x):
    if isinstance(x, Fraction):
        return f"{x.numerator}/{x.denominator}"
    if isinstance(x, tuple):
        return list(x)
    return str(x)


def write(res: dict, dest: Path) -> None:
    owners = res["owners"]
    cols = ["scenario_id", "side", "birth_published", "status", "never_armed_end", "cutoff", "E_status", "E_display",
            "E", "E_n_bars", "age_bars", "phase", "class_dB", "class_dP", "dB_s15", "dP_s15", "I_s15_descriptive",
            "R_depth_I_descriptive", "context_at_cutoff", "outcome_class", "outcome_kind", "Y"]
    with (dest / "episodes.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for o in owners:
            w.writerow([jsonable(o.get(c)) if isinstance(o.get(c), Fraction) else
                        ("" if o.get(c) is None else o.get(c)) for c in cols])
    with (dest / "strata.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["age_bars", "phase", "class_dB", "class_dP", "n", "Y1", "Y0", "distinct_E", "Y_varies", "C", "D",
                    "T", "E_tied_pairs_excluded", "weight"])
        for r in res["somers"]["strata"]:
            s = r["stratum"]
            w.writerow([s["age_bars"], s["phase"], s["class_dB"], s["class_dP"], r["n"], r["Y1"], r["Y0"],
                        r["distinct_E"], r["Y_varies"], r["C"], r["D"], r["T"], r["E_tied_pairs_excluded"],
                        "" if r["weight"] is None else r["weight"]])
    doc = {"purpose": "A reaction directional efficiency: descriptive exploration of E, Sep-Dec 2025 (exposed "
                      "development data; no test, interval or economic result)",
           "flow": res["flow"], "somers": {k: v for k, v in res["somers"].items() if k != "pairs"},
           "pairs": res["somers"]["pairs"], "concentration_and_overlap": res["concentration_and_overlap"],
           "checks": res["checks"], "owners": owners}
    (dest / "results.json").write_text(json.dumps(doc, indent=1, default=jsonable) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------------------------------------
# synthetic self-test (engineering inputs only; run before the registration and before any real outcome)
# ----------------------------------------------------------------------------------------------------------------------

def selftest() -> None:
    ok = []
    # 1. the feasibility engine paths through this pipeline: same E, key and outcome as the feasibility results
    ref = {(e["episode"], e["side"]): e for e in
           json.loads((HERE.parent / "A-REACTION-EFFICIENCY-FEASIBILITY" / "results.json").read_text())["episodes"]}
    for side in ("LONG", "SHORT"):
        for p, c in [("BASE", "B"), ("BASE", "F"), ("BASE", "H"), ("BASE", "G"), ("BASE", "X"), ("FRONT", "B"),
                     ("ALT", "B"), ("GAP", "H")]:
            j, bars, gaps = F.run_historical(F.tape(p, c, side))
            scen = defaultdict(list)
            views = []
            for e in j:
                if e["kind"] == "scenario" and e["record"]["scenario_id"][:3] in ("AL-", "AS-"):
                    scen[e["record"]["scenario_id"]].append(e)
                elif e["kind"] == "market_view":
                    views.append((dt(e["clock_time"]), e["seq"], e["record"]["phase"], e["record"]["observed_context"]))
            res = explore(scen, views, [], sorted(bars, key=lambda b: b.start), gaps)
            own = [o for o in res["owners"] if o["side"] == side][0]
            r = ref[(f"{p}+{c}/historical", side)]
            if r["cutoff"] is None:
                ok.append((f"{p}+{c} {side} never armed", own["status"] == "NEVER_ARMED"))
                continue
            rc = r["comparison"]
            ok.append((f"{p}+{c} {side} E", own["E_display"] == r["E_at_cutoff"]["E"]))
            ok.append((f"{p}+{c} {side} key", (own["age_bars"], own["phase"], own["class_dB"], own["class_dP"]) ==
                       (rc["age_bars"], rc["phase"], rc["bin_dB"], rc["bin_dP"])))
            ok.append((f"{p}+{c} {side} outcome", own["outcome_class"] == r["outcome"]["class"]))
            ok.append((f"{p}+{c} {side} checks", all(own["checks"].values())))
    # 2. Somers' D by hand: the note's worked example, ties, singletons, non-estimable
    def ep(i, e, y, k=(1, "TRANSITION", 1, 5)):
        return {"scenario_id": f"s{i}", "E": Fraction(e), "Y": y, "age_bars": k[0], "phase": k[1], "class_dB": k[2],
                "class_dP": k[3], "birth_published": "2025-09-01T00:00:00Z", "side": "LONG",
                "frozen_at_cutoff": {"horizon": "2025-09-01T02:00:00Z"}}
    s = somers([ep(1, "0.9", 0), ep(2, "0.2", 1)])
    ok.append(("worked example d = -1", s["d_exact"] == "-1/1" and (s["C"], s["D"], s["T"]) == (0, 1, 0)))
    s = somers([ep(1, "0.9", 1), ep(2, "0.2", 0), ep(3, "0.5", 0)])
    ok.append(("C2 D0 T1 -> 2/3", (s["C"], s["D"], s["T"]) == (2, 0, 1) and s["d_exact"] == "2/3"))
    s = somers([ep(1, "0.5", 1), ep(2, "0.5", 0)])
    ok.append(("E tie only -> NOT_ESTIMABLE", s["status"] == "NOT_ESTIMABLE" and
               s["strata"][0]["E_tied_pairs_excluded"] == 1))
    s = somers([ep(1, "0.9", 0), ep(2, "0.2", 0)])
    ok.append(("no Y variation -> tie, d = 0", (s["T"], s["d_exact"]) == (1, "0/1")))
    s = somers([ep(1, "0.9", 0), ep(2, "0.2", 1, k=(2, "TRANSITION", 1, 5))])
    ok.append(("different strata never paired", s["status"] == "NOT_ESTIMABLE"))
    s = somers([ep(1, "0.9", 1), ep(2, "0.2", 0), ep(3, "0.8", 0, k=(1, "X", 0, 0)), ep(4, "0.1", 1, k=(1, "X", 0, 0))])
    ok.append(("aggregate C/D before the ratio (not mean of strata)", (s["C"], s["D"], s["d_exact"]) == (1, 1, "0/1")))
    # 3. class edges: floor, lower edge included, negative classes
    ok.append(("class edges", [math.floor(Fraction(x) / BIN) for x in ("0", "0.2499", "0.25", "-0.01", "-0.25")]
               == [0, 0, 1, -1, -1]))
    for name, v in ok:
        print(f"{'ok ' if v else 'FAIL'} {name}")
    print(f"selftest: {sum(v for _, v in ok)}/{len(ok)}")
    if not all(v for _, v in ok):
        raise SystemExit(1)


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        selftest()
    else:
        out = Path(sys.argv[1])
        res = explore(*read_run(out))
        write(res, HERE)
        print(json.dumps(res["flow"], indent=1, default=str))
        print("checks:", json.dumps(res["checks"], default=str))
