"""v0.6 A/B/C expectation historical check: identity, hash and completeness of the reused processing artifacts.

Reused, never recomputed: the 12 October v0.6 offline processing (journal + admitted trade 1m bars) recorded in
``A-REACTION-EFFICIENCY-EXPLORATION/run_manifest.json``, and the 13 October v0.6 journal recorded in
``A2X-HISTORICAL-COMPARISON/run_manifest_v0.6.json`` (proven entry-for-entry identical to it, build/digest/chain
removed). Reads hashes, counts, kinds and times only.

  .venv/Scripts/python.exe delivery/evidence/V06-EXPECTATION-HISTORICAL-CHECK/verify_artifacts.py <run_12oct_dir> <run_13oct_v06_dir>
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


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(r12: Path, r13: Path) -> None:
    m12 = json.loads((EV / "A-REACTION-EFFICIENCY-EXPLORATION/run_manifest.json").read_text(encoding="utf-8"))
    m13 = json.loads((EV / "A2X-HISTORICAL-COMPARISON/run_manifest_v0.6.json").read_text(encoding="utf-8"))
    c = {}
    c["12 Oct journal sha256 = committed manifest"] = sha(r12 / "journal.jsonl.gz") == m12["outputs_outside_git"]["journal.jsonl.gz"]
    c["12 Oct trade bars sha256 = committed manifest"] = sha(r12 / "trade_bars.csv.gz") == m12["outputs_outside_git"]["trade_bars.csv.gz"]
    c["13 Oct v0.6 journal sha256 = committed manifest"] = sha(r13 / "journal.jsonl.gz") == m13["outputs_outside_git"]["journal.jsonl.gz"]
    c["method v0.6, same pack/cache/feed, no evaluator, every event, finish 06:05Z"] = (
        m12["method"] == m13["method"] == "v0.6" and m12["pack_id"] == m13["pack_id"]
        and m12["cache_manifest_sha256"] == m13["cache_manifest_sha256"]
        and m12["feed_content_identity"] == m13["feed_content_identity"] and m12["evaluator"] is None
        and m12["events_applied"] == 679335 and m12["clock_end"] == "2026-01-01T06:05:00Z")
    c["rules/register identity = frozen v0.6"] = (
        m12["engine"]["adviser"]["identity"]["rules_sha256"] == "57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66"
        and m12["engine"]["adviser"]["identity"]["register_sha256"] == "98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda")
    n, last, kinds = 0, None, {}
    with gzip.open(r12 / "journal.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            n += 1
            last = e["chain"]
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    c["journal complete: entries, kinds and last chain = manifest"] = (
        n == m12["journal_entries"] and last == m12["journal_last_chain"] and kinds == m12["journal_counts"])
    bars = gaps = 0
    with gzip.open(r12 / "trade_bars.csv.gz", "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "bar":
                bars += 1
            else:
                gaps += 1
    c["trade bars complete: 226,445 observations, 0 non-observations (= manifest)"] = (
        bars == m12["trade_bars"] == 226445 and gaps == m12["trade_non_observations"] == 0)
    out = {"checks": c, "all_pass": all(c.values()), "journal_entries": n, "journal_counts": kinds, "trade_bars": bars,
           "trade_non_observations": gaps, "sources": {"12oct": str(r12), "13oct": str(r13)}}
    (HERE / "artifacts_verification.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    for k, v in c.items():
        print(("ok   " if v else "FAIL ") + k)
    print("ALL PASS" if out["all_pass"] else "DISCREPANCY: stop")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
