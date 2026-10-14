"""A confirmed direction, historical replication [2025-01-01, 2025-05-01): run the registered probe UNCHANGED.

``probe.py`` (registered at ``6f3ac03``, delivered at ``cd579d5``) is loaded from its own file after its SHA-256 is
checked byte for byte. Its only population constant ``WINDOW`` is set to the authorized replication population; every
geometry, barrier, time, outcome, check and output rule is the registered one. Births before the population (the
initialization) keep the probe's ``warmup`` label and are tabulated separately; births at/after its end keep the
``tail`` label and are never added (the probe's registered tail check reports any).

  python replicate.py run <run_dir> <out_dir>
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE.parent / "A-CONFIRMED-DIRECTION-REFERENCE" / "probe.py"
PROBE_SHA256 = "ffc9833094347ff8eb910bd6a370859cb15ce6582518a1da58e5f67a092694a0"
POPULATION = ("2025-01-01T00:00:00Z", "2025-05-01T00:00:00Z")


def load_probe():
    raw = PROBE.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != PROBE_SHA256:
        raise SystemExit(f"probe.py is not the registered file ({got} != {PROBE_SHA256}): stop")
    spec = importlib.util.spec_from_file_location("probe", PROBE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["probe"] = mod
    spec.loader.exec_module(mod)
    mod.WINDOW = POPULATION  # the population interval of this replication, nothing else
    return mod


if __name__ == "__main__":
    if sys.argv[1] != "run":
        raise SystemExit(__doc__)
    load_probe().main_run(Path(sys.argv[2]), Path(sys.argv[3]))
