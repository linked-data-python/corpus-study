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

Repair 2026-10-30 (triage: weak-oracle): `self` now logs every assertion
with its arguments, and 61 further calls perturb the PROV graph through
demo's `perturb` seam so that each count, each membership test, the
first-of-several reads and each path of the attribute loop is, in at
least one call, the one that decides.  See the section below CASES.
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
    # every .ldpy artefact the driver may run (RDFEVAL_SIDES swaps an
    # optimized one in for translated.ldpy), each under its own path
    for ldpy in sorted(HERE.glob("*.ldpy")):
        r = transpile(ldpy.read_text(), filename=str(ldpy))
        path = str(ldpy)
        linecache.cache[path] = (len(r.code), None,
                                  r.code.splitlines(keepends=True), path)


_prime_linecache_for_transpiled_source()


class _Case(unittest.TestCase):
    """Stand-in for OntologyAnnotationTestCase: only .ONTOLOGY (bound by
    the real class's setUpClass) and the assert* methods (inherited from
    unittest.TestCase, unmodified) are needed by the extracted method.

    Repair 2026-10-30: every assertEqual/assertTrue the region makes is
    also LOGGED with its arguments before unittest checks it, and two
    instances compare equal only if their logs hold the same calls (as a
    multiset: alpaca's own graph lists the two attributes in an order that
    depends on random blank-node labels, which may differ between the two
    sides).  The harness compares the `self` argument after each call
    (call[i].arg[0]), so the 7 counts, the 13 membership booleans and the
    (value, expected) pair of every loop iteration are all compared --
    not only "no assertion failed"."""
    ONTOLOGY = ONTOLOGY

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.log = []

    def runTest(self):
        pass

    def assertEqual(self, first, second, msg=None):
        self.log.append(("assertEqual", first, second))
        return super().assertEqual(first, second, msg)

    def assertTrue(self, expr, msg=None):
        self.log.append(("assertTrue", expr))
        return super().assertTrue(expr, msg)

    def _key(self):
        return sorted(repr(entry) for entry in self.log)

    def __eq__(self, other):
        return isinstance(other, _Case) and self._key() == other._key()

    __hash__ = None

    def __repr__(self):
        return f"_Case(log={self.log!r})"


def call_default():
    # A fresh _Case (and hence nothing shared) per invocation; alpaca's own
    # activate(clear=True)/deactivate() resets its module-level session
    # state inside the region itself.
    return ((_Case(),), {})


# ---------------------------------------------------------------------------
# Repair 2026-10-30: perturbed graphs.
#
# alpaca always produces the same graph, on which every assertion passes:
# the default call alone cannot tell a deleted island, a widened term or
# an assertion replaced by True from the original.  Through demo's
# `perturb` seam (identical on both sides), each call below edits the PROV
# graph that save_provenance() returned before the region parses it, so
# that one term of one read is the one that decides.  The edited graph is
# handed back as N-Triples (valid Turtle) in a canonical order -- blank
# nodes relabelled by role, triples sorted by role -- because rdflib's
# memory store iterates in insertion order: both sides then iterate the
# attributes and the subjects of a class in the same order, and
# "the first of several" (list(...)[0], .value()) is the same node.
#
# Roles, found in the graph alpaca produced: exec (alpaca:FunctionExecution),
# param (ontology:Parameter), output (ontology:ProcessedDataMultiple), input
# (ontology:InputObject), attr_name / attr_channel (the two
# alpaca:hasAttribute objects of output, by pairName).
# ---------------------------------------------------------------------------
from rdflib import Graph, Literal, Namespace, BNode, RDF, PROV, XSD
from alpaca.ontology import ALPACA

EX = Namespace("http://example.org/rdfeval#")      # neighbours, never in alpaca's graph
O = ONTOLOGY


def _roles(g):
    def one(cls):
        return next(iter(g.subjects(RDF.type, cls)), None)
    r = {"exec": one(ALPACA.FunctionExecution), "param": one(O.Parameter),
         "output": one(O.ProcessedDataMultiple), "input": one(O.InputObject)}
    for a in g.objects(r["output"], ALPACA.hasAttribute):
        r["attr_" + str(g.value(a, ALPACA.pairName))] = a
    assert all(r.get(k) is not None for k in
               ("exec", "param", "output", "input", "attr_name", "attr_channel")), r
    return r


def _canonical(g, roles, first=()):
    """N-Triples text: `first` triples (in that order), then the rest of g
    sorted by role; blank nodes labelled by role."""
    names = {v: k for k, v in roles.items()}
    labels = {}

    def key(t):
        return names.get(t, "~" + t.n3() if not isinstance(t, BNode) else "~_")

    def n3(t):
        if isinstance(t, BNode):
            if t not in labels:
                labels[t] = names.get(t, f"b{len(labels)}")
            return "_:" + labels[t]
        return t.n3()
    head = list(first)
    rest = sorted((t for t in g if t not in head),
                  key=lambda t: tuple(key(x) for x in t))
    return "".join(f"{n3(s)} {n3(p)} {n3(o)} .\n" for s, p, o in head + rest)


def _perturbation(edit):
    """A str -> str function for demo(perturb=...).  `edit(g, roles)` mutates
    g and may return triples to put FIRST in the text (so that they are the
    first solution of a read that takes the first of several)."""
    def perturb(text):
        g = Graph().parse(data=text, format="turtle")
        roles = _roles(g)
        first = edit(g, roles) or ()
        for t in first:
            g.add(t)
        return _canonical(g, roles, first)
    perturb.__name__ = getattr(edit, "__name__", "perturb")
    return perturb


def _case(edit):
    p = _perturbation(edit)
    return lambda: ((_Case(), p), {})


