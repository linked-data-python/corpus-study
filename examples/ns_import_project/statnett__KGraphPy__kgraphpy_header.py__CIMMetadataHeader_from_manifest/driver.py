"""Validation driver for
statnett__KGraphPy__kgraphpy_header.py__CIMMetadataHeader_from_manifest.

Not the generic ``run_pair(entry=..., calls=[...])`` shape: one of the two
cases the fixture is required to cover -- the zero-solution graph identifier
-- makes ``from_manifest`` *raise* ``ValueError``, and ``run_pair``'s call
loop treats any exception as a driver bug (it aborts the whole verdict with
a traceback) rather than as a per-case outcome to compare. So this driver
calls the entry point itself, on both sides, and records "returned X" or
"raised Y" the way the edmondchuc__rdflib-orm driver in this same stratum
does for its five pytest functions.

Equality of the two ``CIMMetadataHeader`` instances the matching case
returns is judged by ``__eq__`` on the shim class in original.py/
translated.ldpy (subject equality plus set-equality of the header graph's
triples) -- both sides define that method identically, so it adds no
asymmetric behaviour, only comparability for a plain object the generic
harness would otherwise compare by identity.

Repair audit (2026-10-31) -- what each added call exercises, and why:

* The outcome of a raising call is compared by exception type AND message
  (the message names the graph identifier the region computed).
* The header graph's prefix bindings are compared, not only its triples:
  the second half of the region (``NamespaceManager(..., "none")``, the
  ``nm.bind`` loop, ``header_graph.namespace_manager = nm``) decides nothing
  else, and the repository's own tests assert on exactly those bindings
  (tests/test_header.py:612-614, 630-637).  Before this, deleting the
  ``nm.bind`` loop or the ``namespace_manager`` assignment stayed green.
* ``fixture.trig``, read in the region's DEFAULT format (no ``format=``
  argument, as main.py:65 calls it): headers in the default graph, model data
  in named graphs whose triples ALSO have the header subject in subject
  position.  A plain ``Graph`` sees only the default graph; a reading that
  went through the store or a union would copy the named-graph triples.  The
  identifier is passed as a ``str`` and as a ``URIRef`` (the repository's
  tests pass both); a third identifier is absent.
* The parametrised cases of tests/test_header.py:489-586 and
  test_from_manifest_namespaces (617-637), with the repository's own seam:
  ``Graph.parse`` replaced by ``fake_parse_factory`` (tests/fixtures.py:117),
  identically for both sides -- relative identifiers (``graph1``,
  ``graph1#section``), a literal and a blank node in subject position that
  must NOT match, and a manifest whose bound prefixes are only partly used.
"""
from pathlib import Path
from unittest.mock import patch

from rdflib import BNode, Graph, Literal, Namespace, URIRef

from rdfeval.harness import _exec_ldpy, _exec_python, _emit

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
TRIG = Path(__file__).resolve().parent / "fixture.trig"
EX = "http://example.org/"


def _outcome(thunk):
    try:
        return ("ok", thunk(), None)
    except Exception as e:  # noqa: BLE001 - the outcome IS the datum
        return ("raised", None, f"{type(e).__name__}: {e}")


def call(fn, graph_uri):
    return _outcome(lambda: fn(str(FIXTURE), graph_uri, "turtle"))


def call_trig(fn, graph_uri):
    """The default format, no ``format=`` argument."""
    return _outcome(lambda: fn(str(TRIG), graph_uri))


def _make_graph(triples):
    """tests/fixtures.py:71-79, make_graph."""
    g = Graph()
    g.bind("ex", Namespace("http://example.org/"))
    for t in triples:
        g.add(t)
    return g


def _namespaces_graph():
    """tests/test_header.py:618-624, test_from_manifest_namespaces."""
    g = Graph()
    g.bind("ex", "https://example.org/")
    g.bind("foo", "www.bar.com/")
    g.bind("exa", "www.extra.com/")
    g.add((URIRef("graph1"), URIRef("https://example.org/p1"), Literal("o1")))
    g.add((URIRef("graph1"), URIRef("www.bar.com/p2"), Literal("o2")))
    g.add((URIRef("graph2"), URIRef("www.extra.com/p3"), Literal("o3")))
    return g


