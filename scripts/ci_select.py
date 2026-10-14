"""Reproducible test selection for CI and local work (standard library only; no test is run here).

Every changed path is classified, then the pytest files that can observe the change are found on one dependency
graph of the repository's Python files:

* static imports anywhere in a file (module level or inside functions), with their parent packages;
* module names written as strings (``"-m", "algotrader.cli"``: the E2E stack starts the whole app this way);
* references to a tracked file - its file name anywhere in the text, or a path written as string segments whose
  segments occur contiguously in the file's path, at least one of them non-generic (``ROOT / "web" / "src"``,
  ``"delivery/evidence/X"``, ``SCHEMA_DIR = ... / "schemas"``; ``"web" / "dist"`` names the build, not ``web/src``);
* every test file depends on ``tests/conftest.py`` (loaded for every test); every E2E file on every ``web/`` file
  (the E2E stack serves the web build).

A test file is selected when anything it reaches changed. Scopes, in increasing order:

``docs``    documentation/evidence only; tests that read a changed file are still selected;
``ui``      the web app (plus docs): web typecheck/build, the tests that reach ``web/`` (all E2E) and the compose smoke;
``engine``  Python sources, method documents, schemas, tests or scripts: the reached tests (the E2E stack reaches
            the whole app, so every E2E file is selected for any ``src/`` change) and the compose smoke;
``full``    everything, as before this selector existed. Conservative fallback for shared components (dependencies,
            toolchain, Docker, CI, the selector itself, ``tests/conftest.py``), unknown paths, deleted or renamed
            files of any type, unparsable files, a changed file no test reaches, an unknown base, or an explicit request.

Nothing is skipped silently: the report lists each changed path with its class and every excluded test file.

Usage::

    python scripts/ci_select.py --base <sha>               # committed changes base..HEAD
    python scripts/ci_select.py --base HEAD --worktree     # local: uncommitted + untracked changes as well
    python scripts/ci_select.py --base <sha> --github      # CI: writes $GITHUB_OUTPUT and $GITHUB_STEP_SUMMARY
    python scripts/ci_select.py --full --reason "..."      # explicit full run
"""

from __future__ import annotations

import argparse
import ast
import functools
import json
import math
import os
import re
import subprocess
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path

# ci_select: no-references
ROOT = Path(__file__).resolve().parents[1]
SELF = "scripts/ci_select.py"
# A file containing this marker names paths only as data; its path strings create no reference edges (its imports
# still count). Used by the selector and its own tests; the selector itself is a shared component (full run).
NO_REFERENCES = "ci_select: " + "no-references"
SCOPES = ("docs", "ui", "engine", "full")

# shared components: a change here can affect any check -> full
SHARED = {
    "pyproject.toml", "uv.lock", ".python-version", ".nvmrc", "Dockerfile", "docker-compose.yml", ".dockerignore",
    ".gitattributes", ".gitignore", SELF, "tests/conftest.py", "ci/test_durations.json",
}
SHARED_PREFIXES = (".github/",)
ROOT_DOCS = {"README.md", "STATE.md", "FOUNDATION.md", "AGENTS.md", "task.md", "CLAUDE.md"}
DOC_PREFIXES = ("delivery/", "research/", "strategic_reviews/", "source_notes/")
UI_PREFIXES = ("web/",)
# inputs of the Docker image / compose smoke besides src/ and web/
COMPOSE_INPUTS = {"scripts/build_commit.py", "scripts/stack_smoke.py"}  # README is copied only as package metadata
# directory names too generic to count as a reference on their own (file names still count)
GENERIC_DIRS = {"src", "algotrader", "tests", "e2e", "delivery", "evidence", "research", "strategic_reviews",
                "source_notes", "scripts", "method", "adviser"}