def _identity(g, r):
    """Canonicalised but unchanged: everything passes, the log is complete
    (7 counts, 13 membership tests, 2 loop iterations)."""


# -- the seven counts: an extra subject of the class changes the count; a
#    neighbour (same object, other predicate) must not.
def _extra_typed(cls):
    def edit(g, r):
        g.add((EX.extra, RDF.type, cls))
    return edit


def _neighbour_of_type(cls):
    def edit(g, r):
        g.add((EX.extra, EX.other, cls))
        g.add((EX.extra, RDF.type, EX.OtherClass))
    return edit


COUNTED = [O.Parameter, O.ProcessFunctionMultiple, O.ProcessedDataMultiple,
           O.InputObject, O.OutputObject, O.ProcessFunction, O.ProcessedData]


# -- execution_uri = list(subjects(RDF.type, FunctionExecution))[0]: no
#    execution at all (IndexError upstream), and another execution listed
#    first (which is then the one the next assertion checks).
def _no_execution(g, r):
    g.remove((r["exec"], RDF.type, ALPACA.FunctionExecution))


def _other_execution_first(g, r):
    return [(EX.otherExec, RDF.type, ALPACA.FunctionExecution)]


# -- the 13 membership tests: drop the triple, move its subject elsewhere,
#    move its object elsewhere (same predicate).  `o` is a role name or a term.
CHECKS = [
    ("exec", RDF.type, O.ProcessFunctionMultiple),
    ("param", ALPACA.pairName, Literal("param_1")),
    ("param", ALPACA.pairValue, Literal(45)),
    ("output", PROV.wasGeneratedBy, "exec"),
    ("output", RDF.type, ALPACA.DataObjectEntity),
    ("output", RDF.type, O.OutputObject),
    ("attr_name", RDF.type, O.Attribute),
    ("exec", PROV.used, "input"),
    ("input", RDF.type, ALPACA.DataObjectEntity),
    ("output", PROV.wasDerivedFrom, "input"),
]


def _check_edit(check, how):
    s_role, p, o_spec = check

    def edit(g, r):
        s = r[s_role]
        o = r[o_spec] if type(o_spec) is str else o_spec      # a role name, not a URIRef
        assert (s, p, o) in g, check
        g.remove((s, p, o))
        if how == "move-subject":
            g.add((EX.elsewhere, p, o))
        elif how == "move-object":
            g.add((s, p, EX.elsewhere))
    edit.__name__ = f"{how}:{s_role}"
    return edit


def _literal_variant(p, value):
    """param's pairName / pairValue replaced by a literal that is not the
    one the region looks for, though it prints the same."""
    def edit(g, r):
        g.remove((r["param"], p, None))
        g.add((r["param"], p, value))
    return edit


# -- the attribute loop.
def _set(attr, p, value):
    def edit(g, r):
        g.remove((r[attr], p, None))
        if value is not None:
            g.add((r[attr], p, value))
    return edit


def _drop_link(g, r):
    """Only one attribute left: one iteration."""
    g.remove((r["output"], ALPACA.hasAttribute, r["attr_channel"]))


def _third_attribute(g, r):
    """Three iterations, all passing."""
    a = BNode()
    g.add((r["output"], ALPACA.hasAttribute, a))
    g.add((a, ALPACA.pairName, Literal("channel")))
    g.add((a, ALPACA.pairValue, Literal(34)))


def _attribute_of_another_subject(g, r):
    """Neighbour: an attribute of `input`, whose name the expected dict does
    not know -- a loop that reads any subject's attributes raises KeyError."""
    a = BNode()
    g.add((r["input"], ALPACA.hasAttribute, a))
    g.add((a, ALPACA.pairName, Literal("bogus")))
    g.add((a, ALPACA.pairValue, Literal(1)))


def _second_attribute_named_name(g, r):
    """The `if name == 'name'` branch taken twice: the second attribute
    named 'name' has no ontology:Attribute type."""
    _set("attr_channel", ALPACA.pairName, Literal("name"))(g, r)
    _set("attr_channel", ALPACA.pairValue, Literal("SpikeTrain#2"))(g, r)


def _type_on_wrong_attribute(g, r):
    """ontology:Attribute moved from attr_name to attr_channel."""
    g.remove((r["attr_name"], RDF.type, O.Attribute))
    g.add((r["attr_channel"], RDF.type, O.Attribute))


def _second_pair_name(g, r):
    """Two pairNames on one attribute: .value() and .first() both take the
    first one inserted (the canonical text lists alpaca's first)."""
    g.add((r["attr_channel"], ALPACA.pairName, Literal("zzz")))


CASES = (
    [_case(_identity)]
    + [_case(_extra_typed(c)) for c in COUNTED]
    + [_case(_neighbour_of_type(c)) for c in COUNTED]
    + [_case(_no_execution), _case(_other_execution_first)]
    + [_case(_check_edit(c, how)) for c in CHECKS
       for how in ("drop", "move-subject", "move-object")]
    + [_case(_literal_variant(ALPACA.pairName,
                              Literal("param_1", datatype=XSD.string))),
       _case(_literal_variant(ALPACA.pairValue, Literal("45"))),
       _case(_literal_variant(ALPACA.pairValue, Literal(45.0)))]
    + [_case(_set("attr_channel", ALPACA.pairValue, Literal(35))),
       _case(_set("attr_channel", ALPACA.pairName, Literal("bogus"))),
       _case(_set("attr_channel", ALPACA.pairName, None)),
       _case(_set("attr_channel", ALPACA.pairValue, None)),
       _case(_drop_link), _case(_third_attribute),
       _case(_attribute_of_another_subject),
       _case(_second_attribute_named_name),
       _case(_type_on_wrong_attribute),
       _case(_second_pair_name)]
)


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[call_default] + CASES,
)
