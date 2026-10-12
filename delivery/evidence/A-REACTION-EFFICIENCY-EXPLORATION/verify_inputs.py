"""A reaction directional efficiency, descriptive exploration: verification of the copied inputs (no outcome is read).

Checks the local, read-only copy of exactly two artifacts taken from the Owner volume under Astra's bounded
derogation of 12 October 2026:
* the pack manifest ``packs/pack-1ae7d36c20adbde0a468a7e0f6d8750a9951aa8e/manifest.json``;
* its immutable feed cache ``feedcache/fc-80221b24abf3a50b764cc873f4a70cc709847a6b/``.

Verified: manifest sha256 = the registered hash; the body re-hashes to the pack id and validates; the manifest names
this cache and its manifest hash; the cache opens with that pinned hash and its identity re-derives; every partition's
sha256, size and line count; the ordered-event hash recomputed over every canonical line; one complete observation
per minute and family over the initialization [2025-07-28, 2025-09-01), the evaluation [2025-09-01, 2026-01-01) and
the authorized tail [2026-01-01T00:00Z, 06:05Z), with no quality/gap event and nothing outside them. Only event
families, kinds and times are inspected: no price is printed or summarized.

Run from the repository root:
  .venv/Scripts/python.exe delivery/evidence/A-REACTION-EFFICIENCY-EXPLORATION/verify_inputs.py <data_root>
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from algotrader.corpus.pack import pack_id_for  # noqa: E402
from algotrader.corpus.pack_contracts import PackManifest  # noqa: E402
from algotrader.observe import feedcache as fc  # noqa: E402

PACK_ID = "pack-1ae7d36c20adbde0a468a7e0f6d8750a9951aa8e"
MANIFEST_SHA256 = "1bec1f1575306d4444969569675e28bfdc9dac60e2d6f461b283871362221f92"  # registered by Astra
CACHE_ID = "fc-80221b24abf3a50b764cc873f4a70cc709847a6b"
WINDOWS = {"initialization": ("2025-07-28T00:00:00Z", "2025-09-01T00:00:00Z"),
           "evaluation": ("2025-09-01T00:00:00Z", "2026-01-01T00:00:00Z"),
           "tail": ("2026-01-01T00:00:00Z", "2026-01-01T06:05:00Z")}
FAMILIES = ("trade_bar_1m", "mark_bar_1m", "index_bar_1m")
OUT = Path(__file__).resolve().parent / "inputs_verification.json"


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main(data_root: Path) -> None:
    checks: dict[str, object] = {}
    mpath = data_root / "packs" / PACK_ID / "manifest.json"
    raw = mpath.read_bytes()
    msha = hashlib.sha256(raw).hexdigest()
    checks["pack_manifest_sha256_equals_registered"] = msha == MANIFEST_SHA256
    doc = json.loads(raw)
    checks["pack_id_field"] = doc.get("pack_id") == PACK_ID
    checks["pack_body_rehashes_to_id"] = pack_id_for(doc) == PACK_ID
    PackManifest.model_validate(doc)
    checks["pack_manifest_schema_valid"] = True
    feed = doc["feed"]
    checks["pack_names_this_cache"] = feed["cache_id"] == CACHE_ID
    cache = fc.open_cache(data_root, CACHE_ID, expected_manifest_sha256=feed["cache_manifest_sha256"])
    checks["cache_manifest_sha256_equals_pack_pin"] = cache.manifest_sha256 == feed["cache_manifest_sha256"]
    checks["cache_identity_rederives"] = fc.cache_id_for(cache.manifest["key"]) == CACHE_ID
    fm = cache.feed_manifest
    checks["feed_content_identity_equals_pack"] = fm.content_identity == feed["content_identity"]
    checks["feed_ordered_event_hash_equals_pack"] = fm.ordered_event_hash == feed["ordered_event_hash"]
    checks["feed_event_count_equals_pack"] = fm.event_count == feed["event_count"]
    files = sorted(p.name for p in cache.path.iterdir())
    expected_files = sorted(["manifest.json", "exclusions.jsonl"] + [p["file"] for p in cache.partitions])
    checks["cache_directory_holds_exactly_the_manifest_files"] = files == expected_files
    checks["exclusions_file_sha256"] = fc.sha256_file(cache.path / "exclusions.jsonl") == \
        cache.manifest["source_facts"].get("exclusions_sha256")

    oh = hashlib.sha256()
    commit = fc.initial_commitment(CACHE_ID)
    seen: dict[str, dict[str, set]] = {f: {w: set() for w in WINDOWS} for f in FAMILIES}
    other_kinds: dict[str, int] = {}
    outside = 0
    dup = 0
    n = 0
    bad_parts = []
    wins = {w: (dt(a), dt(b)) for w, (a, b) in WINDOWS.items()}
    for p in cache.partitions:
        blob = (cache.path / p["file"]).read_bytes()
        if hashlib.sha256(blob).hexdigest() != p["sha256"] or len(blob) != p["bytes"]:
            bad_parts.append(p["file"])
            continue
        lines = gzip.decompress(blob).split(b"\n")[:-1]
        if len(lines) != p["count"] or commit.hex() != p["commitment_before"]:
            bad_parts.append(p["file"])
        for line in lines:
            oh.update(line + b"\n")
            commit = fc.extend_commitment(commit, line)
            n += 1
            e = json.loads(line)
            fam, kind = e["channel"]["family"], e["kind"]
            if fam not in FAMILIES or kind != "bar_observation":
                other_kinds[f"{fam}/{kind}"] = other_kinds.get(f"{fam}/{kind}", 0) + 1
                continue
            t = dt(e["event_time"])
            if dt(e["event_end_time"]) - t != timedelta(minutes=1):
                other_kinds[f"{fam}/non_1m_interval"] = other_kinds.get(f"{fam}/non_1m_interval", 0) + 1
            w = next((k for k, (a, b) in wins.items() if a <= t < b), None)
            if w is None:
                outside += 1
                continue
            if t in seen[fam][w]:
                dup += 1
            seen[fam][w].add(t)
    checks["every_partition_sha256_size_count_and_commitment"] = not bad_parts
    checks["ordered_event_hash_recomputed_equals_manifest"] = oh.hexdigest() == fm.ordered_event_hash
    checks["events_read_equal_event_count"] = n == fm.event_count
    coverage = []
    for f in FAMILIES:
        for w, (a, b) in wins.items():
            expected = int((b - a) / timedelta(minutes=1))
            got = seen[f][w]
            complete = len(got) == expected and min(got) == a and max(got) == b - timedelta(minutes=1)
            coverage.append({"family": f, "window": w, "start": WINDOWS[w][0], "end": WINDOWS[w][1],
                             "expected_minutes": expected, "observed_minutes": len(got), "complete": complete})
    checks["coverage_complete_every_family_and_window"] = all(c["complete"] for c in coverage)
    checks["no_quality_gap_or_other_event"] = not other_kinds
    checks["no_event_outside_the_three_windows"] = outside == 0
    checks["no_duplicate_minute"] = dup == 0
    pack_cov = [{k: c[k] for k in ("family", "window", "expected_slots", "valid", "missing", "rejected")}
                for c in doc["coverage"]]
    win_map = {"warmup": "initialization", "evaluation": "evaluation", "tail": "tail"}
    checks["pack_coverage_rows_agree"] = all(
        any(c["family"] == r["family"] and c["window"] == win_map.get(r["window"]) and
            c["observed_minutes"] == r["valid"] == r["expected_slots"] and r["missing"] == r["rejected"] == 0
            for c in coverage) for r in pack_cov if r["family"] in FAMILIES)
    checks["pack_windows_equal_authorized"] = (
        doc["windows"]["warmup"]["start"] == "2025-07-28T00:00:00+00:00"
        and doc["windows"]["evaluation"]["start"] == "2025-09-01T00:00:00+00:00"
        and doc["windows"]["evaluation"]["end"] == "2026-01-01T00:00:00+00:00"
        and doc["tail_end"] == "2026-01-01T06:05:00Z" and doc["clock_end"] == "2026-01-01T06:05:00Z")
    out = {
        "purpose": "verification of the copied inputs of the A reaction E exploration (no outcome read)",
        "provenance": {
            "source": "Owner Docker volume mounted at /data/market in container algotrader-api-1 (read-only use)",
            "copied": ["/data/market/packs/" + PACK_ID + "/manifest.json", "/data/market/feedcache/" + CACHE_ID + "/"],
            "method": "docker cp (source unchanged); destination: session scratchpad outside Git",
            "copied_at_utc": "2026-10-12T15:41:53Z",
            "authorization": "Astra bounded derogation relayed by the Owner, 12 October 2026",
            "prior_consultation": "2026-10-12, before the derogation: docker exec on algotrader-api-1 listed "
                                  "/data/market and /data/market/packs, hashed the pack manifest and printed its "
                                  "metadata (capabilities, coverage counts, windows, identities, sources); then listed "
                                  "the cache directory and printed the feed cache_id/manifest hash. No price, run "
                                  "record or DB was read.",
        },
        "pack": {"pack_id": PACK_ID, "manifest_sha256": msha, "preset_id": doc["preset"]["preset_id"],
                 "preset_sha256": doc["preset_sha256"], "status": doc["status"], "clock_end": doc["clock_end"],
                 "windows": WINDOWS, "limitations": doc["limitations"]},
        "feed_cache": {"cache_id": CACHE_ID, "manifest_sha256": cache.manifest_sha256,
                       "content_identity": fm.content_identity, "ordered_event_hash": fm.ordered_event_hash,
                       "ordered_event_hash_recomputed": oh.hexdigest(), "final_prefix_commitment": commit.hex(),
                       "event_count": fm.event_count, "event_counts": fm.event_counts,
                       "partitions": len(cache.partitions), "partition_bytes": sum(p["bytes"] for p in cache.partitions),
                       "availability_policy": fm.availability_policy.policy_id},
        "coverage": coverage, "other_event_kinds": other_kinds, "bad_partitions": bad_parts, "checks": checks,
        "all_checks_pass": all(v is True for v in checks.values()),
    }
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    for k, v in checks.items():
        print(f"{'ok ' if v is True else 'FAIL'} {k}")
    print("ALL PASS" if out["all_checks_pass"] else "DISCREPANCY: stop")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