MODULE_STRING = re.compile(r"^(algotrader(?:\.\w+)*)(?::\w+)?$")
# estimated seconds per shard (each shard also pays ~1-2 min of runner setup)
MAX_UNIT_SHARDS, UNIT_SHARD_TARGET = 8, 600.0
MAX_E2E_SHARDS, E2E_SHARD_TARGET = 3, 240.0


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True,
                          encoding="utf-8").stdout


def tracked_files() -> list[str]:
    return [p for p in git("ls-files", "-z").split("\0") if p]


@dataclass
class Change:
    path: str
    status: str            # A/M/D, or R for the old path of a rename (the new path is listed as A)
    cls: str = ""          # docs / ui / engine / full
    renamed_to: str = ""
    reason: str = ""
    reached_by: list[str] = field(default_factory=list)


def changed_paths(base: str | None, worktree: bool) -> list[Change]:
    out: dict[str, Change] = {}
    if base is not None:
        # committed: merge-base(base, HEAD)..HEAD; worktree: base against the working tree (staged and unstaged)
        raw = git("diff", "--name-status", "-M", "-z", base if worktree else f"{base}...HEAD")
        parts = [p for p in raw.split("\0") if p]
        i = 0
        while i < len(parts):
            st = parts[i][0]
            if st in ("R", "C"):
                old, new = parts[i + 1], parts[i + 2]
                out[old] = Change(old, "R", renamed_to=new) if st == "R" else Change(old, "M")
                out[new] = Change(new, "A")
                i += 3
            else:
                out[parts[i + 1]] = Change(parts[i + 1], st)
                i += 2
    if worktree:
        for p in git("ls-files", "--others", "--exclude-standard", "-z").split("\0"):
            if p:
                out.setdefault(p, Change(p, "A"))
    return [out[k] for k in sorted(out)]


# ---- dependency graph ------------------------------------------------------------------------------------------------

def module_names(files: list[str]) -> dict[str, str]:
    """Importable module name -> path for src/ packages and the tests directories (pytest prepends them)."""
    mods: dict[str, str] = {}
    for p in files:
        if not p.endswith(".py"):
            continue
        parts = p[:-3].split("/")
        if parts[0] == "src":
            parts = parts[1:]
            if parts[-1] == "__init__":
                parts = parts[:-1]
            mods[".".join(parts)] = p
        elif parts[0] == "tests":
            mods.setdefault(parts[-1], p)
    return mods


def _resolve(name: str, mods: dict[str, str]) -> list[str]:
    out = []
    bits = name.split(".")
    for i in range(1, len(bits) + 1):  # parent packages execute on import
        m = ".".join(bits[:i])
        if m in mods:
            out.append(mods[m])
    return out


