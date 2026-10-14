"""Offline-only historical replication study entry (``study_kind`` / ``offline_only``; additive registry change).

Pure part: the real packaged registry - the historical entry's exact windows, classification and pinned sources, the
unchanged identities and classification of every earlier preset and study, and the unchanged guards. DB part (synthetic
engineering inputs only, never market data): an offline-only historical study fixture is prepared by the ordinary
offline path (``create_pack_job`` + corpus worker) and is never listed, prepared or run through the app API, even on
direct request and with its pack already prepared; an ordinary study fixture stays admitted as before."""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from pathlib import Path

import pytest
import study_fixtures as sf
from adviser_db import fake_from
from fastapi.testclient import TestClient
from pack_fixtures import connect, corpus_worker, drain

from algotrader.api import create_app
from algotrader.corpus import pack_job as pj
from algotrader.corpus import presets as ps

ROOT = Path(__file__).resolve().parents[1]
HIST_ID = "A-CONFIRMED-DIRECTION-HISTORICAL-REPLICATION-2025"
HIST_PRESET = "a-confirmed-direction-historical-replication-2025-v1"
# identities before the additive change (preset_sha256 under the packaged presets.json policies)
PINNED = {"btc-september-development-v1": "4b56ad2f472aaee32b868a11f3e96892e20d27f3e2ebd9002e3a899c7fb7adc8",
          "btc-september-october-continuity-v1": "30457c51cb6c08d14538e077fb7d123c47d5d287507090e0b492a7c6aa8b4242",
          "btc-2025-09-to-2025-12-continuous-init35d-v1":
              "fabd1c55535a1f13e0fe7cdd30e217886e229063987015e4a7fbf64a0c952dbc",
          "a-v06-operational-evaluation-2027-v1": "861455dfd8f993cdb08c6c0191f1cb64bccdfb9408060c67e1cf525e325919ca"}
PROSPECTIVE_NOTE = ("Registered prospective study window outside the development and protected periods; data "
                    "preparation and integrity checks never certify uncontaminated evidence.")


def Z(s):
    from datetime import datetime
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _real(monkeypatch):
    monkeypatch.delenv("ALGOTRADER_CORPUS_PRESETS", raising=False)
    monkeypatch.delenv("ALGOTRADER_STUDY_PRESETS", raising=False)
    return ps.load_presets(), ps.load_study_presets()


def _sha_lf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


# -- 1. classification: historical entry, existing study unchanged -------------------------------------------------

def test_existing_presets_and_study_keep_identity_and_classification(monkeypatch):
    f, sp = _real(monkeypatch)
    got = {p.preset_id: ps.preset_sha256(f, p) for p in f.presets}
    old = next(s for s in sp.studies if s.study_id == "A-V06-OPERATIONAL-EVALUATION")
    got[old.preset.preset_id] = ps.preset_sha256(f, old.preset)
    assert got == PINNED
    assert old.study_kind is None and old.offline_only is None and ps.offline_only_study(old.preset) is None
    assert ps.classify(f, old.preset) == {"label": "REGISTERED_STUDY_WINDOW", "portions": [],
                                          "study_id": "A-V06-OPERATIONAL-EVALUATION", "method": "v0.6",
                                          "run_type": "adviser_evaluation", "note": PROSPECTIVE_NOTE,
                                          "certified_uncontaminated": False}
    for p in f.presets:
        assert "study_kind" not in ps.classify(f, p) and ps.offline_only_study(p) is None


def test_historical_entry_classification_and_pinned_sources(monkeypatch):
    f, sp = _real(monkeypatch)
    [h] = [s for s in sp.studies if s.study_id == HIST_ID]
    assert (h.study_kind, h.offline_only, h.method, h.run_type) == ("HISTORICAL_REPLICATION", True, "v0.6",
                                                                    "adviser_evaluation")
    for src in h.sources:
        assert _sha_lf(ROOT / src.path) == src.sha256_lf, src.path
    c = ps.classify(f, h.preset)
    assert c["label"] == "REGISTERED_STUDY_WINDOW" and c["study_kind"] == "HISTORICAL_REPLICATION"
    assert c["portions"] == [] and c["certified_uncontaminated"] is False and c["study_id"] == HIST_ID
    assert "historical replication" in c["note"] and "not completely documented" in c["note"]
    assert "prospective" not in c["note"]
    assert ps.offline_only_study(h.preset).study_id == HIST_ID


# -- 2. exact window, initialization, tail and protections ------------------------------------------------------------

def test_historical_window_is_exact_and_the_guards_are_unchanged(monkeypatch):
    f, sp = _real(monkeypatch)
    p = next(s for s in sp.studies if s.study_id == HIST_ID).preset
    assert p.preset_id == HIST_PRESET and p.initialization == ps.INITIALIZATION_EXPLICIT and not p.default
    assert (p.warmup.start, p.warmup.end) == (Z("2024-11-27T00:00:00Z"), Z("2025-01-01T00:00:00Z"))
    assert p.evaluation.start - p.warmup.start == timedelta(days=35)
    assert (p.evaluation.start, p.evaluation.end) == (Z("2025-01-01T00:00:00Z"), Z("2025-05-01T00:00:00Z"))
    assert (p.tail.start, p.tail.end) == (Z("2025-05-01T00:00:00Z"), Z("2025-05-01T06:05:00Z"))
    assert p.tail.minutes == f.outcome_tail_minutes == 365 and not p.automatic_prepare
    ps.check_windows(f, p)  # accepted by the ordinary rule: a registered study outside both periods
    assert ps.resolve(f, HIST_PRESET) == p
    shifted = p.model_copy(update={"evaluation": ps.Window(start=p.evaluation.start,
                                                           end=p.evaluation.end + timedelta(days=1)),
                                   "tail": ps.Window(start=p.tail.start + timedelta(days=1),
                                                     end=p.tail.end + timedelta(days=1))})
    for bad in (shifted, p.model_copy(update={"evidence_class": "DEVELOPMENT"}),
                p.model_copy(update={"preset_id": "copy-v1"})):
        with pytest.raises(ps.PresetError):
            ps.check_windows(f, bad)
    with pytest.raises(ps.PresetError):
        ps.months_preset(f, ["2025-01"])  # the month builder still stays inside the target


