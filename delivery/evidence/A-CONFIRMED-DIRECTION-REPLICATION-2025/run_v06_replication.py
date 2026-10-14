"""A confirmed direction, historical replication [2025-01-01, 2025-05-01): the single offline v0.6 processing.

Copied from ``A-REACTION-EFFICIENCY-EXPLORATION/run_v06_offline.py`` (same kernel construction); only the pack identity
is an argument (checked against the hash registered in REGISTRATION.md section 7 before anything is applied), the frozen
v0.6 rules/register identity is checked, and the run manifest is copied next to this script.

The same construction as the app's adviser evaluation job (``observe/job.py``), without database or services:
``temporal_config(feed manifest, MP-001 dependencies)`` and ``engine_config(feed manifest, pack manifest, build,
"v0.6")`` pin the engine; one ``observe.kernel.Kernel`` applies every canonical line of the receipt-pinned feed cache
in order (factual reducer -> temporal clock policy -> professional barriers -> admission); ``Kernel.finish`` runs the
declared finite clock end (the pack's, 2025-05-01T06:05Z). The frozen v0.6 core is built from the pinned identity
(``config_from_engine`` refuses any other packaged release).

No economic evaluator: the runtime is built with evaluator None. The existing tests
``test_evaluator_disabled_leaves_every_professional_record_identical`` (v0.3+) and
``test_evaluator_on_off_and_appended_future_do_not_change_professional_records`` (v0.4) assert digest-identical
professional records with and without it. No path/economic record is produced.

Outputs (outside Git, in <out_dir>): ``journal.jsonl.gz`` (every professional journal entry, in order),
``trade_bars.csv.gz`` (every admitted trade 1m event: interval, available_time, OHLC; non-observations as gaps),
``progress.log`` (durable progress) and ``run_manifest.json`` (identities, counts, hashes; also copied next to this
script). Nothing is read from or written to the Owner stack.

Run from the repository root:
  .venv/Scripts/python.exe delivery/evidence/A-CONFIRMED-DIRECTION-REPLICATION-2025/run_v06_replication.py       <data_root> <out_dir> <build_sha> <pack_id> <pack_manifest_sha256>
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from algotrader.adviser.engine import _runtime_cls, config_from_engine, engine_config, release  # noqa: E402
from algotrader.adviser.harness import mp001_dependencies  # noqa: E402
from algotrader.feed.ordering import default_freshness  # noqa: E402
from algotrader.observe import feedcache as fc  # noqa: E402
from algotrader.observe.kernel import Kernel, new_temporal, temporal_config  # noqa: E402

METHOD = "v0.6"
RULES_V06 = "57bf2309990d5085326f62fae9e6a88808b1de566a837995341910692e832e66"
REGISTER_V06 = "98ef101e4c23fbdfee80b2e1f0adf61eea92aeb8665db777bb8582b0ae4c5bda"
TAKE_EVERY = 20000


def main(data_root: Path, out: Path, build: str, PACK_ID: str, MANIFEST_SHA256: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
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
              "adviser": engine_config(fm, pack, build, METHOD)}
    ident = engine["adviser"]["identity"]
    if (ident["rules_sha256"], ident["register_sha256"], ident["implementation"]) != (
            RULES_V06, REGISTER_V06, "adviser.core.v6"):
        raise SystemExit(f"engine identity is not the frozen v0.6: {ident}: stop")
    rt_cls, core_cls = _runtime_cls(release(engine))
    runtime = rt_cls(core_cls(config_from_engine(engine)), None)  # frozen v0.6 core, no evaluator
    kernel = Kernel(cache.feed_meta, default_freshness(), None, fc.initial_commitment(cache.cache_id),
                    new_temporal(fm, engine), runtime)
    clock_end = datetime.fromisoformat(engine["adviser"]["clock_end"].replace("Z", "+00:00"))
    note(f"start: pack {PACK_ID}, cache {cache.cache_id}, {fm.event_count} events, method {METHOD}, build {build}")

    jpath, bpath = out / "journal.jsonl.gz", out / "trade_bars.csv.gz"
    jf = gzip.open(jpath, "wt", encoding="utf-8", compresslevel=6)
    bf = gzip.open(bpath, "wt", encoding="utf-8", compresslevel=6)
    bf.write("start,end,available_time,kind,open,high,low,close\n")
    counts: dict[str, int] = {}
    last_chain = None
    n_bars = n_gaps = 0
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
        e = kernel.apply_line(line)
        if e.channel.family.value == "trade_bar_1m":
            if e.kind.value == "bar_observation":
                p = e.payload
                bf.write(f"{e.event_time.isoformat()},{e.event_end_time.isoformat()},{e.available_time.isoformat()},"
                         f"bar,{p.open},{p.high},{p.low},{p.close}\n")
                n_bars += 1
            else:
                bf.write(f"{e.event_time.isoformat()},,{e.available_time.isoformat()},{e.kind.value},,,,\n")
                n_gaps += 1
        if (seq + 1) % TAKE_EVERY == 0:
            drain()
            el = time.monotonic() - t0
            note(f"applied {seq + 1}/{fm.event_count} events, clock {kernel.as_of().isoformat()}, "
                 f"elapsed {el:.0f}s, ETA {el / (seq + 1) * (fm.event_count - seq - 1):.0f}s")
    drain()
    note("feed applied; professional finish at the declared clock end")
    kernel.finish(clock_end)
    drain()
    jf.close()
    bf.close()
    elapsed = time.monotonic() - t0

    def sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    manifest = {
        "purpose": "single offline v0.6 processing of the pack for the A confirmed-direction historical replication "
                   "[2025-01-01, 2025-05-01) (no evaluator)",
        "pack_id": PACK_ID, "pack_manifest_sha256": MANIFEST_SHA256, "cache_id": cache.cache_id,
        "cache_manifest_sha256": cache.manifest_sha256, "feed_content_identity": fm.content_identity,
        "build": build, "method": METHOD, "engine": engine, "evaluator": None,
        "events_applied": kernel.cursor, "final_input_commitment": kernel.commitment.hex(),
        "temporal_commitment": kernel.temporal.commitment(), "adviser_commitment": runtime.commitment(),
        "clock_end": engine["adviser"]["clock_end"], "journal_counts": dict(sorted(counts.items())),
        "journal_entries": sum(counts.values()), "journal_last_chain": last_chain,
        "trade_bars": n_bars, "trade_non_observations": n_gaps,
        "outputs_outside_git": {"journal.jsonl.gz": sha(jpath), "trade_bars.csv.gz": sha(bpath)},
        "elapsed_seconds": round(elapsed, 1), "python": sys.version.split()[0],
    }
    text = json.dumps(manifest, indent=1, default=str) + "\n"
    (out / "run_manifest.json").write_text(text, encoding="utf-8")
    (Path(__file__).resolve().parent / "run_manifest.json").write_text(text, encoding="utf-8")
    note(f"done: {kernel.cursor} events, {sum(counts.values())} journal entries, {elapsed:.0f}s")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])