def call_faked(fn, make_manifest, subject):
    """tests/fixtures.py:117-126: parse copies a prepared graph."""
    source = make_manifest()

    def fake_parse(self, *args, **kwargs):
        self.namespace_manager = source.namespace_manager
        for triple in source:
            self.add(triple)
        return self

    with patch.object(Graph, "parse", fake_parse):
        return _outcome(lambda: fn("dummy.trig", subject))


P = URIRef(EX + "p")
FAKED = {
    "uriref-subject": (lambda: _make_graph([
        (URIRef("graph1"), P, Literal("o")),
        (URIRef("graph2"), P, Literal("x"))]), URIRef("graph1")),
    "str-subject": (lambda: _make_graph([
        (URIRef("graph1"), P, Literal("o")),
        (URIRef("graph2"), P, Literal("x"))]), "graph1"),
    "fragment-subject": (lambda: _make_graph([
        (URIRef("graph1#section"), P, Literal("o")),
        (URIRef("graph1"), P, Literal("x"))]), URIRef("graph1#section")),
    "not-found": (lambda: _make_graph([
        (URIRef("graph1"), P, Literal("o")),
        (URIRef("graph2"), P, Literal("x"))]), URIRef("graph3")),
    "several-triples": (lambda: _make_graph([
        (URIRef("graph1"), URIRef(EX + "p1"), Literal("o1")),
        (URIRef("graph1"), URIRef(EX + "p2"), Literal("o2")),
        (URIRef("graph2"), URIRef(EX + "p3"), Literal("o3"))]), URIRef("graph1")),
    "literal-subject": (lambda: _make_graph([
        (Literal("weird"), P, Literal("o"))]), Literal("weird")),
    "bnode-subject": (lambda: _make_graph([
        (BNode("b1"), P, Literal("o")),
        (URIRef("graph1"), P, Literal("x"))]), BNode("b1")),
    "str-vs-bnode": (lambda: _make_graph([
        (BNode("b1"), P, Literal("o")),
        (URIRef("graph1"), P, Literal("x"))]), "b1"),
    "mixed-terms": (lambda: _make_graph([
        (BNode("graph1"), P, Literal("o")),
        (URIRef("graph1"), P, Literal("x")),
        (Literal("graph1"), P, Literal("y"))]), "graph1"),
    "namespaces": (_namespaces_graph, "graph1"),
}


def _bindings(header):
    return sorted((p, str(n)) for p, n in header.graph.namespaces())


def compare(name, left, right, diffs):
    so, ro, eo = left
    st, rt, et = right
    if (so, eo) != (st, et):
        diffs.append(f"{name}: outcome differs "
                     f"(original {so}/{eo} vs translated {st}/{et})")
    elif so == "ok":
        if ro != rt:
            diffs.append(f"{name}: result differs "
                         f"(subject {ro.subject!r} vs {rt.subject!r}, "
                         f"{len(ro.graph)} vs {len(rt.graph)} triples)")
        if _bindings(ro) != _bindings(rt):
            diffs.append(f"{name}: header bindings differ "
                         f"({_bindings(ro)} vs {_bindings(rt)})")


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:from_manifest-outcomes", "diffs": [],
                     "error": None}
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        import traceback
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    fo, ft = ns_o["from_manifest"], ns_t["from_manifest"]

    cases = {
        "matching": "urn:uuid:graph-1",
        "zero-solution": "urn:uuid:no-such-graph",
    }
    for name, graph_uri in cases.items():
        compare(name, call(fo, graph_uri), call(ft, graph_uri), diffs)

    trig_cases = {
        "trig-str": "urn:uuid:graph-1",
        "trig-uriref": URIRef("urn:uuid:graph-2"),
        "trig-absent": "urn:uuid:graph-3",
    }
    for name, graph_uri in trig_cases.items():
        compare(name, call_trig(fo, graph_uri), call_trig(ft, graph_uri), diffs)

    for name, (make, subject) in FAKED.items():
        compare(name, call_faked(fo, make, subject),
                call_faked(ft, make, subject), diffs)

    if out_o != out_t:
        diffs.append("stdout differs at module definition time")

    verdict["cases"] = list(cases) + list(trig_cases) + list(FAKED)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()

if __name__ == "__main__":
    import sys
    sys.exit(0 if VERDICT["equivalent"] else 1)
