"""v0.7 historical policy study: ONE offline v0.7 adviser evaluation of one pack, with the ordinary economic evaluator.

The same construction as the application's adviser-evaluation job (``observe/job.py``), without database or services:
``engine = {temporal: temporal_config(feed manifest, MP-001 dependencies), adviser: engine_config(feed manifest, pack
manifest, build, "v0.7")}``; ``adviser.engine.new_runtime(engine)`` builds the frozen v0.7 core AND the pinned
evaluator (``new_evaluator`` refuses a different evaluator identity); one ``observe.kernel.Kernel`` applies every
canonical line of the receipt-pinned feed cache in order; ``Kernel.finish`` runs the declared clock end. The report is
the application's own ``adviser.report7.build`` (the function ``evaluation/api.adviser_section`` calls) on the
journal and evaluation records in sequence order, the final ``core.inspect()`` view, status ``completed`` and
``clock_end_reached``.

Outputs outside Git (<out_dir>): ``journal.jsonl.gz``, ``records.jsonl.gz``, ``progress.log``, ``report.json``,
``report.md`` and ``run_manifest.json`` (identities, counts, hashes); the manifest and the report are copied next to
this script under ``<label>/``. Nothing is read from or written to the Owner stack; no app route is used.

  .venv/Scripts/python.exe delivery/evidence/V07-HISTORICAL-POLICY-STUDY/run_v07_economic.py \\
      <label> <data_root> <out_dir> <build_sha> <pack_id> <pack_manifest_sha256>
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

from algotrader.adviser import report7  # noqa: E402
from algotrader.adviser.engine import engine_config, new_runtime  # noqa: E402
from algotrader.adviser.harness import mp001_dependencies  # noqa: E402
from algotrader.feed.ordering import default_freshness  # noqa: E402
from algotrader.observe import feedcache as fc  # noqa: E402
from algotrader.observe.kernel import Kernel, new_temporal, temporal_config  # noqa: E402

HERE = Path(__file__).resolve().parent
METHOD = "v0.7"
RULES_V07 = "1f3704f4453bc3ab7528e9de916d05d64e2e0955c0ef81170c26694bf719b39f"
REGISTER_V07 = "8525ec74e2ccbaf0834137312c05aff59bae4714a76221d9f42b426ea7d5569c"
EVALUATOR_SHA = "85504d5843e144d0b86a0ee3e693c064f4d7f64e7928c1e54fb9c9e9f308615c"
TAKE_EVERY = 20000


def main(label: str, data_root: Path, out: Path, build: str, pack_id: str, manifest_sha: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    log = (out / "progress.log").open("a", encoding="utf-8")

    def note(msg: str) -> None:
        line = f"{datetime.now(UTC).isoformat()} {msg}"
        print(line, flush=True)
        log.write(line + "\n")
        log.flush()

    raw = (data_root / "packs" / pack_id / "manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest_sha:
        raise SystemExit("pack manifest differs from the registered hash: stop")
    pack = json.loads(raw)
    feed = pack["feed"]
    cache = fc.open_cache(data_root, feed["cache_id"], expected_manifest_sha256=feed["cache_manifest_sha256"])
    fm = cache.feed_manifest
    engine = {"temporal": temporal_config(fm, dependencies=mp001_dependencies()),
              "adviser": engine_config(fm, pack, build, METHOD)}
    ident = engine["adviser"]["identity"]
    if (ident["rules_sha256"], ident["register_sha256"], ident["implementation"]) != (
            RULES_V07, REGISTER_V07, "adviser.core.v7") or engine["adviser"]["evaluator"]["sha256"] != EVALUATOR_SHA:
        raise SystemExit("engine or evaluator identity differs from the registration: stop")
    runtime = new_runtime(engine)  # frozen v0.7 core + the pinned ordinary evaluator
    kernel = Kernel(cache.feed_meta, default_freshness(), None, fc.initial_commitment(cache.cache_id),
                    new_temporal(fm, engine), runtime)
    clock_end = datetime.fromisoformat(engine["adviser"]["clock_end"].replace("Z", "+00:00"))
    note(f"start {label}: pack {pack_id}, cache {cache.cache_id}, {fm.event_count} events, method {METHOD}, "
         f"build {build}, evaluator {EVALUATOR_SHA[:12]}")
    jpath, rpath = out / "journal.jsonl.gz", out / "records.jsonl.gz"
    jf = gzip.open(jpath, "wt", encoding="utf-8", compresslevel=6)
    rf = gzip.open(rpath, "wt", encoding="utf-8", compresslevel=6)
    journal: list[dict] = []
    records: list[dict] = []
    counts: dict[str, int] = {}
    rcounts: dict[str, int] = {}
    t0 = time.monotonic()

    def drain() -> None:
        j, r = runtime.take()
        for e in j:
            counts[e["kind"]] = counts.get(e["kind"], 0) + 1
            jf.write(json.dumps(e, default=str, sort_keys=True) + "\n")
            journal.append({"seq": e["seq"], "kind": e["kind"],  # as the app reads it back (timestamptz isoformat)
                            "clock_time": datetime.fromisoformat(str(e["clock_time"]).replace("Z", "+00:00")).isoformat(),
                            "record": json.loads(json.dumps(e["record"], default=str))})
        for x in r:
            rcounts[x["kind"]] = rcounts.get(x["kind"], 0) + 1
            rf.write(json.dumps(x, default=str, sort_keys=True) + "\n")
            records.append({"seq": x["seq"], "kind": x["kind"], "record": json.loads(json.dumps(x["record"], default=str))})

    reader = fc.CacheReader(cache)
    for seq, line in reader.iter_from(0):
        kernel.apply_line(line)
        if (seq + 1) % TAKE_EVERY == 0:
            drain()
            el = time.monotonic() - t0
            note(f"applied {seq + 1}/{fm.event_count}, clock {kernel.as_of().isoformat()}, elapsed {el:.0f}s")
    drain()
    note("feed applied; finish at the declared clock end")
    kernel.finish(clock_end)
    drain()
    jf.close()
    rf.close()
    view = json.loads(json.dumps(runtime.core.inspect(), default=str))
    rep = report7.build(engine=engine, journal=journal, records=records, view=view, status="completed",
                        clock_end_reached=True)
    rep_text = json.dumps(rep, indent=1, default=str, sort_keys=True) + "\n"
    md_text = "\n".join(report7.render_markdown(rep)) + "\n"
    (out / "report.json").write_text(rep_text, encoding="utf-8", newline="\n")
    (out / "report.md").write_text(md_text, encoding="utf-8", newline="\n")
    elapsed = time.monotonic() - t0

    def sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    manifest = {
        "purpose": f"single offline v0.7 adviser evaluation with the ordinary evaluator ({label})",
        "label": label, "pack_id": pack_id, "pack_manifest_sha256": manifest_sha, "cache_id": cache.cache_id,
        "cache_manifest_sha256": cache.manifest_sha256, "feed_content_identity": fm.content_identity,
        "build": build, "method": METHOD, "engine": engine, "events_applied": kernel.cursor,
        "final_input_commitment": kernel.commitment.hex(), "temporal_commitment": kernel.temporal.commitment(),
        "adviser_commitment": runtime.commitment(), "clock_end": engine["adviser"]["clock_end"],
        "journal_counts": dict(sorted(counts.items())), "journal_entries": sum(counts.values()),
        "record_counts": dict(sorted(rcounts.items())), "records": sum(rcounts.values()),
        "outputs_outside_git": {"journal.jsonl.gz": sha(jpath), "records.jsonl.gz": sha(rpath),
                                "report.json": sha(out / "report.json"), "report.md": sha(out / "report.md")},
        "elapsed_seconds": round(elapsed, 1), "python": sys.version.split()[0]}
    text = json.dumps(manifest, indent=1, default=str) + "\n"
    (out / "run_manifest.json").write_text(text, encoding="utf-8")
    dest = HERE / label
    dest.mkdir(exist_ok=True)
    (dest / "run_manifest.json").write_text(text, encoding="utf-8", newline="\n")
    (dest / "report.json").write_text(rep_text, encoding="utf-8", newline="\n")
    (dest / "report.md").write_text(md_text, encoding="utf-8", newline="\n")
    note(f"done {label}: {kernel.cursor} events, {sum(counts.values())} journal entries, "
         f"{sum(rcounts.values())} evaluation records, {elapsed:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6])
