"""A revisions historical check: identity, hash and completeness of the reused local v0.6 artifacts.

Reused, never recomputed: the 12 October 2026 offline v0.6 processing (journal + admitted trade 1m bars) recorded in
``A-REACTION-EFFICIENCY-EXPLORATION/run_manifest.json`` and already re-read by the A2X comparison and the expectation
check. Reads hashes, counts, kinds, identities and times only (no price, no outcome).

  .venv/Scripts/python.exe delivery/evidence/A-REVISION-HISTORICAL-CHECK/verify_inputs.py <run_12oct_dir>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EV = HERE.parent
RULES_V06 = "57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66"
REGISTER_V06 = "98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(run: Path) -> None:
    m = json.loads((EV / "A-REACTION-EFFICIENCY-EXPLORATION/run_manifest.json").read_text(encoding="utf-8"))
    ident = m["engine"]["adviser"]["identity"]
    c: dict[str, bool] = {}
    c["journal sha256 = committed manifest"] = sha(run / "journal.jsonl.gz") == m["outputs_outside_git"]["journal.jsonl.gz"]
    c["trade bars sha256 = committed manifest"] = sha(run / "trade_bars.csv.gz") == m["outputs_outside_git"]["trade_bars.csv.gz"]
    c["method v0.6, frozen rules/register, no evaluator, finish 2026-01-01T06:05Z"] = (
        m["method"] == "v0.6" and ident["rules_sha256"] == RULES_V06 and ident["register_sha256"] == REGISTER_V06
        and ident["implementation"] == "adviser.core.v6" and m["evaluator"] is None
        and m["clock_end"] == "2026-01-01T06:05:00Z" and ident["pins"]["tick"] == "0.1")
    n, last, kinds, methods = 0, None, {}, set()
    with gzip.open(run / "journal.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            n += 1
            last = e["chain"]
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
            env = e["record"].get("env") or {}
            if env.get("method"):
                methods.add((env["method"]["rules_sha256"], env["method"]["register_sha256"],
                             env["method"]["implementation"]))
    c["journal complete: entries, kinds and last chain = manifest"] = (
        n == m["journal_entries"] and last == m["journal_last_chain"] and kinds == m["journal_counts"])
    c["every journal record carries the frozen v0.6 identity"] = methods == {(RULES_V06, REGISTER_V06, "adviser.core.v6")}
    bars = gaps = 0
    first = last_bar = None
    with gzip.open(run / "trade_bars.csv.gz", "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "bar":
                bars += 1
                first = first or row["start"]
                last_bar = row["start"]
            else:
                gaps += 1
    c["trade bars complete: 226,445 observations, 0 non-observations (= manifest)"] = (
        bars == m["trade_bars"] == 226445 and gaps == m["trade_non_observations"] == 0)
    out = {"checks": c, "all_pass": all(c.values()), "journal_entries": n, "journal_counts": kinds,
           "journal_last_chain": last, "trade_bars": bars, "trade_non_observations": gaps,
           "trade_bars_first_start": first, "trade_bars_last_start": last_bar,
           "sha256": {"journal.jsonl.gz": sha(run / "journal.jsonl.gz"),
                      "trade_bars.csv.gz": sha(run / "trade_bars.csv.gz")},
           "source": str(run)}
    (HERE / "inputs_verification.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    for k, v in c.items():
        print(("ok   " if v else "FAIL ") + k)
    print("ALL PASS" if out["all_pass"] else "DISCREPANCY: stop")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
