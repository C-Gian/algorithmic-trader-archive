"""Descriptive historical comparison v0.6 / v0.6-a2x: the new v0.6 journal against the 12 October v0.6 journal.

Same pack, rules and register; different build (6a0f22a then, this registration's commit now) and the passive trace now.
Every journal entry is compared in order after removing only ``record.env.method.build`` and the entry's ``digest`` and
``chain`` (they hash the build). Prints the counts and the first difference, if any; writes nothing else.

  .venv/Scripts/python.exe delivery/evidence/A2X-HISTORICAL-COMPARISON/crosscheck_baseline.py <old_journal.jsonl.gz> <new_journal.jsonl.gz>
"""

from __future__ import annotations

import gzip
import json
import sys


def strip(line: str) -> dict:
    e = json.loads(line)
    e.pop("digest", None)
    e.pop("chain", None)
    e["record"]["env"]["method"].pop("build", None)
    return e


def main(old: str, new: str) -> None:
    n = 0
    with gzip.open(old, "rt", encoding="utf-8") as a, gzip.open(new, "rt", encoding="utf-8") as b:
        for la, lb in zip(a, b, strict=False):
            n += 1
            ea, eb = strip(la), strip(lb)
            if ea != eb:
                print(f"FIRST DIFFERENCE at entry {n}: {ea['kind']} {ea['record_id']} / {eb['kind']} {eb['record_id']}")
                raise SystemExit(1)
        rest_a, rest_b = sum(1 for _ in a), sum(1 for _ in b)
    if rest_a or rest_b:
        print(f"LENGTH DIFFERS after {n} equal entries: +{rest_a} old, +{rest_b} new")
        raise SystemExit(1)
    print(f"IDENTICAL: {n} journal entries equal (build, digest and chain removed)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
