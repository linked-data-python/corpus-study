"""Pairwise quantitative comparison of original.py vs translated.ldpy.

For each example whose translation is final (and not excluded), compute:

Surface size (both sides)
    loc, code_loc, chars, tokens, syntax nodes (Python: positioned AST
    nodes; ldpy: masked-AST nodes + island structure nodes — see
    rdfeval.ldpy_metrics for the exact definition).

RDF-specific complexity (both sides)
    explicit rdflib constructor calls, term constructions, namespace
    manipulation, graph construction calls, graph operations, triples
    added/expressed, RDF terms per line, triples per line, Python
    operations per triple.

RDF/code correspondence (§9 of the evaluation plan)
    scaffolding_tokens_per_triple   tokens of triple-building statements
                                    that are not part of the three terms
    nesting_per_triple              AST edges from the enclosing statement
                                    to a term (Python) / bracket depth of a
                                    term inside its island (ldpy)
    constructors_per_triple         explicit rdflib constructors / triples
    staging_assignments             assignments whose right-hand side is a
                                    single RDF term construction (a proxy
                                    for "intermediate expressions required")

Each metric is computed by code in this module or rdfeval.analyze /
rdfeval.ldpy_metrics — nothing is estimated by hand.  Rows are written to
results/raw/pairs.jsonl and results/summary/pairs.csv.
"""

from __future__ import annotations

import ast
import csv
import io
import json
import tokenize

from .analyze import SIGNIFICANT_TOKENS, analyze_source
from .config import RESULTS_RAW, RESULTS_SUMMARY, provenance
from .ldpy_metrics import LdpyMetricsError, measure_ldpy_source
from .validate import iter_examples

PAIRS_PATH = RESULTS_RAW / "pairs.jsonl"
PAIRS_CSV = RESULTS_SUMMARY / "pairs.csv"


def _tok_count(text: str) -> int:
    n = 0
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type in SIGNIFICANT_TOKENS and tok.string.strip():
                n += 1
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return n


def python_correspondence(source: str, preamble: str | None = None) -> dict:
    """Per-triple correspondence metrics for the rdflib side."""
    fa = analyze_source(source, preamble=preamble)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    # map (lineno, col) of triple_add ops back to Call nodes
    add_calls = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("add", "set") and node.args
                and isinstance(node.args[0], ast.Tuple)
                and len(node.args[0].elts) == 3):
            add_calls.append(node)
    op_keys = {(o.lineno, o.col) for o in fa.ops if o.category == "triple_add"}
    add_calls = [c for c in add_calls if (c.lineno, c.col_offset) in op_keys]

    scaffolding = 0
    nesting_sum = 0
    nterms = 0
    for call in add_calls:
        seg = ast.get_source_segment(source, call) or ""
        term_toks = 0
        for elt in call.args[0].elts:
            tseg = ast.get_source_segment(source, elt) or ""
            term_toks += _tok_count(tseg)
        scaffolding += max(0, _tok_count(seg) - term_toks)
        # nesting: stmt -> Call -> Tuple -> term = depth of term below stmt.
        # For an expression-statement g.add((s,p,o)): 3 edges.
        for elt in call.args[0].elts:
            nesting_sum += _node_depth(call, elt) + 1   # +1: stmt -> call
            nterms += 1

    staging = 0
    term_lines = {(o.lineno, o.col) for o in fa.ops
                  if o.category in ("term_constructor", "namespace_term")}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and \
                (node.value.lineno, node.value.col_offset) in term_lines:
            staging += 1

    triples = max(fa.triples_added, 1)
    return {
        "triple_stmt_count": len(add_calls),
        "scaffolding_tokens": scaffolding,
        "scaffolding_tokens_per_triple":
            round(scaffolding / len(add_calls), 3) if add_calls else None,
        "nesting_per_term":
            round(nesting_sum / nterms, 3) if nterms else None,
        "constructors_per_triple": round(fa.constructors / triples, 3),
        "staging_assignments": staging,
    }


def _node_depth(root: ast.AST, target: ast.AST) -> int:
    """Edges from root to target in the AST (0 if root is target)."""
    def dfs(node, depth):
        if node is target:
            return depth
        for child in ast.iter_child_nodes(node):
            r = dfs(child, depth + 1)
            if r is not None:
                return r
        return None
    return dfs(root, 0) or 0