class Graph:
    def __init__(self, files: list[str]) -> None:
        self.files = files
        self.py = [p for p in files if p.endswith(".py") and p.split("/")[0] in ("src", "tests", "scripts")]
        self.mods = module_names(files)
        self.edges: dict[str, set[str]] = {p: set() for p in self.py}
        self.unparsable: list[str] = []
        self.texts: dict[str, str] = {}
        for p in self.py:
            text = (ROOT / p).read_text(encoding="utf-8", errors="replace")
            self.texts[p] = text
            try:
                tree = _parse(text, p)
            except SyntaxError:
                self.unparsable.append(p)
                continue
            self.edges[p] |= self._imports(p, tree)
        self._references()
        conftest = "tests/conftest.py"
        for p in self.py:
            if is_test_file(p) and conftest in self.edges:
                self.edges[p].add(conftest)

    def _imports(self, path: str, tree: ast.AST) -> set[str]:
        deps: set[str] = set()
        pkg = self._package(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    deps.update(_resolve(a.name, self.mods))
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    anchor = pkg.split(".")[: len(pkg.split(".")) - node.level + 1] if pkg else []
                    base = ".".join([*anchor, base] if base else anchor)
                deps.update(_resolve(base, self.mods))
                for a in node.names:
                    deps.update(_resolve(f"{base}.{a.name}" if base else a.name, self.mods))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                m = MODULE_STRING.match(node.value)
                if m:
                    deps.update(_resolve(m.group(1), self.mods))
        deps.discard(path)
        return deps

    @staticmethod
    def _package(path: str) -> str:
        parts = path[:-3].split("/")
        if parts[0] != "src":
            return ""
        parts = parts[1:]
        return ".".join(parts[:-1])  # the containing package (also for __init__)

    def _references(self) -> None:
        """Edges from a Python file to the tracked files it names: a file name anywhere in its text, or a path written
        as string segments (``ROOT / "web" / "src"``, ``"delivery/evidence/X"``) whose segments occur contiguously in
        the file's path and include a non-generic one. ``"web" / "dist"`` (the build output) therefore does not name
        ``web/src``. E2E tests serve the web build, so they depend on every ``web/`` file explicitly."""
        by_name: dict[str, set[str]] = {}
        by_seg: dict[str, set[str]] = {}
        segs = {f: f.split("/") for f in self.files}
        for f, parts in segs.items():
            if len(parts[-1]) >= 6 and "." in parts[-1]:
                by_name.setdefault(parts[-1], set()).add(f)
            for s in parts:
                by_seg.setdefault(s, set()).add(f)
        web = {f for f in self.files if f.startswith(UI_PREFIXES)}
        for p, text in self.texts.items():
            if NO_REFERENCES in text:  # names paths only as data (the selector and its tests)
                continue
            for name, targets in by_name.items():
                if name in text:  # a name shared by several folders links all of them (conservative)
                    self.edges[p] |= targets - {p}
            for chain in self._path_chains(p):
                if all(s in GENERIC_DIRS for s in chain):
                    continue
                for f in by_seg.get(chain[0], ()):
                    parts = segs[f]
                    if any(parts[i:i + len(chain)] == chain for i in range(len(parts) - len(chain) + 1)):
                        self.edges[p].add(f)
            if is_e2e(p):
                self.edges[p] |= web
            self.edges[p].discard(p)

    def _path_chains(self, path: str) -> list[list[str]]:
        try:
            tree = _parse(self.texts[path], path)
        except SyntaxError:
            return []
        chains: list[list[str]] = []
        inner: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) and id(node) not in inner:
                operands, todo = [], [node]
                while todo:  # flatten a / b / c (left-associative) in source order
                    n = todo.pop()
                    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
                        inner.add(id(n))
                        todo += [n.right, n.left]
                    else:
                        operands.append(n)
                run: list[str] = []
                for o in [*operands, None]:
                    if isinstance(o, ast.Constant) and isinstance(o.value, str) and o.value:
                        run += [s for s in o.value.split("/") if s]
                    elif run:
                        chains.append(run)
                        run = []
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and "/" in node.value \
                    and re.fullmatch(r"[\w.\-/]+", node.value):
                chains.append([s for s in node.value.split("/") if s])
        return [c for c in chains if c]

    def reach(self, start: str) -> set[str]:
        seen, todo = {start}, [start]
        while todo:
            for n in self.edges.get(todo.pop(), ()):
                if n not in seen:
                    seen.add(n)
                    todo.append(n)
        return seen


@functools.lru_cache(maxsize=2)
def graph(files: tuple[str, ...]) -> Graph:
    return Graph(list(files))


def _parse(text: str, path: str) -> ast.AST:
    with warnings.catch_warnings():  # invalid escapes inside test strings are the tests' business, not ours
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(text, filename=path)


def is_test_file(p: str) -> bool:
    return p.startswith("tests/") and Path(p).name.startswith("test_") and p.endswith(".py")


def is_e2e(p: str) -> bool:
    return p.startswith("tests/e2e/")


# ---- weights for balanced shards ---------------------------------------------------------------------------------

def _param_count(dec: ast.expr) -> int:
    if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "parametrize" and len(dec.args) >= 2:
        vals = dec.args[1]
        if isinstance(vals, (ast.List, ast.Tuple, ast.Set)):
            return max(1, len(vals.elts))
        return 5  # computed parameter list: unknown size
    return 1


