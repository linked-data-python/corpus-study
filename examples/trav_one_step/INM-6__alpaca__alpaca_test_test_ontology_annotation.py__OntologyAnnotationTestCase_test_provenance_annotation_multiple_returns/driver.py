"""Validation driver for INM-6__alpaca__alpaca_test_test_ontology_annotation.py__OntologyAnnotationTestCase_test_provenance_annotation_multiple_returns.

This region READS a graph, so the oracle is not isomorphism but the
equality of the values both versions produce from the same input graph
(design record corpus/405). But the graph here is not external input: the
region runs `alpaca`'s real Provenance tracking over a call it makes itself
(`process_multiple(input_object, 45)`, decorated with `@Provenance` in the
context shim `alpaca_context.py`) and reads back the PROV graph that
produces. There is nothing for a `fixture.ttl` to supply.

`entry` is the `demo` harness added identically to both original.py and
translated.ldpy (see meta.json): the region is a unittest.TestCase method
that only ever asserts, so `demo` turns a failed assertion into a
comparable "ok" / ("assertion-failed", msg) value instead of letting an
AssertionError abort the driver. `demo(self)` needs a `self` with both
`.ONTOLOGY` (bound in OntologyAnnotationTestCase.setUpClass upstream) and
the assert* methods the region calls (self.assertEqual, self.assertTrue) --
supplied here as a minimal real unittest.TestCase instance, one fresh
instance per side per call so alpaca's activate()/deactivate() session
state (verified safe to invoke twice in the same process, see meta.json)
never leaks between the two sides.

Originally marked EXCLUDED (translation_status: draft) because `alpaca` was
not installed in this venv. Corrected: `alpaca-prov` IS published on PyPI
(`pip index versions alpaca-prov` -> 0.2.0, 0.1.0 -- the "present but
uninstalled" case, not "inexistent"), installed into ~/.venvs/ldpy, and the
region genuinely executes end to end -- this is not a stand-in fixture, it
is alpaca's own real call-stack introspection producing a real PROV graph,
verified against the upstream source (INM-6/alpaca@2b8dd34fc6, see
alpaca_context.py) before relying on it.

Installing alpaca surfaced a second, more interesting obstacle, fixed by
`_prime_linecache_for_transpiled_source` below: alpaca's own frame
introspection chokes on the untranspiled .ldpy text it finds on disk. See
that function's docstring, and meta.json, for the full account -- this is
a genuine finding about running third-party source-introspecting code from
a transpiled file, not a gap in what `m{ }`/`.first()`/`.count()`/`bool()`
can express.
"""
import linecache
import unittest
from pathlib import Path

from rdfeval.harness import run_pair
from alpaca_context import ONTOLOGY

HERE = Path(__file__).resolve().parent
TRANSLATED = HERE / "translated.ldpy"


def _prime_linecache_for_transpiled_source() -> None:
    """alpaca's @Provenance decorator introspects the CALLING frame's
    source (inspect.getsourcelines -> linecache) to build a _SourceCode
    (used e.g. for the alpaca:codeStatement triple) -- see
    alpaca/code_analysis/source_code.py. The frame that calls activate()
    from translated.ldpy has co_filename == str(TRANSLATED): the harness
    compiles the TRANSPILED Python but tags the code object with the
    original .ldpy path (rdfeval/harness.py:_exec_ldpy), which it must,
    since that IS the region's file. A naive linecache read therefore
    finds the raw .ldpy text on disk (`@graph prov_graph`, `m{ }`, ...) --
    not valid Python -- and alpaca's own `ast.parse()` on it raises
    SyntaxError, with no rdflib triple mismatch involved at all.

    This primes linecache with the actual transpiled Python text instead,
    exactly as `_exec_ldpy` compiled it -- the standard technique tools
    like doctest/IPython use to make `inspect` see the source of
    dynamically compiled code. It changes nothing about what runs (the
    module was already compiled from this same transpiled text); it only
    lets a third-party library's frame introspection see it too.
    """
    from ldpy.transpiler import transpile
    r = transpile(TRANSLATED.read_text(), filename=str(TRANSLATED))
    path = str(TRANSLATED)
    linecache.cache[path] = (len(r.code), None,
                              r.code.splitlines(keepends=True), path)


_prime_linecache_for_transpiled_source()


class _Case(unittest.TestCase):
    """Stand-in for OntologyAnnotationTestCase: only .ONTOLOGY (bound by
    the real class's setUpClass) and the assert* methods (inherited from
    unittest.TestCase, unmodified) are needed by the extracted method."""
    ONTOLOGY = ONTOLOGY

    def runTest(self):
        pass


def call_default():
    # A fresh _Case (and hence nothing shared) per invocation; alpaca's own
    # activate(clear=True)/deactivate() resets its module-level session
    # state inside the region itself.
    return ((_Case(),), {})


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[call_default],
)
