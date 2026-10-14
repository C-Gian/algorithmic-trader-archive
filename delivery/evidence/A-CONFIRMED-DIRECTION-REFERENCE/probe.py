"""A confirmed direction — fixed-geometry barrier probe against its opposite orientation (v0.6, Sep–Dec 2025).

Registered in REGISTRATION.md before any tabulation. Reads the reused local v0.6 journal and admitted trade 1m bars
only: no engine, replay, extraction or acquisition. Stdlib only, Decimal prices, no tolerance.

At the publication t0 of each scenario's first A CONFIRM: P = the record's confirmation close (checked equal to the close
of the confirming 1m bar, admitted at/before t0), d = the A direction, B = destination, V = invalidation (both from the
CONFIRM record). a = d(B-P), b = d(P-V) must be strictly positive.
  selected orientation A : favourable P + d*a, adverse P - d*b
  opposite orientation O : favourable P - d*a, adverse P + d*b
Each is observed on the complete trade 1m bars of [t0, t0 + 4h). Y = 1 favourable first, 0 adverse first, 0 horizon with
no favourable contact (own category); ambiguity or incompleteness leaves Y undetermined. No intrabar order is inferred.

  python probe.py selftest
  python probe.py run <run_dir> <out_dir>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

WINDOW = ("2025-09-01T00:00:00Z", "2026-01-01T00:00:00Z")
HORIZON = timedelta(hours=4)  # registered A hard horizon (v0.6 register), here a fixed probe horizon
MIN = timedelta(minutes=1)
MINUTE_RID = re.compile(r"#obs@(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)$")
CODE_SEG = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
F, A, H = "F", "A", "H"  # favourable first (Y=1), adverse first (Y=0), horizon with no favourable contact (Y=0)
Y = {F: 1, A: 0, H: 0}


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def zs(t: datetime | None) -> str | None:
    return None if t is None else t.isoformat().replace("+00:00", "Z")


def code(reason: str | None) -> str:
    out = []
    for seg in (reason or "").split(":"):
        if not CODE_SEG.match(seg):
            break
        out.append(seg)
    return ":".join(out)


def window_of(t: str) -> str:
    return "warmup" if t < WINDOW[0] else "evaluation" if t < WINDOW[1] else "tail"


@dataclass(frozen=True)
class Bar:
    start: datetime
    end: datetime
    h: Decimal
    lo: Decimal
    c: Decimal


# ----------------------------------------------------------------------------------------------------------------------
# the barrier walk (joint over orientations; no intrabar order)
# ----------------------------------------------------------------------------------------------------------------------

def walk(bars: dict[datetime, Bar | None], data_end: datetime, t0: datetime, horizon_end: datetime,
         orients: list[tuple[Decimal, Decimal]], p0: Decimal) -> dict:
    """Feasible joint outcomes of ``orients`` (each (favourable level, adverse level)) on the bars of [t0, H).

    A level above the start price is touched by high >= level, a level below by low <= level (as the engine's contacts).
    Bars ending at/before t0 are never outcomes. Inside one bar the order of the touched levels is unknown: every order
    is enumerated (equal levels are one event). A bar straddling t0 or H may hold each touched level outside the window:
    each subset is enumerated too. A missing bar or one beyond the data lets every open orientation become F, A or stay
    open. At H, an open orientation is H; if the data end before H, it may be F, A or H. Returns the set of joint states
    and, per bar where the set branched, the cause."""
    k = len(orients)
    states = {(None,) * k}
    causes: list[str] = []
    resolved_at: dict[int, str] = {}
    m = t0.replace(second=0, microsecond=0)
    while m < horizon_end:
        end = m + MIN
        if end <= t0:
            m = end
            continue
        straddle = m < t0 or end > horizon_end
        bar = bars.get(m) if m < data_end else None
        new: set[tuple] = set()
        cause = None
        for s in states:
            open_ = [i for i, v in enumerate(s) if v is None]
            if not open_:
                new.add(s)
                continue
            if bar is None:
                cause = "INCOMPLETE_DATA_END" if m >= data_end else "INCOMPLETE_MISSING_INTERVAL"
                for combo in itertools.product((F, A, None), repeat=len(open_)):
                    st = list(s)
                    for i, v in zip(open_, combo):
                        st[i] = v
                    new.add(tuple(st))
                continue
            touched = set()
            for i in open_:
                for lvl in orients[i]:
                    if (lvl > p0 and bar.h >= lvl) or (lvl < p0 and bar.lo <= lvl):
                        touched.add(lvl)
            if not touched:
                new.add(s)
                continue
            subsets = ([c for r in range(len(touched) + 1) for c in itertools.combinations(sorted(touched), r)]
                       if straddle else [tuple(sorted(touched))])
            outs = set()
            for sub in subsets:
                for perm in itertools.permutations(sub):
                    st = list(s)
                    for lvl in perm:
                        for i in open_:
                            if st[i] is None:
                                if lvl == orients[i][0]:
                                    st[i] = F
                                elif lvl == orients[i][1]:
                                    st[i] = A
                    outs.add(tuple(st))
            if len(outs) > 1:
                cause = "AMBIGUOUS_STRADDLING_INTERVAL" if straddle else "AMBIGUOUS_SAME_INTERVAL"
            new |= outs
        if len(new) > 1 and cause and (not causes or causes[-1] != f"{cause}@{zs(m)}"):
            causes.append(f"{cause}@{zs(m)}")
        if len(states) == 1 and len(new) == 1:
            (before,), (after,) = states, new
            for i in range(k):
                if before[i] is None and after[i] is not None:
                    resolved_at[i] = zs(m)
        states = new
        m = end
    final = set()
    for s in states:
        open_ = [i for i, v in enumerate(s) if v is None]
        if not open_:
            final.add(s)
        elif data_end >= horizon_end:
            final.add(tuple(H if v is None else v for v in s))
        else:
            if "INCOMPLETE_DATA_END" not in " ".join(causes):
                causes.append(f"INCOMPLETE_DATA_END@{zs(data_end)}")
            for combo in itertools.product((F, A, H), repeat=len(open_)):
                st = list(s)
                for i, v in zip(open_, combo):
                    st[i] = v
                final.add(tuple(st))
    return {"states": final, "causes": causes, "resolved_at": resolved_at}


def probe(bars, data_end, t0, P, a, b, d) -> dict:
    """Both orientations at one confirmation: marginals (category per orientation) and the joint feasible set."""
    sel = (P + d * a, P - d * b)
    opp = (P - d * a, P + d * b)
    horizon_end = t0 + HORIZON
    out = {}
    for name, o in (("A", sel), ("O", opp)):
        w = walk(bars, data_end, t0, horizon_end, [o], P)
        vals = {s[0] for s in w["states"]}
        if len(vals) == 1:
            v = next(iter(vals))
            cat = {F: "FAVOURABLE_FIRST", A: "ADVERSE_FIRST", H: "HORIZON_NO_FAVOURABLE_CONTACT"}[v]
            out[name] = {"Y": Y[v], "category": cat, "resolved_interval": w["resolved_at"].get(0), "reason": None,
                         "favourable": str(o[0]), "adverse": str(o[1])}
        else:
            ys = sorted({Y[v] for v in vals})
            out[name] = {"Y": None, "category": "UNDETERMINED", "resolved_interval": None,
                         "reason": w["causes"][0] if w["causes"] else "UNDETERMINED", "possible_Y": ys,
                         "favourable": str(o[0]), "adverse": str(o[1])}
    joint = walk(bars, data_end, t0, horizon_end, [sel, opp], P)
    diffs = sorted({Fraction(Y[s[0]] - Y[s[1]], 2) for s in joint["states"]})
    out["joint_differences"] = [str(x) for x in diffs]
    out["_dmin"], out["_dmax"] = diffs[0], diffs[-1]
    return out


# ----------------------------------------------------------------------------------------------------------------------
# population and episodes
# ----------------------------------------------------------------------------------------------------------------------

def episodes(journal: list[dict], bars: dict, data_end: datetime) -> list[dict]:
    per: dict[str, list[dict]] = defaultdict(list)
    for e in journal:
        if e["kind"] == "scenario" and e["record"].get("family") == "A":
            per[e["record"]["scenario_id"]].append(e)
    out = []
    for sid, es in per.items():
        es.sort(key=lambda e: e["seq"])
        born = es[0]["clock_time"]
        conf = next((e for e in es if e["record"]["transition"] == "CONFIRM"), None)
        if conf is None:
            continue
        r = conf["record"]
        term = next((e for e in es if e["record"]["transition"] == "TERMINAL"), None)
        d = 1 if r["direction"] == "LONG" else -1
        t0 = dt(conf["clock_time"])
        ep = {"scenario_id": sid, "window": window_of(born), "born_at": born, "direction": r["direction"],
              "confirmed_epoch": r.get("anchor_epoch"), "cutoff": conf["clock_time"], "cutoff_cursor": conf["factual_cursor"],
              "horizon_end": zs(t0 + HORIZON), "confirmed_deadline": r.get("confirmed_deadline"),
              "P": r.get("confirmation_close"), "B": r.get("destination"), "V": r.get("invalidation_level"),
              "native_terminal": f"{term['record'].get('terminal_state')}:{code(term['record'].get('reason'))}" if term
              else "OPEN_AT_DATA_END", "native_terminal_at": term["clock_time"] if term else None,
              "status": None, "reason": None}
        m = MINUTE_RID.search(r.get("reason") or "")
        bar = bars.get(dt(m.group(1))) if m else None
        if None in (ep["P"], ep["B"], ep["V"]) or bar is None:
            ep["status"], ep["reason"] = "NOT_EVALUABLE", "essential evidence unavailable (P, B, V or the confirming bar)"
            out.append(ep)
            continue
        P, B, V = Decimal(ep["P"]), Decimal(ep["B"]), Decimal(ep["V"])
        ep["P_bar"], ep["P_bar_end"] = zs(bar.start), zs(bar.end)
        if bar.c != P or bar.end > t0:
            ep["status"], ep["reason"] = "NOT_EVALUABLE", "P is not the close of a bar admitted at/before the cutoff"
            out.append(ep)
            continue
        a, b = d * (B - P), d * (P - V)
        ep["a"], ep["b"] = str(a), str(b)
        if a <= 0 or b <= 0:
            ep["status"], ep["reason"] = "INVALID_GEOMETRY", f"a = {a}, b = {b} (both must be > 0)"
            out.append(ep)
            continue
        ep["status"] = "VALID_GEOMETRY"
        res = probe(bars, data_end, t0, P, a, b, d)
        ep["A"], ep["O"] = res["A"], res["O"]
        ep["joint_differences"] = res["joint_differences"]
        ep["_dmin"], ep["_dmax"] = res["_dmin"], res["_dmax"]
        yA, yO = res["A"]["Y"], res["O"]["Y"]
        ep["pair"] = "DETERMINED" if yA is not None and yO is not None else (
            "UNRESOLVED_BOTH" if yA is None and yO is None else "UNRESOLVED_A_ONLY" if yA is None else "UNRESOLVED_O_ONLY")
        if ep["pair"] == "DETERMINED":
            ep["reference"] = str(Fraction(yA + yO, 2))
            ep["difference"] = str(Fraction(yA - yO, 2))
        out.append(ep)
    return sorted(out, key=lambda e: (e["cutoff"], e["scenario_id"]))


def overlap(eps: list[dict]) -> dict:
    """Overlap of the probe windows [cutoff, cutoff + 4h) and temporal concentration (descriptive)."""
    xs = sorted(((dt(e["cutoff"]), dt(e["horizon_end"]), e) for e in eps), key=lambda x: x[0])
    n_over, opp = [], 0
    for i, (s, t, e) in enumerate(xs):
        others = [x for j, x in enumerate(xs) if j != i and x[0] < t and s < x[1]]
        e["overlapping_windows"] = len(others)
        n_over.append(len(others))
        opp += any(x[2]["direction"] != e["direction"] for x in others)
    clusters, cur, cur_end = [], [], None
    for s, t, e in xs:
        if cur and s < cur_end:
            cur.append(e)
            cur_end = max(cur_end, t)
        else:
            if cur:
                clusters.append(cur)
            cur, cur_end = [e], t
    if cur:
        clusters.append(cur)
    by_month = Counter(e["cutoff"][:7] for e in eps)
    by_day = Counter(e["cutoff"][:10] for e in eps)
    return {"episodes": len(eps), "with_at_least_one_overlapping_window": sum(1 for n in n_over if n),
            "with_an_overlapping_opposite_direction_window": opp,
            "overlap_count_distribution": dict(sorted(Counter(n_over).items())),
            "clusters_of_overlapping_windows": len(clusters),
            "cluster_size_distribution": dict(sorted(Counter(len(c) for c in clusters).items())),
            "by_month": dict(sorted(by_month.items())), "distinct_days": len(by_day),
            "max_per_day": max(by_day.values()) if by_day else 0,
            "days_with_3_or_more": sum(1 for v in by_day.values() if v >= 3)}


def tables(eps: list[dict]) -> dict:
    valid = [e for e in eps if e["status"] == "VALID_GEOMETRY"]
    det = [e for e in valid if e["pair"] == "DETERMINED"]
    t = {"first_confirmations": len(eps), "status": dict(sorted(Counter(e["status"] for e in eps).items())),
         "not_evaluable_or_invalid": [{"scenario_id": e["scenario_id"], "status": e["status"], "reason": e["reason"]}
                                      for e in eps if e["status"] != "VALID_GEOMETRY"],
         "by_direction": dict(sorted(Counter(e["direction"] for e in valid).items())),
         "outcomes_selected_A": dict(sorted(Counter(e["A"]["category"] for e in valid).items())),
         "outcomes_opposite_O": dict(sorted(Counter(e["O"]["category"] for e in valid).items())),
         "undetermined_reasons": dict(sorted(Counter(
             f"{k}:{e[k]['reason'].split('@')[0]}" for e in valid for k in ("A", "O") if e[k]["Y"] is None).items())),
         "pairs": dict(sorted(Counter(e["pair"] for e in valid).items()))}
    t["paired_2x2_determined"] = {f"Y_A={ya},Y_O={yo}": sum(1 for e in det if e["A"]["Y"] == ya and e["O"]["Y"] == yo)
                                  for ya in (1, 0) for yo in (1, 0)}
    t["paired_2x2_with_categories"] = dict(sorted(Counter(
        f"A:{e['A']['category']} | O:{e['O']['category']}" for e in det).items()))
    n = len(det)
    if n:
        sa, so = sum(e["A"]["Y"] for e in det), sum(e["O"]["Y"] for e in det)
        mean = Fraction(sa - so, 2 * n)
        t["determined_pairs"] = {"n": n, "selected_favourable_first": sa, "opposite_favourable_first": so,
                                 "reference_total": str(Fraction(sa + so, 2)),
                                 "mean_reference": str(Fraction(sa + so, 2 * n)),
                                 "mean_difference": str(mean),
                                 "mean_difference_percentage_points": f"{float(mean) * 100:.2f}"}
    nv = len(valid)
    if nv and len(det) < nv:
        lo = sum((e["_dmin"] for e in valid), Fraction(0)) / nv
        hi = sum((e["_dmax"] for e in valid), Fraction(0)) / nv
        t["bounds_over_all_valid_geometry"] = {"n": nv, "lower": str(lo), "upper": str(hi),
                                               "lower_pp": f"{float(lo) * 100:.2f}", "upper_pp": f"{float(hi) * 100:.2f}"}
    t["overlap_and_concentration"] = overlap(valid)
    return t


def checks(eps: list[dict], journal: list[dict], bars: dict, data_end: datetime) -> dict:
    confs = Counter(e["record"]["scenario_id"] for e in journal if e["kind"] == "scenario"
                    and e["record"].get("family") == "A" and e["record"]["transition"] == "CONFIRM")
    c = {"one episode per confirmed A scenario (first and only CONFIRM)": (
        len(eps) == len(confs) and all(v == 1 for v in confs.values())
        and sorted(e["scenario_id"] for e in eps) == sorted(confs)),
         "no tail-window birth": not any(e["window"] == "tail" for e in eps),
         "P = close of the confirming bar, admitted at/before the cutoff": all(
             e["status"] != "NOT_EVALUABLE" for e in eps),
         "horizon = cutoff + 4h = the record's confirmed_deadline": all(
             e["horizon_end"] == e["confirmed_deadline"] for e in eps),
         "every probe window wholly inside the bar data, no missing interval": all(
             dt(e["horizon_end"]) <= data_end and all(bars.get(dt(e["cutoff"]) + i * MIN) is not None
                                                      for i in range(int(HORIZON / MIN)))
             for e in eps)}
    valid = [e for e in eps if e["status"] == "VALID_GEOMETRY"]
    c["each determined orientation resolved inside its window or by the horizon"] = all(
        e[k]["category"] == "HORIZON_NO_FAVOURABLE_CONTACT" or (
            e[k]["resolved_interval"] and e["cutoff"] <= e[k]["resolved_interval"] < e["horizon_end"])
        for e in valid for k in ("A", "O") if e[k]["Y"] is not None)
    c["selected barriers are B and V, opposite barriers mirror them around P"] = all(
        Decimal(e["A"]["favourable"]) == Decimal(e["B"]) and Decimal(e["A"]["adverse"]) == Decimal(e["V"])
        and Decimal(e["O"]["favourable"]) + Decimal(e["A"]["favourable"]) == 2 * Decimal(e["P"])
        and Decimal(e["O"]["adverse"]) + Decimal(e["A"]["adverse"]) == 2 * Decimal(e["P"]) for e in valid)
    return c


def reconcile(t: dict) -> dict:
    st, pairs = t["status"], t["pairs"]
    nv = st.get("VALID_GEOMETRY", 0)
    n2 = sum(t["paired_2x2_determined"].values())
    return {"first confirmations = valid + invalid + not evaluable": t["first_confirmations"] == sum(st.values()),
            "valid = determined + unresolved pairs": nv == sum(pairs.values()),
            "2x2 total = determined pairs": n2 == pairs.get("DETERMINED", 0),
            "selected outcomes sum to valid": sum(t["outcomes_selected_A"].values()) == nv,
            "opposite outcomes sum to valid": sum(t["outcomes_opposite_O"].values()) == nv}


def run(journal, bars, data_end) -> dict:
    eps = episodes(journal, bars, data_end)
    tabs = {w: tables([e for e in eps if e["window"] == w]) for w in ("evaluation", "warmup")}
    rec = {w: reconcile(tabs[w]) for w in tabs}
    chk = checks(eps, journal, bars, data_end)
    return {"eps": eps, "res": {"tables": tabs, "reconciliation": rec, "checks": chk,
                                "all_checks_pass": all(chk.values()) and all(all(v.values()) for v in rec.values())}}


def episodes_csv(eps: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["window", "scenario_id", "direction", "born_at", "confirmed_epoch", "cutoff", "cutoff_cursor",
                "horizon_end", "P", "P_bar", "B", "V", "a", "b", "status", "reason", "A_favourable", "A_adverse",
                "Y_A", "A_category", "A_interval", "A_reason", "O_favourable", "O_adverse", "Y_O", "O_category",
                "O_interval", "O_reason", "pair", "reference", "difference", "joint_feasible_differences",
                "overlapping_windows", "native_terminal", "native_terminal_at"])
    for e in eps:
        a_, o_ = e.get("A") or {}, e.get("O") or {}
        w.writerow([e["window"], e["scenario_id"], e["direction"], e["born_at"], e["confirmed_epoch"], e["cutoff"],
                    e["cutoff_cursor"], e["horizon_end"], e["P"], e.get("P_bar"), e["B"], e["V"], e.get("a"),
                    e.get("b"), e["status"], e["reason"], a_.get("favourable"), a_.get("adverse"), a_.get("Y"),
                    a_.get("category"), a_.get("resolved_interval"), a_.get("reason"), o_.get("favourable"),
                    o_.get("adverse"), o_.get("Y"), o_.get("category"), o_.get("resolved_interval"), o_.get("reason"),
                    e.get("pair"), e.get("reference"), e.get("difference"), " ".join(e.get("joint_differences", [])),
                    e.get("overlapping_windows"), e["native_terminal"], e["native_terminal_at"]])
    return buf.getvalue()


def load_bars(path: Path) -> dict:
    bars: dict[datetime, Bar | None] = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s = dt(row["start"])
            bars[s] = None if row["kind"] != "bar" else Bar(s, dt(row["end"]), Decimal(row["high"]),
                                                          Decimal(row["low"]), Decimal(row["close"]))
    return bars


def main_run(run_dir: Path, out: Path) -> None:
    with gzip.open(run_dir / "journal.jsonl.gz", "rt", encoding="utf-8") as f:
        journal = [json.loads(x) for x in f]
    bars = load_bars(run_dir / "trade_bars.csv.gz")
    data_end = max(bars) + MIN
    got = run(journal, bars, data_end)
    out.mkdir(parents=True, exist_ok=True)
    files = {"results.json": json.dumps(got["res"], indent=1, sort_keys=True) + "\n",
             "episodes.csv": episodes_csv(got["eps"])}
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
        print(name, hashlib.sha256(text.encode()).hexdigest())
    print("ALL CHECKS PASS" if got["res"]["all_checks_pass"] else "CHECK FAILURE")


# ----------------------------------------------------------------------------------------------------------------------
# hand-derived synthetic cases (no engine)
# ----------------------------------------------------------------------------------------------------------------------

def selftest() -> dict:
    res: dict[str, bool] = {}

    def check(name, cond):
        res[name] = bool(cond)

    T0 = dt("2025-09-02T10:00:00Z")
    P = Decimal(1000)

    def mk(d: int, spec: dict[int, tuple] | None = None, n: int = 240, missing=(), start=-5):
        """Flat bars at P (high P+0.5, low P-0.5) from T0+start to T0+n minutes; spec gives (high, low) offsets from P
        in the d-oriented domain (mirrored for SHORT)."""
        bars = {}
        for i in range(start, n):
            s = T0 + i * MIN
            if i in missing:
                bars[s] = None
                continue
            hi, lo = (spec or {}).get(i, (Decimal("0.5"), Decimal("-0.5")))
            vals = sorted([P + Decimal(str(hi)) * d, P + Decimal(str(lo)) * d])
            bars[s] = Bar(s, s + MIN, vals[1], vals[0], P)
        return bars, T0 + n * MIN

    for d in (1, -1):
        tag = "LONG" if d > 0 else "SHORT"
        a, b = Decimal(10), Decimal(4)  # different distances
        # favourable first for A: +10 at minute 30; O's favourable is -10, its adverse +4 -> O adverse first (same bar)
        bars, end = mk(d, {30: (11, 0)})
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} A favourable first (Y_A=1); O adverse first in that bar (Y_O=0)",
              (r["A"]["category"], r["O"]["category"]) == ("FAVOURABLE_FIRST", "ADVERSE_FIRST")
              and r["A"]["resolved_interval"] == zs(T0 + 30 * MIN) and r["joint_differences"] == ["1/2"])
        # adverse first for A at -4 (minute 12), which is not O's favourable (-10): O open until -10 at minute 50
        bars, end = mk(d, {12: (0, -5), 50: (0, -10)})
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} A adverse first (Y_A=0); O favourable later (Y_O=1); difference -1/2",
              (r["A"]["Y"], r["O"]["Y"]) == (0, 1) and r["joint_differences"] == ["-1/2"])
        # no contact within 4h: both horizon categories (Y=0), distinct from adverse first
        bars, end = mk(d)
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} no contact: both HORIZON_NO_FAVOURABLE_CONTACT, Y=0, difference 0",
              r["A"]["category"] == r["O"]["category"] == "HORIZON_NO_FAVOURABLE_CONTACT" and r["joint_differences"] == ["0"])
        # both A barriers in one bar: A ambiguous; O: +4 (adverse) and -10 (favourable) both touched too
        bars, end = mk(d, {20: (11, -11)})
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} two contacts in one bar: both orientations UNDETERMINED (AMBIGUOUS_SAME_INTERVAL), all joint "
              "differences feasible", r["A"]["Y"] is None and r["O"]["Y"] is None
              and r["A"]["reason"].startswith("AMBIGUOUS_SAME_INTERVAL")
              and r["joint_differences"] == ["-1/2", "0", "1/2"])
        # equal distances a = b: the same events decide both orientations -> (1,1) and (0,0) infeasible
        bars, end = mk(d, {20: (5, -5)})
        r = probe(bars, end, T0, P, Decimal(5), Decimal(5), d)
        check(f"{tag} a = b, both levels in one bar: joint constraint keeps only differences -1/2 and +1/2",
              r["joint_differences"] == ["-1/2", "1/2"])
        # a contact in the bar ending at the cutoff (pre-publication) is never an outcome
        bars, end = mk(d, {-1: (11, -11)})
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} contacts before the cutoff are not outcomes", r["A"]["category"] == "HORIZON_NO_FAVOURABLE_CONTACT")
        # a cutoff inside a bar (straddle): its touched level may lie before the cutoff -> ambiguity kept
        t_mid = T0 + 30 * timedelta(seconds=1)
        bars, end = mk(d, {0: (11, 0)}, n=245)  # the data also cover the bar straddling t_mid + 4h
        w = walk(bars, end, t_mid, t_mid + HORIZON, [(P + d * a, P - d * b)], P)
        check(f"{tag} straddling-cutoff bar touching the favourable level stays undetermined (F or later outcome)",
              {s[0] for s in w["states"]} == {F, H} and w["causes"][0].startswith("AMBIGUOUS_STRADDLING_INTERVAL"))
        # horizon edge: the bar ending exactly at t0+4h counts; the next one never does
        bars, end = mk(d, {239: (11, 0), 240: (0, -11)}, n=245)
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} the last bar [H-1m, H) counts, the bar starting at H does not",
              r["A"]["category"] == "FAVOURABLE_FIRST" and r["O"]["category"] == "ADVERSE_FIRST")
        bars, end = mk(d, {240: (11, 0)}, n=245)
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} a contact after the horizon is not an outcome (horizon category)",
              r["A"]["category"] == "HORIZON_NO_FAVOURABLE_CONTACT")
        # missing interval before any contact: undetermined, not skipped
        bars, end = mk(d, {30: (11, 0)}, missing=(10,))
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} a missing interval before resolution leaves Y undetermined (INCOMPLETE_MISSING_INTERVAL)",
              r["A"]["Y"] is None and r["A"]["reason"].startswith("INCOMPLETE_MISSING_INTERVAL"))
        bars, end = mk(d, {5: (11, 0)}, missing=(10,))
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} a missing interval after resolution changes nothing", r["A"]["category"] == "FAVOURABLE_FIRST"
              and r["O"]["category"] == "ADVERSE_FIRST")
        # data ending before the horizon: open orientations undetermined
        bars, end = mk(d, n=100)
        r = probe(bars, end, T0, P, a, b, d)
        check(f"{tag} data ending before the horizon: INCOMPLETE_DATA_END", r["A"]["Y"] is None
              and r["A"]["reason"].startswith("INCOMPLETE_DATA_END") and r["A"]["possible_Y"] == [0, 1])
        # partially determined pair: A resolved favourable, O ambiguous later
        bars, end = mk(d, {3: (11, 0), 60: (13, -11)})
        r = probe(bars, end, T0, P, Decimal(10), Decimal(12), d)  # O adverse +12 not touched at minute 3
        check(f"{tag} partially determined pair: Y_A=1, O undetermined, joint differences 0 and 1/2",
              r["A"]["Y"] == 1 and r["O"]["Y"] is None and r["joint_differences"] == ["0", "1/2"])

    # geometry and episodes (LONG): non-positive a or b is reported, never adjusted; P checked against its bar
    def journal_for(P_, B_, V_, close_):
        recs = [{"seq": 1, "kind": "scenario", "clock_time": "2025-09-02T09:00:00Z", "factual_cursor": 1,
                 "record_id": "b", "record": {"family": "A", "scenario_id": "S", "transition": "BIRTH",
                                              "direction": "LONG"}},
                {"seq": 2, "kind": "scenario", "clock_time": zs(T0), "factual_cursor": 2, "record_id": "c",
                 "record": {"family": "A", "scenario_id": "S", "transition": "CONFIRM", "direction": "LONG",
                            "anchor_epoch": 1, "confirmation_close": P_, "destination": B_, "invalidation_level": V_,
                            "confirmed_deadline": zs(T0 + HORIZON), "reason": f"x#obs@{zs(T0 - MIN)}"}}]
        bars, end = mk(1)
        last = bars[T0 - MIN]
        bars[T0 - MIN] = Bar(last.start, last.end, last.h, last.lo, Decimal(close_))
        return recs, bars, end

    for (B_, V_, want) in (("1000", "990", "INVALID_GEOMETRY"), ("1010", "1000", "INVALID_GEOMETRY"),
                           ("990", "980", "INVALID_GEOMETRY"), ("1010", "990", "VALID_GEOMETRY")):
        recs, bars, end = journal_for("1000", B_, V_, "1000")
        eps = episodes(recs, bars, end)
        check(f"geometry B={B_} V={V_}: {want}", eps[0]["status"] == want)
    recs, bars, end = journal_for("1000", "1010", "990", "1000.1")
    check("P different from the confirming bar close: NOT_EVALUABLE",
          episodes(recs, bars, end)[0]["status"] == "NOT_EVALUABLE")

    # bounds over the whole valid population with a partially determined pair
    e1 = {"status": "VALID_GEOMETRY", "pair": "DETERMINED", "A": {"Y": 1, "category": "FAVOURABLE_FIRST"},
          "O": {"Y": 0, "category": "ADVERSE_FIRST"}, "_dmin": Fraction(1, 2), "_dmax": Fraction(1, 2),
          "direction": "LONG", "cutoff": "2025-09-02T10:00:00Z", "horizon_end": "2025-09-02T14:00:00Z"}
    e2 = {"status": "VALID_GEOMETRY", "pair": "UNRESOLVED_O_ONLY", "A": {"Y": 1, "category": "FAVOURABLE_FIRST"},
          "O": {"Y": None, "category": "UNDETERMINED", "reason": "AMBIGUOUS_SAME_INTERVAL@x"},
          "_dmin": Fraction(0), "_dmax": Fraction(1, 2), "direction": "SHORT",
          "cutoff": "2025-09-02T11:00:00Z", "horizon_end": "2025-09-02T15:00:00Z"}
    t = tables([e1, e2])
    check("mean difference on determined pairs only; bounds over all valid keep the feasible joint values",
          t["determined_pairs"]["mean_difference"] == "1/2" and t["bounds_over_all_valid_geometry"]["lower"] == "1/4"
          and t["bounds_over_all_valid_geometry"]["upper"] == "1/2"
          and t["overlap_and_concentration"]["with_at_least_one_overlapping_window"] == 2
          and t["overlap_and_concentration"]["with_an_overlapping_opposite_direction_window"] == 2)
    return {"cases": res, "passed": sum(res.values()), "total": len(res)}


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        r = selftest()
        for k, v in r["cases"].items():
            print(("ok   " if v else "FAIL ") + k)
        print(f"{r['passed']}/{r['total']}")
        (Path(__file__).resolve().parent / "selftest.json").write_text(json.dumps(r, indent=1) + "\n",
                                                                      encoding="utf-8", newline="\n")
        sys.exit(0 if r["passed"] == r["total"] else 1)
    elif sys.argv[1] == "run":
        main_run(Path(sys.argv[2]), Path(sys.argv[3]))
