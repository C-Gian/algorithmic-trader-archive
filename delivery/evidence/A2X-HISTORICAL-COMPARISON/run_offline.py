"""Descriptive historical comparison v0.6 / v0.6-a2x: ONE offline processing of the pack for one policy.

Same construction as ``A-REACTION-EFFICIENCY-EXPLORATION/run_v06_offline.py`` (the app's adviser evaluation job without
database or services): ``temporal_config(feed manifest, MP-001 dependencies)`` and ``engine_config(feed manifest, pack
manifest, build, method)`` pin the engine; one ``observe.kernel.Kernel`` applies every canonical line of the
receipt-pinned feed cache in order; ``Kernel.finish`` runs the declared clock end (2026-01-01T06:05Z). The core is built
from the pinned identity (``config_from_engine`` refuses a different packaged release). The EXPERIMENTAL variant is
selected only here, explicitly (``engine_config(..., experimental=True)``); nothing is installed or offered by the app.

No economic evaluator (runtime evaluator None). The passive trace of ``instrument.py`` is installed on the core.

Outputs (outside Git, in <out_dir>): ``journal.jsonl.gz`` (every professional journal entry, in order),
``trace.jsonl.gz`` (instrument events), ``progress.log`` and ``run_manifest.json`` (identities, counts, hashes; a copy
``run_manifest_<method>.json`` is written next to this script). Nothing is read from or written to the Owner stack.

Run from the repository root:
  .venv/Scripts/python.exe delivery/evidence/A2X-HISTORICAL-COMPARISON/run_offline.py <data_root> <out_dir> <build_sha> <v0.6|v0.6-a2x>
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from instrument import install  # noqa: E402

from algotrader.adviser.engine import _runtime_cls, config_from_engine, engine_config, release  # noqa: E402
from algotrader.adviser.harness import mp001_dependencies  # noqa: E402
from algotrader.feed.ordering import default_freshness  # noqa: E402
from algotrader.observe import feedcache as fc  # noqa: E402
from algotrader.observe.kernel import Kernel, new_temporal, temporal_config  # noqa: E402

PACK_ID = "pack-1ae7d36c20adbde0a468a7e0f6d8750a9951aa8e"
MANIFEST_SHA256 = "1bec1f1575306d4444969569675e28bfdc9dac60e2d6f461b283871362221f92"
METHODS = ("v0.6", "v0.6-a2x")
TAKE_EVERY = 20000


def main(data_root: Path, out: Path, build: str, method: str) -> None:
    if method not in METHODS:
        raise SystemExit(f"method must be one of {METHODS}")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "journal.jsonl.gz").exists():
        raise SystemExit(f"{out} already holds a journal: one processing per policy only")
    log = (out / "progress.log").open("a", encoding="utf-8")

    def note(msg: str) -> None:
        line = f"{datetime.now(UTC).isoformat()} {msg}"
        print(line, flush=True)
        log.write(line + "\n")
        log.flush()

    raw = (data_root / "packs" / PACK_ID / "manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise SystemExit("pack manifest differs from the registered hash: stop")
    pack = json.loads(raw)
    feed = pack["feed"]
    cache = fc.open_cache(data_root, feed["cache_id"], expected_manifest_sha256=feed["cache_manifest_sha256"])
    fm = cache.feed_manifest
    engine = {"temporal": temporal_config(fm, dependencies=mp001_dependencies()),
              "adviser": engine_config(fm, pack, build, method, experimental=(method == "v0.6-a2x"))}
    rt_cls, core_cls = _runtime_cls(release(engine))
    runtime = rt_cls(core_cls(config_from_engine(engine)), None)  # frozen core, no evaluator
    core = runtime.core
    jpath, tpath = out / "journal.jsonl.gz", out / "trace.jsonl.gz"
    tf = gzip.open(tpath, "wt", encoding="utf-8", compresslevel=6)
    tcount: dict[str, int] = {}

    def write(ev: dict) -> None:
        tcount[ev["ev"]] = tcount.get(ev["ev"], 0) + 1
        tf.write(json.dumps(ev, sort_keys=True, default=str) + "\n")

    install(core, write)
    kernel = Kernel(cache.feed_meta, default_freshness(), None, fc.initial_commitment(cache.cache_id),
                    new_temporal(fm, engine), runtime)
    clock_end = datetime.fromisoformat(engine["adviser"]["clock_end"].replace("Z", "+00:00"))
    note(f"start: pack {PACK_ID}, cache {cache.cache_id}, {fm.event_count} events, method {method}, build {build}")

    jf = gzip.open(jpath, "wt", encoding="utf-8", compresslevel=6)
    counts: dict[str, int] = {}
    last_chain = None
    t0 = time.monotonic()

    def drain() -> None:
        nonlocal last_chain
        journal, records = runtime.take()
        if records:
            raise SystemExit("an evaluation record was produced without an evaluator: stop")
        for e in journal:
            counts[e["kind"]] = counts.get(e["kind"], 0) + 1
            last_chain = e.get("chain")
            jf.write(json.dumps(e, default=str, sort_keys=True) + "\n")

    reader = fc.CacheReader(cache)
    for seq, line in reader.iter_from(0):
        kernel.apply_line(line)
        if (seq + 1) % TAKE_EVERY == 0:
            drain()
            el = time.monotonic() - t0
            note(f"applied {seq + 1}/{fm.event_count} events, clock {kernel.as_of().isoformat()}, "
                 f"elapsed {el:.0f}s, ETA {el / (seq + 1) * (fm.event_count - seq - 1):.0f}s")
    drain()
    note("feed applied; professional finish at the declared clock end")
    kernel.finish(clock_end)
    drain()
    if runtime.core is not core:
        raise SystemExit("the runtime replaced its core: the trace would be incomplete")
    jf.close()
    tf.close()
    elapsed = time.monotonic() - t0

    def sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    manifest = {
        "purpose": f"single offline {method} processing of the pack for the v0.6 / v0.6-a2x descriptive comparison "
                   "(no evaluator; passive trace)",
        "pack_id": PACK_ID, "pack_manifest_sha256": MANIFEST_SHA256, "cache_id": cache.cache_id,
        "cache_manifest_sha256": cache.manifest_sha256, "feed_content_identity": fm.content_identity,
        "build": build, "method": method, "engine": engine, "evaluator": None,
        "events_applied": kernel.cursor, "final_input_commitment": kernel.commitment.hex(),
        "temporal_commitment": kernel.temporal.commitment(), "adviser_commitment": runtime.commitment(),
        "clock_end": engine["adviser"]["clock_end"], "journal_counts": dict(sorted(counts.items())),
        "journal_entries": sum(counts.values()), "journal_last_chain": last_chain,
        "trace_counts": dict(sorted(tcount.items())),
        "a2x_counters": core.counters.get("a2x"),
        "outputs_outside_git": {"journal.jsonl.gz": sha(jpath), "trace.jsonl.gz": sha(tpath)},
        "elapsed_seconds": round(elapsed, 1), "python": sys.version.split()[0],
    }
    text = json.dumps(manifest, indent=1, default=str) + "\n"
    (out / "run_manifest.json").write_text(text, encoding="utf-8")
    (HERE / f"run_manifest_{method}.json").write_text(text, encoding="utf-8")
    note(f"done: {kernel.cursor} events, {sum(counts.values())} journal entries, {elapsed:.0f}s")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4])