DB_FIXTURES = {"database_url", "empty_database_url"}
# Calibrated on the 6-shard local run of 13 October 2026 (one machine, shared PostgreSQL; least squares over shards):
# about 1.3 s per non-database test and 20 s per database test; an E2E test about 20 s. Coarse - single database tests
# vary widely - and replaced by measured seconds as soon as ci/test_durations.json is committed.
COST_PLAIN, COST_DB, COST_E2E = 1.3, 20.0, 20.0


def heuristic_weight(path: str) -> float:
    """Estimated seconds when no measured durations exist: test functions x literal parametrization, a database test
    (one using database_url directly or through a fixture of the same file) costing much more."""
    text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
    try:
        tree = _parse(text, path)
    except SyntaxError:
        return 60.0
    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    args = {f.name: {a.arg for a in f.args.args} for f in funcs}
    db = set(DB_FIXTURES)
    grew = True
    while grew:
        grew = False
        for name, a in args.items():
            if not name.startswith("test") and name not in db and a & db:
                db.add(name)
                grew = True
    total = 0.0
    for f in funcs:
        if not f.name.startswith("test"):
            continue
        k = 1
        for d in f.decorator_list:
            k *= _param_count(d)
        cost = COST_E2E if is_e2e(path) else COST_DB if args[f.name] & db else COST_PLAIN
        total += k * cost
    return max(total, 1.0)


def load_durations() -> dict[str, float]:
    f = ROOT / "ci" / "test_durations.json"
    if f.is_file():
        return {k: float(v) for k, v in json.loads(f.read_text(encoding="utf-8"))["files"].items()}
    return {}


def shard(files: list[str], weights: dict[str, float], target: float, max_shards: int) -> list[list[str]]:
    if not files:
        return []
    total = sum(weights[f] for f in files)
    n = max(1, min(max_shards, len(files), math.ceil(total / target)))
    bins: list[tuple[float, int, list[str]]] = [(0.0, i, []) for i in range(n)]
    for f in sorted(files, key=lambda f: (-weights[f], f)):  # longest-processing-time first, deterministic
        bins.sort(key=lambda b: (b[0], b[1]))
        w, i, fs = bins[0]
        bins[0] = (w + weights[f], i, [*fs, f])
    return [sorted(b[2]) for b in sorted(bins, key=lambda b: b[1])]


# ---- classification ----------------------------------------------------------------------------------------------

def classify(changes: list[Change], g: Graph, tests: list[str], forced: str | None) -> tuple[str, list[str]]:
    reasons: list[str] = []
    rank = {s: i for i, s in enumerate(SCOPES)}
    scope = "docs"

    def bump(s: str) -> None:
        nonlocal scope
        if rank[s] > rank[scope]:
            scope = s

    reached: dict[str, list[str]] = {}
    for t in tests:
        for n in g.reach(t):
            reached.setdefault(n, []).append(t)
    for c in changes:
        p = c.path
        c.reached_by = sorted(reached.get(p, []))
        # the graph is built on the files present now, so the former dependants of a deleted or renamed path are
        # unknown whatever its type: full, before any classification by path
        if c.status == "D":
            c.cls, c.reason = "full", "deleted (its former dependants are not in the current graph)"
        elif c.status == "R":
            c.cls, c.reason = "full", (f"renamed to {c.renamed_to} (its former dependants are not in the current "
                                       "graph)")
        elif p in SHARED or p.startswith(SHARED_PREFIXES):
            c.cls, c.reason = "full", "shared component"
        elif p in g.unparsable:
            c.cls, c.reason = "full", "Python file that could not be parsed"
        elif p in ROOT_DOCS or p.startswith(DOC_PREFIXES):
            c.cls, c.reason = "docs", "documentation/evidence" + (" read by tests" if c.reached_by else "")
        elif p.startswith(UI_PREFIXES):
            c.cls, c.reason = "ui", "web app"
        elif p.startswith(("src/", "tests/", "scripts/", "schemas/")):
            if not c.reached_by:
                c.cls, c.reason = "full", "no test reaches this file"
            else:
                c.cls, c.reason = "engine", "code, method document, schema, test or script"
        else:
            c.cls, c.reason = "full", "unknown path"
        bump(c.cls)
        if c.cls == "full":
            reasons.append(f"{p}: {c.reason}")
    if forced:
        scope = "full"
        reasons.insert(0, forced)
    return scope, reasons


