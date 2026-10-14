"""A confirmed direction, historical replication: verify the offline-prepared pack and its sources BEFORE processing.

Ordinary trust checks only (no price, no outcome is read beyond what the ordinary verification itself hashes):
* the published pack through its trusted receipt (``pack.open_pack``: manifest bytes = receipt, body hashes to the id,
  schema, provenance file);
* the registered preset identity, windows, clock end and the offline-only historical classification;
* coverage per family and window (expected slots, valid, missing, rejected and reasons), overlap (conflicts,
  identical collapses, overlapping slots), status and limitations;
* every source dataset: provenance (official OKX endpoints, request window, retrieval time), full ordinary
  ``marketdata.dataset.verify`` (file hashes and rows), its quality report (status, findings: duplicates/conflicts/
  missing intervals);
* the composed feed cache through ``feedcache.open_cache`` with the manifest's expected hash.

Writes ``inputs_verification.json`` next to this script and prints the identities to register (section 7).

  python verify_pack_inputs.py <data_root> <database_url> <pack_id>
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from algotrader.corpus import pack as pk  # noqa: E402
from algotrader.corpus import presets as ps  # noqa: E402
from algotrader.marketdata import dataset as md  # noqa: E402
from algotrader.observe import feedcache as fc  # noqa: E402

HERE = Path(__file__).resolve().parent
PRESET_ID = "a-confirmed-direction-historical-replication-2025-v1"
WINDOWS = {"warmup": ("2024-11-27T00:00:00+00:00", "2025-01-01T00:00:00+00:00"),
           "evaluation": ("2025-01-01T00:00:00+00:00", "2025-05-01T00:00:00+00:00"),
           "tail": ("2025-05-01T00:00:00+00:00", "2025-05-01T06:05:00+00:00")}
BAR_FAMILIES = ("trade_bar_1m", "mark_bar_1m", "index_bar_1m")


def z(s: str) -> datetime:
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def main(data_root: Path, url: str, pack_id: str) -> None:
    with psycopg.connect(url, autocommit=True, row_factory=dict_row) as c:
        receipt = pk.pack_receipt(c, pack_id)
    doc = pk.open_pack(data_root, pack_id, receipt)
    f = ps.load_presets()
    preset = ps.resolve(f, PRESET_ID)
    checks: dict[str, bool] = {}
    checks["pack opened through its trusted receipt (bytes, id, schema, provenance)"] = True
    checks["preset = the registered offline-only historical study preset"] = (
        doc["preset"]["preset_id"] == PRESET_ID and ps.Preset.model_validate(doc["preset"]) == preset
        and ps.offline_only_study(preset) is not None)
    ec = doc["evidence_classes"]
    checks["classification: REGISTERED_STUDY_WINDOW, HISTORICAL_REPLICATION, never certified uncontaminated"] = (
        ec["label"] == "REGISTERED_STUDY_WINDOW" and ec.get("study_kind") == "HISTORICAL_REPLICATION"
        and ec["certified_uncontaminated"] is False)
    w = doc["windows"]
    checks["windows exactly as registered; requested and clock end = tail end 2025-05-01T06:05Z"] = (
        all((z(w[k]["start"]), z(w[k]["end"])) == (z(a), z(b)) for k, (a, b) in WINDOWS.items())
        and z(doc["requested_start"]) == z(WINDOWS["warmup"][0]) and z(doc["tail_end"]) == z(WINDOWS["tail"][1])
        and z(doc["clock_end"]) == z(WINDOWS["tail"][1]))
    cov = doc["coverage"]
    bars = [x for x in cov if x["family"] in BAR_FAMILIES]
    checks["trade/mark/index 1m: every slot valid in every window (0 missing, 0 rejected)"] = (
        len(bars) == 9 and all(x["valid"] == x["expected_slots"] and x["missing"] == 0 and x["rejected"] == 0
                               for x in bars))
    ov = doc["overlap"]
    checks["no conflict between sources (overlap conflicts 0)"] = ov["conflicts"] == 0
    datasets = []
    for s in doc["sources"]:
        path = md.dataset_path(data_root, s["dataset_id"])
        man = md.load_manifest(path)
        q = md.load_quality(path)
        problems = md.verify(path)
        fams = json.loads(q.model_dump_json())["families"]
        mj = json.loads(man.model_dump_json())
        datasets.append({
            "dataset_id": s["dataset_id"], "slice": [s["start"], s["end"]],
            "request": [s["request_start"], s["request_end"]],
            "source_manifest_sha256": s["source_manifest_sha256"],
            "manifest_sha256_on_disk": hashlib.sha256((path / "manifest.json").read_bytes()).hexdigest(),
            "cache_id": s["cache_id"], "cache_manifest_sha256": s["cache_manifest_sha256"],
            "retrieval_started_at": mj.get("retrieval_started_at"),
            "endpoints": sorted({x.get("endpoint") for x in mj.get("families", [])}),
            "source": (mj.get("request") or {}).get("source"),
            "verify_problems": problems, "quality_status": q.status.value if hasattr(q.status, "value") else q.status,
            "quality_families": fams,
            "quality_findings": [json.loads(x.model_dump_json()) for x in q.findings]})
    checks["every source dataset passes the ordinary full verification (hashes, rows)"] = all(
        not d["verify_problems"] for d in datasets)
    checks["source manifests on disk = the pack's pinned source manifests"] = all(
        d["manifest_sha256_on_disk"] == d["source_manifest_sha256"] for d in datasets)
    checks["provenance: OKX public endpoints only"] = all(
        d["source"] == "okx" and all(e and e.startswith("/api/v5/") for e in d["endpoints"]) for d in datasets)
    cache = fc.open_cache(data_root, doc["feed"]["cache_id"], expected_manifest_sha256=doc["feed"]["cache_manifest_sha256"])
    checks["pack feed cache opens with its pinned manifest hash; content identity and event count match"] = (
        cache.feed_manifest.content_identity == doc["feed"]["content_identity"]
        and cache.feed_manifest.event_count == doc["feed"]["event_count"])
    raw = (pk.packs_root(data_root) / pack_id / "manifest.json").read_bytes()
    out = {
        "checks": checks, "all_pass": all(checks.values()),
        "pack": {"pack_id": pack_id, "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                 "receipt_manifest_sha256": receipt["manifest_sha256"], "status": doc["status"],
                 "limitations": doc["limitations"], "preset_sha256": ps.preset_sha256(f, preset),
                 "windows": w, "clock_end": doc["clock_end"], "evidence_classes": ec,
                 "coverage": cov, "overlap": ov, "input_readiness_preview": doc["input_readiness_preview"]},
        "feed": {k: doc["feed"][k] for k in ("cache_id", "cache_manifest_sha256", "content_identity", "event_count",
                                             "event_counts", "availability_policy_id") if k in doc["feed"]},
        "datasets": datasets, "data_root": str(data_root),
    }
    (HERE / "inputs_verification.json").write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8",
                                                   newline="\n")
    for k, v in checks.items():
        print(("ok   " if v else "FAIL ") + k)
    print(json.dumps({"pack_id": pack_id, "manifest_sha256": out["pack"]["manifest_sha256"],
                      "status": doc["status"], **out["feed"]}, default=str)[:900])
    print("ALL PASS" if out["all_pass"] else "DISCREPANCY: stop")


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2], sys.argv[3])
