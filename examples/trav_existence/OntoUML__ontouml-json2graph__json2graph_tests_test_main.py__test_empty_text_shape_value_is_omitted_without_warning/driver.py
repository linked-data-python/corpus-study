"""Validation driver for OntoUML__ontouml-json2graph__json2graph_tests_test_main.py__test_empty_text_shape_value_is_omitted_without_warning.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). The graph is not passed in directly, though: the region builds
it itself by calling the package's own JSON->RDF decoder
(`write_text_shape_project` + `decode_ontouml_json2graph`, stubbed in
context_shim.py -- see meta.json). The driver controls what that stub
produces by dropping a `_fixture_name` marker file into the tmp_path it hands
the region beforehand, naming which of the Turtle fixtures alongside this
file to copy in as `ontouml_graph`.

Two observations per fixture, both compared side by side:

1. `demo(tmp_path)`, the harness both files carry identically (see
   meta.json): "ok", or ("assertion-failed", str(e)). This was the whole
   oracle before the 2026-10-30 repair.
2. WHICH assertion of the region fails, as its ordinal (1, 2 or 3) among
   the `assert` statements of the region function. `demo` cannot say it:
   the three asserts carry no message, so str(e) is '' for each of them.
   Without this, swapping ontouml:text and ontouml:value between the second
   and third assertions stayed green -- the overall pass/fail is symmetric
   in the two predicates, only the failing assertion tells them apart. The
   ordinal is read from the traceback: the line where the region function
   raised, located among the `assert` nodes of the code that side actually
   executed (original.py as is, the .ldpy through the transpiler, whose
   line numbers differ from the source file's).

The fixtures, one per outcome:
  * fixture_clean                all three pass -> "ok"; view-2_shape
                                 carries text and value (another subject
                                 must not match);
  * fixture_missing_type         assertion 1 fails; view-1_shape has
                                 another rdf:type and ontouml:Text under
                                 another predicate (a widened object or
                                 predicate would match them);
  * fixture_leftover_text        assertion 2 fails;
  * fixture_leftover_value       assertion 3 fails;
  * fixture_leftover_empty_value assertion 3 fails on an EMPTY literal --
                                 the very bug the upstream test guards
                                 against; presence, not truthiness.

This driver executes both sides by hand (like the add_isolated drivers that
bypass run_pair's call loop) because run_pair can only compare what `demo`
returns, and `demo` is scaffolding identical on both sides, not edited here.
"""
from __future__ import annotations

import ast
import sys
import tempfile
import traceback
from pathlib import Path

from rdfeval.harness import _emit, _exec_ldpy, _exec_python

HERE = Path(__file__).resolve().parent
REGION = "test_empty_text_shape_value_is_omitted_without_warning"

FIXTURES = [
    "fixture_clean.ttl",
    "fixture_missing_type.ttl",
    "fixture_leftover_text.ttl",
    "fixture_leftover_value.ttl",
    "fixture_leftover_empty_value.ttl",
]


def _executed_code(ns: dict) -> str:
    """The Python text that side actually ran (the .ldpy transpiled)."""
    path = Path(ns["__file__"])
    if path.suffix == ".ldpy":
        from ldpy.transpiler import transpile
        return transpile(path.read_text(), filename=str(path)).code
    return path.read_text()


def _assert_spans(code: str) -> list[tuple[int, int]]:
    """(first, last) line of each `assert` in the region function, in order."""
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.FunctionDef) and node.name == REGION:
            return [(a.lineno, a.end_lineno) for a in ast.walk(node)
                    if isinstance(a, ast.Assert)]
    raise RuntimeError(f"{REGION} not found in executed code")


def _which_assert(ns: dict, tmp_path: Path) -> object:
    """'ok', or the ordinal of the region's assertion that failed."""
    spans = _assert_spans(_executed_code(ns))
    try:
        ns[REGION](tmp_path)
        return "ok"
    except AssertionError:
        tb = sys.exc_info()[2]
        line = None
        while tb is not None:
            if tb.tb_frame.f_code.co_name == REGION:
                line = tb.tb_lineno
            tb = tb.tb_next
        for i, (first, last) in enumerate(spans, 1):
            if line is not None and first <= line <= last:
                return ("assertion-failed", i)
        return ("assertion-failed", f"line {line}, not an assert")


def _tmp(fixture_name: str) -> Path:
    tmp_path = Path(tempfile.mkdtemp())
    (tmp_path / "_fixture_name").write_text(fixture_name, encoding="utf-8")
    return tmp_path


verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:demo + failing-assertion ordinal",
           "diffs": [], "error": None}

try:
    ns_o, _ = _exec_python(HERE / "original.py")
    ns_t, _ = _exec_ldpy(HERE / "translated.ldpy")
    for ns in (ns_o, ns_t):
        if not callable(ns.get("demo")) or not callable(ns.get(REGION)):
            raise RuntimeError("entry points not found in both modules")

    diffs: list[str] = []
    for i, name in enumerate(FIXTURES):
        tmp_path = _tmp(name)            # one per case, shared: same marker
        do, dt = ns_o["demo"](tmp_path), ns_t["demo"](tmp_path)
        if do != dt:
            diffs.append(f"case[{i}] {name}: demo differs ({do!r} vs {dt!r})")
        wo, wt = _which_assert(ns_o, tmp_path), _which_assert(ns_t, tmp_path)
        if wo != wt:
            diffs.append(f"case[{i}] {name}: failing assertion differs "
                         f"({wo!r} vs {wt!r})")
        verdict.setdefault("observed", []).append([name, wo])
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