def measure_pair(py_source: str, ldpy_source: str,
                 preamble: str | None = None) -> dict:
    """``preamble``: bindings-only source of the example's context shim
    modules, so terms imported from a shim are recognised (analysis only —
    the shim's surface counts on neither side)."""
    fa = analyze_source(py_source, preamble=preamble)
    lm = measure_ldpy_source(ldpy_source)
    # rdflib constructs remaining in the ldpy version (outside islands)
    residual = analyze_source(lm.masked_source, preamble=preamble)
    corr = python_correspondence(py_source, preamble=preamble)

    py_code_loc = fa.code_loc
    py = {
        "loc": fa.total_loc, "code_loc": py_code_loc,
        "chars": len(py_source), "tokens": fa.tokens,
        "syntax_nodes": fa.ast_nodes,
        "constructors": fa.constructors,
        "terms_constructed": fa.terms_constructed,
        "triples_added": fa.triples_added,
        "graph_ops": fa.graph_ops,
        "rdf_ops": fa.rdf_ops,
        "category_counts": fa.category_counts,
        **{f"corr_{k}": v for k, v in corr.items()},
    }
    ld = {
        "loc": lm.loc, "code_loc": lm.code_loc,
        "chars": lm.chars, "tokens": lm.tokens,
        "syntax_nodes": lm.syntax_nodes,
        "islands": lm.islands, "island_kinds": lm.island_kinds,
        "terms": lm.terms,
        "triples_expressed": lm.triples_expressed,
        "triples_semantic": lm.triples_semantic,
        "scaffolding_tokens": lm.scaffolding_tokens,
        "residual_constructors": residual.constructors,
        "residual_rdf_ops": residual.rdf_ops,
        "corr_scaffolding_tokens_per_triple":
            round(lm.scaffolding_tokens / lm.triples_expressed, 3)
            if lm.triples_expressed else None,
        "corr_nesting_per_term":
            round(lm.term_depth_sum / lm.terms, 3) if lm.terms else None,
        "corr_constructors_per_triple":
            round(residual.constructors / lm.triples_expressed, 3)
            if lm.triples_expressed else None,
    }

    def ratio(a, b):
        return round(b / a, 4) if a else None

    return {
        "python": py, "ldpy": ld,
        "ratios": {
            "loc": ratio(py["loc"], ld["loc"]),
            "code_loc": ratio(py["code_loc"], ld["code_loc"]),
            "chars": ratio(py["chars"], ld["chars"]),
            "tokens": ratio(py["tokens"], ld["tokens"]),
            "syntax_nodes": ratio(py["syntax_nodes"], ld["syntax_nodes"]),
        },
    }


def run(config: dict) -> None:
    rows = []
    skipped = []
    for ex_dir, meta in iter_examples():
        if meta.get("translation_status") != "final":
            continue
        if meta.get("classification") in ("not-expressible", "excluded"):
            skipped.append((meta["region_id"], meta.get("classification")))
            continue
        vstatus = (meta.get("validation") or {}).get("status")
        py_source = (ex_dir / "original.py").read_text()
        ldpy_source = (ex_dir / "translated.ldpy").read_text()
        shims = [p for p in sorted(ex_dir.glob("*.py"))
                 if p.name not in ("original.py", "driver.py")]
        preamble = "\n".join(p.read_text() for p in shims) or None
        try:
            pair = measure_pair(py_source, ldpy_source, preamble=preamble)
        except LdpyMetricsError as e:
            print(f"  ! {meta['region_id']}: {e}")
            skipped.append((meta["region_id"], f"metrics-error: {e}"))
            continue
        rows.append({
            "region_id": meta["region_id"],
            "repository": meta["repository"],
            "path": meta["path"],
            "band": meta["band"],
            "classification": meta.get("classification"),
            "validation_status": vstatus or "unvalidated",
            **pair,
        })
    PAIRS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PAIRS_PATH, "w") as f:
        f.write(json.dumps({"provenance": provenance(config),
                            "skipped": skipped}) + "\n")
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # flat CSV for spreadsheet/statistics use
    if rows:
        PAIRS_CSV.parent.mkdir(parents=True, exist_ok=True)
        flat_rows = []
        for r in rows:
            flat = {"region_id": r["region_id"], "repository": r["repository"],
                    "band": r["band"], "classification": r["classification"],
                    "validation_status": r["validation_status"]}
            for side in ("python", "ldpy"):
                for k, v in r[side].items():
                    if isinstance(v, (int, float, type(None))):
                        flat[f"{side}_{k}"] = v
            for k, v in r["ratios"].items():
                flat[f"ratio_{k}"] = v
            flat_rows.append(flat)
        fieldnames = sorted({k for fr in flat_rows for k in fr},
                            key=lambda k: (k != "region_id", k))
        with open(PAIRS_CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(flat_rows)
    print(f"compare: {len(rows)} pairs measured, {len(skipped)} skipped")


def load_pairs() -> list[dict]:
    if not PAIRS_PATH.exists():
        raise SystemExit("no pairs; run `rdfeval compare` first")
    rows = [json.loads(line) for line in PAIRS_PATH.read_text().splitlines()
            if line.strip()]
    return [r for r in rows if "region_id" in r]