def test_a_historical_entry_may_not_overlap_development_or_protected(tmp_path, monkeypatch):
    inside = sf.study_preset(ev_start=Z("2025-07-10T02:00:00Z"),
                             ev_end=Z("2025-07-10T06:00:00Z"), init_start=Z("2025-07-10T00:00:00Z"))
    _write(tmp_path, monkeypatch, preset=inside)
    with pytest.raises(ps.PresetError, match="may not overlap the protected period"):
        ps.check_windows(ps.load_presets(), ps.load_study_presets().studies[0].preset)


# -- 3-6. DB: offline preparation admitted, app refusals, ordinary studies unchanged ---------------------------------

def _write(tmp_path: Path, monkeypatch, preset: dict | None = None, historical: bool = True) -> None:
    sf.write_files(tmp_path, monkeypatch, preset=preset)
    if historical:
        doc = sf.study_doc(preset)
        doc["studies"][0].update({"study_kind": "HISTORICAL_REPLICATION", "offline_only": True})
        (tmp_path / "study_presets.json").write_text(json.dumps(doc), encoding="utf-8")


def _counts(url: str) -> tuple[int, int, int]:
    with connect(url) as c:
        return tuple(c.execute(f"SELECT count(*) AS n FROM {t}").fetchone()["n"]
                     for t in ("corpus_pack_jobs", "evaluations", "observation_replays"))


@pytest.mark.db
def test_offline_only_study_is_prepared_offline_and_never_offered_or_run_by_the_app(database_url, tmp_path,
                                                                                     monkeypatch):
    _write(tmp_path, monkeypatch)
    root = tmp_path / "data"
    api = TestClient(create_app(database_url, tmp_path / "art", web_dist=tmp_path / "no-ui", data_root=root))
    # 4. absent from the Workbench selections (the ordinary development preset is still offered)
    listed = [p["preset"]["preset_id"] for p in api.get("/api/corpus/presets").json()["presets"]]
    assert sf.STUDY_PRESET_ID not in listed and "dev-fixture-v1" in listed
    # 5a. a direct Workbench preparation request is refused before any job row exists
    r = api.post(f"/api/corpus/presets/{sf.STUDY_PRESET_ID}/prepare")
    assert r.status_code == 409 and "offline-only" in r.text
    assert _counts(database_url) == (0, 0, 0)
    # 3. the ordinary offline path prepares it (same job function and corpus worker, no override of the guards)
    f = ps.load_presets()
    preset = ps.resolve(f, sf.STUDY_PRESET_ID)
    with connect(database_url) as c:
        job = pj.create_pack_job(c, f, preset, base_url="https://www.okx.com")
    drain(corpus_worker(database_url, root, fake_from(sf.tape(), start=sf.DAY1)))
    with connect(database_url) as c:
        row = c.execute("SELECT status, pack_id FROM corpus_pack_jobs WHERE job_id = %s", (job,)).fetchone()
    assert row["status"] == "completed" and row["pack_id"], row
    pack_id = row["pack_id"]
    manifest = json.loads((root / "packs" / pack_id / "manifest.json").read_text(encoding="utf-8"))
    ec = manifest["evidence_classes"]
    assert (ec["label"], ec["study_kind"], ec["certified_uncontaminated"]) == (
        "REGISTERED_STUDY_WINDOW", "HISTORICAL_REPLICATION", False)
    # 5b. no app run of any type on its already prepared pack: evaluation start and Replay Lab start
    for body in ({"run_type": "adviser_evaluation", "method": "v0.6"}, {"run_type": "adviser_evaluation"},
                 {"run_type": "observation_only"}, {"run_type": "adviser_evaluation", "method": "v0.6",
                                                    "acknowledge_limitations": True}):
        r = api.post("/api/evaluations", json={"pack_id": pack_id, **body})
        assert r.status_code == 409 and "offline-only" in r.text, body
    r = api.post("/api/observations", json={"source_kind": "pack", "source_id": pack_id, "speed": 0})
    assert r.status_code == 409 and "offline-only" in r.text
    assert _counts(database_url) == (1, 0, 0)  # only the offline job; no evaluation, no replay
    assert sf.STUDY_PRESET_ID not in [p["preset"]["preset_id"] for p in api.get("/api/corpus/presets").json()["presets"]]


@pytest.mark.db
def test_an_ordinary_study_is_still_offered_and_prepared_through_the_app(database_url, tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, historical=False)  # 6. no study_kind / offline_only: the earlier behaviour
    root = tmp_path / "data"
    api = TestClient(create_app(database_url, tmp_path / "art", web_dist=tmp_path / "no-ui", data_root=root))
    listed = {p["preset"]["preset_id"]: p for p in api.get("/api/corpus/presets").json()["presets"]}
    view = listed[sf.STUDY_PRESET_ID]
    assert view["classification"]["note"] == PROSPECTIVE_NOTE and "study_kind" not in view["classification"]
    r = api.post(f"/api/corpus/presets/{sf.STUDY_PRESET_ID}/prepare")
    assert r.status_code == 201, r.text
    assert _counts(database_url)[0] == 1
