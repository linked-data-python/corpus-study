"""Extract RDF-heavy code regions from the sampled files.

A *region* is a function/method (with decorators) or, when RDF operations
live at module level or are spread thin, the whole file.  For each sampled
file the extractor:

  1. re-analyses the file and attributes every detected RDF operation to its
     innermost enclosing function;
  2. keeps functions with at least ``min_rdf_ops`` operations and at most
     ``max_region_loc`` physical lines;
  3. reconstructs the *context* a region needs: the module's rdflib imports
     and the module-level bindings (namespaces, graphs, constants) whose
     names the region reads but does not bind;
  4. falls back to the whole file when qualifying regions would cover less
     than ``coverage_threshold`` of the file's RDF operations (extracting a
     region that hides most of the file's RDF work would be misleading).

Output: results/raw/regions.jsonl — one record per region, with provenance
(repository, commit, file, qualname, line span), the source, the context
lines, and the region's RDF metrics.
"""

from __future__ import annotations

import ast
import json

from .acquire import repo_dir
from .analyze import analyze_source
from .config import RESULTS_RAW, provenance
from .sample import load_sample

REGIONS_PATH = RESULTS_RAW / "regions.jsonl"


def _functions(tree: ast.Module):
    """Yield (qualname, node) for every function/method, innermost last."""
    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}{child.name}"
                yield qual, child
                yield from walk(child, qual + ".")
            elif isinstance(child, ast.ClassDef):
                yield from walk(child, f"{prefix}{child.name}.")
    yield from walk(tree, "")


def _span(node: ast.AST) -> tuple[int, int]:
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return start, node.end_lineno


def _names_read(node: ast.AST) -> set[str]:
    bound: set[str] = set()
    read: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            (bound if isinstance(sub.ctx, (ast.Store, ast.Del)) else read).add(sub.id)
        elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bound.add(sub.name)
            bound.update(a.arg for a in sub.args.args + sub.args.kwonlyargs
                         + sub.args.posonlyargs)
            if sub.args.vararg:
                bound.add(sub.args.vararg.arg)
            if sub.args.kwarg:
                bound.add(sub.args.kwarg.arg)
        elif isinstance(sub, ast.ExceptHandler) and sub.name:
            bound.add(sub.name)
    import builtins
    return read - bound - set(dir(builtins))


def _module_context(tree: ast.Module, source_lines: list[str],
                    needed: set[str]) -> list[str]:
    """Module-level statements binding names the region reads: imports and
    simple assignments (namespace/constant definitions), in file order."""
    ctx: list[str] = []
    for stmt in tree.body:
        binds: set[str] = set()
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            for alias in stmt.names:
                binds.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name):
                    binds.add(t.id)
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            binds.add(stmt.target.id)
        if binds & needed:
            ctx.append("\n".join(source_lines[stmt.lineno - 1:stmt.end_lineno]))
    return ctx


def extract_regions(source: str, rcfg: dict) -> list[dict]:
    """Pure extraction logic (testable without a corpus checkout)."""
    fa = analyze_source(source)
    if fa.error or not fa.ops:
        return []
    tree = ast.parse(source)
    lines = source.splitlines()

    # innermost-function attribution: order candidate functions by span size
    funcs = list(_functions(tree))
    regions: list[dict] = []
    op_lines = [op.lineno for op in fa.ops]

    def ops_in(lo: int, hi: int) -> list:
        return [op for op in fa.ops if lo <= op.lineno <= hi]

    # innermost wins: for each op, find the smallest enclosing function span
    covered_ops: set[int] = set()
    candidates = []
    for qual, node in funcs:
        lo, hi = _span(node)
        n_ops = len(ops_in(lo, hi))
        loc = hi - lo + 1
        if n_ops >= rcfg["min_rdf_ops"] and loc <= rcfg["max_region_loc"]:
            candidates.append((qual, node, lo, hi, n_ops, loc))
    # prefer smaller (more focused) regions; drop candidates nested inside an
    # already-kept candidate
    candidates.sort(key=lambda c: c[5])
    kept: list[tuple] = []
    for cand in candidates:
        _, _, lo, hi, _, _ = cand
        if any(k[2] <= lo and hi <= k[3] for k in kept):
            continue
        if any(lo <= k[2] and k[3] <= hi for k in kept):
            continue    # an inner region was already kept
        kept.append(cand)

    for qual, node, lo, hi, n_ops, loc in sorted(kept, key=lambda c: c[2]):
        seg = "\n".join(lines[lo - 1:hi])
        needed = _names_read(node)
        ctx = _module_context(tree, lines, needed)
        ops = ops_in(lo, hi)
        covered_ops.update(id(o) for o in ops)
        regions.append({
            "kind": "function",
            "qualname": qual,
            "lineno": lo, "end_lineno": hi,
            "loc": loc, "rdf_ops": n_ops,
            "categories": _cat_counts(ops),
            "source": seg,
            "context": ctx,
        })

    coverage = (len(covered_ops) / len(fa.ops)) if fa.ops else 0.0
    if not regions or coverage < rcfg.get("coverage_threshold", 0.5):
        return [{
            "kind": "file",
            "qualname": "<module>",
            "lineno": 1, "end_lineno": len(lines),
            "loc": len(lines), "rdf_ops": len(fa.ops),
            "categories": _cat_counts(fa.ops),
            "source": source,
            "context": [],
            "note": (f"whole file kept: function regions covered "
                     f"{coverage:.0%} of RDF operations"),
        }]
    return regions


def _cat_counts(ops) -> dict:
    counts: dict[str, int] = {}
    for op in ops:
        counts[op.category] = counts.get(op.category, 0) + 1
    return dict(sorted(counts.items()))


def run(config: dict) -> None:
    rcfg = config["regions"]
    sample = load_sample()
    out: list[dict] = []
    for band, files in sample["sample"].items():
        for f in files:
            root = repo_dir(config, f["repository"])
            path = root / f["path"]
            try:
                source = path.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                print(f"  ! {f['repository']}/{f['path']}: {e}")
                continue
            regs = extract_regions(source, rcfg)
            for i, reg in enumerate(regs):
                reg.update({
                    "region_id": f"{f['repository'].replace('/', '__')}"
                                 f"__{f['path'].replace('/', '_')}"
                                 f"__{reg['qualname'].replace('.', '_')}",
                    "repository": f["repository"],
                    "commit": f["commit"],
                    "path": f["path"],
                    "band": band,
                    "file_rdf_node_density": f["rdf_node_density"],
                })
                out.append(reg)
    REGIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGIONS_PATH, "w") as fh:
        fh.write(json.dumps({"provenance": provenance(config)}) + "\n")
        for reg in out:
            fh.write(json.dumps(reg, ensure_ascii=False) + "\n")
    n_files = len({(r['repository'], r['path']) for r in out})
    print(f"regions: {len(out)} regions from {n_files} files "
          f"({sum(1 for r in out if r['kind'] == 'file')} whole-file)")


def load_regions() -> list[dict]:
    if not REGIONS_PATH.exists():
        raise SystemExit("no regions; run `rdfeval regions` first")
    rows = [json.loads(line) for line in REGIONS_PATH.read_text().splitlines()
            if line.strip()]
    return [r for r in rows if "region_id" in r]
