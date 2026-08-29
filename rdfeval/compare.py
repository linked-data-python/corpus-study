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
import re
import tokenize

from .analyze import SIGNIFICANT_TOKENS, analyze_source
from .config import RESULTS_RAW, RESULTS_SUMMARY, provenance
from .ldpy_metrics import LdpyMetricsError, measure_ldpy_source
from .constructions import normalise as normalise_constructions
from .study import Study, STUDY
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


# rdflib operations that express a triple PATTERN rather than assert a
# triple: every selector call, and `remove` with a triple argument.  They are
# the Python counterpart of `-{ }` and `m{ }`, and the denominator a reading
# or removing region has instead of "per triple".
_PATTERN_DETAILS = {
    "remove", "triples", "quads", "subjects", "objects", "predicates",
    "subject_objects", "subject_predicates", "predicate_objects", "value",
    "items", "transitive_objects", "transitive_subjects", "triples_choices",
}


def _python_patterns(fa) -> int:
    return sum(1 for op in fa.ops
               if op.category in ("graph_read", "graph_write")
               and op.detail in _PATTERN_DETAILS)


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


RDF_IN_STRING = re.compile(
    r"@prefix\s|\bPREFIX\s|^\s*<[^>\s]+>\s|\ba\s+\w+:|\w+:\w+\s+\w+:", re.M)


def string_embedded_rdf(source: str) -> dict:
    """RDF written as text inside Python string literals.

    ``g.parse(data="…turtle…")`` hides a whole RDF document from Python's
    tokenizer, which sees ONE token.  Translating it to a ``g{ … }`` island
    makes the same RDF visible (and syntax-checked) but multiplies the token
    count, so surface-size comparisons are not meaningful for those pairs
    unless they are analysed separately.  This function reports how much
    such text a source contains.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"literals": 0, "chars": 0, "lines": 0}
    literals, chars, lines = 0, 0, 0
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        text = node.value
        if len(text) < 20 or not RDF_IN_STRING.search(text):
            continue
        literals += 1
        chars += len(text)
        lines += text.count("\n") + 1
    return {"literals": literals, "chars": chars, "lines": lines}


def subgroup_of(py: dict, ld: dict) -> str:
    """Where the RDF of a region lives, in the *original* source.

    inline-construction  triples are built with RDFLib calls in the source
    string-embedded      RDF is written as text inside a Python string
    no-source-rdf        the source contains no RDF structure at all
                         (mappings/queries in external files, graph
                         plumbing, I/O) — the notation cannot apply
    """
    if py["triples_added"] > 0:
        return "inline-construction"
    if py.get("string_rdf_literals", 0) > 0:
        return "string-embedded"
    if py["terms_constructed"] > 0:
        return "terms-only"
    return "no-source-rdf"


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
        "patterns_read": _python_patterns(fa),
        "graph_ops": fa.graph_ops,
        "rdf_ops": fa.rdf_ops,
        "category_counts": fa.category_counts,
        **{f"string_rdf_{k}": v for k, v in string_embedded_rdf(py_source).items()},
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
        "patterns_expressed": lm.patterns_expressed,
        "patterns_semantic": lm.patterns_semantic,
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
        # A region that only READS or REMOVES asserts no triple, so every
        # per-triple ratio above is undefined for it.  Patterns are its unit.
        "corr_scaffolding_tokens_per_pattern":
            round(lm.scaffolding_tokens / lm.patterns_expressed, 3)
            if lm.patterns_expressed else None,
    }

    def ratio(a, b):
        return round(b / a, 4) if a else None

    return {
        "python": py, "ldpy": ld,
        "subgroup": subgroup_of(py, ld),
        "ratios": {
            "loc": ratio(py["loc"], ld["loc"]),
            "code_loc": ratio(py["code_loc"], ld["code_loc"]),
            "chars": ratio(py["chars"], ld["chars"]),
            "tokens": ratio(py["tokens"], ld["tokens"]),
            "syntax_nodes": ratio(py["syntax_nodes"], ld["syntax_nodes"]),
        },
    }


def run(config: dict, study: Study = STUDY) -> None:
    rows = []
    skipped = []
    for ex_dir, meta in iter_examples(study):
        if meta.get("translation_status") != "final":
            continue
        if meta.get("classification") in ("not-expressible", "excluded"):
            skipped.append((meta["region_id"], meta.get("classification")))
            continue
        vstatus = (meta.get("validation") or {}).get("status")
        constructions, unknown = normalise_constructions(
            meta.get("constructions", []))
        if unknown:
            print(f"  ? {meta['region_id']}: construction(s) outside the "
                  f"vocabulary: {unknown}")
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
            study.group: meta[study.group],
            "strata": meta.get("strata", []),
            "constructions": constructions,
            "constructions_unknown": unknown,
            "oracle": meta.get("oracle", "isomorphism"),
            "review_status": _review_status(ex_dir),
            "classification": meta.get("classification"),
            "validation_status": vstatus or "unvalidated",
            **pair,
        })
    pairs_path = study.path(PAIRS_PATH)
    pairs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pairs_path, "w") as f:
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
                    study.group: r[study.group],
                    "strata": " ".join(r.get("strata", [])),
                    "constructions": " ".join(r.get("constructions", [])),
                    "oracle": r.get("oracle"),
                    "review_status": r.get("review_status"),
                    "classification": r["classification"],
                    "subgroup": r.get("subgroup"),
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
        with open(study.path(PAIRS_CSV), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(flat_rows)
    print(f"compare: {len(rows)} pairs measured, {len(skipped)} skipped")


def _review_status(ex_dir) -> str:
    """The human verdict recorded beside the pair."""
    review = ex_dir / "review.json"
    if not review.exists():
        return "not-applicable"
    try:
        return json.loads(review.read_text()).get("review_status", "unreviewed")
    except (OSError, json.JSONDecodeError):
        return "unreadable"


def load_pairs(study: Study = STUDY) -> list[dict]:
    path = study.path(PAIRS_PATH)
    if not path.exists():
        raise SystemExit(f"no pairs; run `rdfeval compare --study {study.name}` first")
    rows = [json.loads(line) for line in path.read_text().splitlines()
            if line.strip()]
    return [r for r in rows if "region_id" in r]
