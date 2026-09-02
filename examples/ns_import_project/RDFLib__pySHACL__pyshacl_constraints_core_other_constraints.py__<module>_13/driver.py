"""Validation driver for RDFLib__pySHACL__pyshacl_constraints_core_other_constraints.py__<module>_13.

The region is a single import statement: nothing is *used* inside it, so
the generic module-state comparison in ``run_pair`` (entry=None) is nearly
blind here. Worse: ``rdfs:`` and ``sh:`` are PREFIXES, not Python names --
importing a prefix captures no name in ``translated.ldpy``'s globals, so
the generic comparison (which only pairs values under a SHARED variable
name) never even looks at them. It only ends up comparing ``RDF_type`` and
``SH_property``, which travel as ordinary names on both sides. A completely
wrong IRI behind ``rdfs:`` or ``sh:`` would still report "equivalent".

So this driver adds an explicit check of the module-level ``__namespaces__``
table that every ldpy module exports (see ldpy/transpiler/core.py, PRELUDE
and the import-island codegen): it must bind ``rdfs`` and ``sh`` to the same
namespace IRIs as the real ``RDFS``/``SH`` objects the original module
imports.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

from rdfeval.harness import _exec_ldpy, run_pair

# run_pair() prints its own RDFEVAL-VERDICT line to stderr as a side effect;
# rdfeval.check takes the FIRST such line, so it has to be silenced here and
# re-emitted once, after the extra prefix check below has had a chance to
# turn a false "equivalent" into a real failure.
_buf = io.StringIO()
with contextlib.redirect_stderr(_buf):
    VERDICT = run_pair(
        __file__,
        entry=None,
        calls=None,
    )

if VERDICT["equivalent"]:
    from pyshacl_consts_context import RDFS, SH

    ns_t, _ = _exec_ldpy(Path(__file__).resolve().parent / "translated.ldpy")
    namespaces = ns_t.get("__namespaces__", {})
    expected = {"rdfs": RDFS, "sh": SH}
    diffs = []
    for prefix, want in expected.items():
        got = namespaces.get(prefix)
        if got is None or str(got) != str(want):
            diffs.append(f"prefix {prefix}: expected {want!r}, got {got!r}")
    if diffs:
        VERDICT["equivalent"] = False
        VERDICT["diffs"] = VERDICT.get("diffs", []) + diffs

print("RDFEVAL-VERDICT " + json.dumps(VERDICT), file=sys.stderr)