def select(base: str | None, worktree: bool, forced: str | None, changes: list[Change] | None = None) -> dict:
    """``changes`` overrides the git diff (used by the selector's own tests)."""
    files = tracked_files()
    if worktree:
        files = sorted(set(files) | {p for p in git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
                                     if p and (ROOT / p).is_file()})
    files = [f for f in files if (ROOT / f).is_file()]
    g = graph(tuple(files))
    tests = sorted(p for p in g.py if is_test_file(p))
    if changes is None:
        if base is None and not forced:
            forced = "base commit unknown"
        changes = changed_paths(base, worktree) if base is not None else []
    scope, reasons = classify(changes, g, tests, forced)
    if scope == "full":
        selected = tests
    else:
        hit = {c.path for c in changes}
        selected = sorted({t for c in changes for t in c.reached_by} | {t for t in tests if t in hit})
    unit = [t for t in selected if not is_e2e(t)]
    e2e = [t for t in selected if is_e2e(t)]
    durations = load_durations()
    weights = {t: durations.get(t) or heuristic_weight(t) for t in tests}
    unit_shards = shard(unit, weights, UNIT_SHARD_TARGET, MAX_UNIT_SHARDS)
    e2e_shards = shard(e2e, weights, E2E_SHARD_TARGET, MAX_E2E_SHARDS)
    web = scope in ("ui", "full") or any(c.path.startswith(UI_PREFIXES) for c in changes)
    compose = scope == "full" or any(c.path.startswith(("src/", "web/")) or c.path in COMPOSE_INPUTS
                                     for c in changes)
    matrix = ([{"name": f"unit {i + 1}/{len(unit_shards)}", "kind": "unit", "files": " ".join(fs)}
               for i, fs in enumerate(unit_shards)]
              + [{"name": f"e2e {i + 1}/{len(e2e_shards)}", "kind": "e2e", "files": " ".join(fs)}
                 for i, fs in enumerate(e2e_shards)])
    return {
        "scope": scope, "base": base, "full_reasons": reasons,
        "changes": [{"path": c.path, "status": c.status, "class": c.cls, "reason": c.reason,
                     "tests_reaching": len(c.reached_by)} for c in changes],
        "selected": selected, "excluded": [t for t in tests if t not in selected], "all_tests": len(tests),
        "web": web, "compose": compose, "matrix": matrix,
        "weights": "measured (ci/test_durations.json)" if durations else "heuristic (no measured durations committed)",
    }


def markdown(r: dict) -> str:
    label = {"docs": "FAST — documentation", "ui": "FAST — UI presentation", "engine": "FAST — engine/code (selected)",
             "full": "FULL suite"}[r["scope"]]
    lines = [f"## Test selection: {label}", "",
             f"Base: `{r['base'] or 'unknown'}` · test files selected {len(r['selected'])} / {r['all_tests']}"
             f" · web typecheck/build: {'yes' if r['web'] else 'no'} · compose smoke: {'yes' if r['compose'] else 'no'}"
             f" · shard weights: {r['weights']}", ""]
    if r["scope"] != "full":
        lines += ["**A green result for this scope is a FAST green, not the full-suite acceptance.**", ""]
    if r["full_reasons"]:
        lines += ["Full suite because:", *[f"- {x}" for x in r["full_reasons"]], ""]
    if not r["changes"] and r["scope"] != "full":
        lines += ["No changed path since the base: nothing to check.", ""]
    lines += ["| Changed path | Status | Class | Reason | Test files reaching it |", "|---|---|---|---|---|"]
    lines += [f"| `{c['path']}` | {c['status']} | {c['class']} | {c['reason']} | {c['tests_reaching']} |"
              for c in r["changes"]] or ["| (none) | | | | |"]
    lines += ["", "Suites run:"]
    lines += [f"- {m['name']}: {m['files'].replace(' ', ', ')}" for m in r["matrix"]] or ["- none (no test reaches the change)"]
    lines += ["", f"Excluded test files ({len(r['excluded'])}): "
              + (", ".join(Path(t).name for t in r["excluded"]) if r["excluded"] else "none"), ""]
    return "\n".join(lines)


