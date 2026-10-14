"""Proof of the backend block on the REAL offline-prepared pack (disposable replica DB; app API via TestClient).

GET-listing, Workbench preparation, evaluation starts and a Replay Lab start on the pack are requested directly; every
refusal is recorded with the row counts before and after (no job, evaluation or replay row may appear).

  python backend_block_proof.py <data_root> <database_url> <pack_id>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from algotrader.api import create_app

HERE = Path(__file__).resolve().parent
PRESET = "a-confirmed-direction-historical-replication-2025-v1"


def counts(url: str) -> dict:
    with psycopg.connect(url, row_factory=dict_row) as c:
        return {t: c.execute(f"SELECT count(*) AS n FROM {t}").fetchone()["n"]
                for t in ("corpus_pack_jobs", "evaluations", "observation_replays")}


def main(root: Path, url: str, pack_id: str) -> None:
    api = TestClient(create_app(url, root.parent / "art-proof", web_dist=root.parent / "no-ui", data_root=root))
    before = counts(url)
    listed = [p["preset"]["preset_id"] for p in api.get("/api/corpus/presets").json()["presets"]]
    calls = []
    for method, path, body in (("POST", f"/api/corpus/presets/{PRESET}/prepare", None),
                               ("POST", "/api/evaluations", {"pack_id": pack_id, "run_type": "adviser_evaluation",
                                                             "method": "v0.6"}),
                               ("POST", "/api/evaluations", {"pack_id": pack_id, "run_type": "observation_only"}),
                               ("POST", "/api/observations", {"source_kind": "pack", "source_id": pack_id,
                                                              "speed": 0})):
        r = api.request(method, path, json=body)
        calls.append({"request": f"{method} {path}", "body": body, "status": r.status_code,
                      "detail": r.json().get("detail")})
    after = counts(url)
    out = {"pack_id": pack_id, "preset_listed_by_workbench_api": PRESET in listed, "listed_presets": listed,
           "requests": calls, "rows_before": before, "rows_after": after,
           "all_refused_without_rows": (PRESET not in listed and all(c["status"] == 409 for c in calls)
                                        and before == after)}
    (HERE / "backend_block_proof.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2], sys.argv[3])