def junit_durations(directory: Path) -> dict:
    """Per-file seconds from pytest JUnit XML reports (``--junitxml``), to refresh ci/test_durations.json."""
    import xml.etree.ElementTree as ET
    per: dict[str, float] = {}
    for x in sorted(directory.rglob("*.xml")):
        for tc in ET.parse(x).getroot().iter("testcase"):
            cls = tc.get("classname", "")
            mod = cls.split(".")
            path = None
            for i in range(len(mod), 0, -1):
                cand = "/".join(mod[:i]) + ".py"
                for pre in ("", "tests/", "tests/e2e/"):
                    if (ROOT / (pre + cand)).is_file():
                        path = pre + cand
                        break
                if path:
                    break
            if path:
                per[path] = per.get(path, 0.0) + float(tc.get("time", 0) or 0)
    return {"files": {k: round(v, 1) for k, v in sorted(per.items())}}


def write_github(r: dict, md: str, record: Path) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
        f.write(f"scope={r['scope']}\n")
        f.write(f"web={'true' if r['web'] else 'false'}\n")
        f.write(f"compose={'true' if r['compose'] else 'false'}\n")
        f.write(f"has_tests={'true' if r['matrix'] else 'false'}\n")
        f.write(f"matrix={json.dumps({'include': r['matrix']})}\n")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(md + "\n")
    record.write_text(json.dumps(r, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", help="base commit (diff base...HEAD; with --worktree the working tree is compared)")
    ap.add_argument("--worktree", action="store_true", help="include uncommitted and untracked changes")
    ap.add_argument("--full", action="store_true", help="select everything")
    ap.add_argument("--reason", default="explicit full request", help="recorded reason for --full")
    ap.add_argument("--github", action="store_true", help="write $GITHUB_OUTPUT and $GITHUB_STEP_SUMMARY")
    ap.add_argument("--json", action="store_true", help="print the selection as JSON")
    ap.add_argument("--durations-from-junit", metavar="DIR", help="print per-file seconds from JUnit XML reports")
    a = ap.parse_args(argv)
    if a.durations_from_junit:
        print(json.dumps(junit_durations(Path(a.durations_from_junit)), indent=2))
        return 0
    if a.base is not None:
        try:
            git("rev-parse", "--verify", f"{a.base}^{{commit}}")
        except subprocess.CalledProcessError:
            print(f"base {a.base!r} is not a known commit: falling back to the full suite", file=sys.stderr)
            a.base = None
    r = select(a.base, a.worktree, a.reason if a.full else None)
    md = markdown(r)
    if a.github:
        write_github(r, md, ROOT / "ci-selection.json")
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(md)
        if r["matrix"]:
            print("Local commands (database tests need ALGOTRADER_TEST_DATABASE_URL; e2e also a web build):")
            unit = [f for m in r["matrix"] if m["kind"] == "unit" for f in m["files"].split()]
            e2e = [f for m in r["matrix"] if m["kind"] == "e2e" for f in m["files"].split()]
            if r["web"]:
                print("  npm --prefix web run typecheck && npm --prefix web run build")
            if unit:
                print("  uv run pytest " + " ".join(unit))
            if e2e:
                print("  uv run pytest " + " ".join(e2e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
