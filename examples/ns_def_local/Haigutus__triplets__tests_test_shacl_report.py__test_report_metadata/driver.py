"""Validation driver for Haigutus__triplets__tests_test_shacl_report.py__test_report_metadata.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a test with no parameters: it reads the report graph that the
repository's real ``violations_to_report_graph`` builds from the module
constant ``VIOLATIONS``.  The ``run_pair`` call below (kept as is) runs it
on that constant.  But that graph holds exactly ONE node with
``dcterms:creator``, ``dcterms:source``, ``dcterms:references`` and
``prov:generatedAtTime`` -- the report -- so a read whose subject is
widened (``[] dcterms:source ?v`` for ``{report} dcterms:source ?v``) or
whose class is widened (``?s a []``) gives the same values: nothing in it
can tell a read of THE report from a read of any node.

The repository has a second shape for that input: ``validate()`` stamps
``violations.attrs["validation"]`` (triplets/validation/__init__.py,
``_report_metadata``), and ``violations_to_report_graph`` copies every
``source_shapes`` graph -- the CBD of each violated shape -- into the
report graph BEFORE the report node (shacl_report.py:199-206).  So the
driver re-executes each side with one context line changed: ``VIOLATIONS``
is replaced, in that side's module globals, by a copy carrying such
attrs, built fresh per side.  Two variants:

  * A -- the CBD of ``http://example.org/shapes#NameShape`` (the
    SOURCE_SHAPE of the second row): a typed ``sh:NodeShape`` with a
    property shape.  A typed node ahead of the report: ``?s a []`` reads
    the shape instead of the report.
  * B -- the same shape annotated with ``dcterms:source``,
    ``dcterms:creator``, ``dcterms:references`` and
    ``prov:generatedAtTime`` (shape-file provenance): a neighbour sharing
    predicate and object position with each of the four reads, ahead of
    the report.  A widened subject reads the shape's values too.

``generated_at`` is fixed in the attrs (the repository takes it from there
before the wall clock).  The outcome of each call -- the four values, or
the exception type and message -- is compared, and the diffs are merged
into the single verdict ``run_pair`` emits.
"""
from rdfeval import harness
from rdfeval.harness import run_pair

_SHAPE = "http://example.org/shapes#NameShape"
_SH = "http://www.w3.org/ns/shacl#"
_CIM = "http://iec.ch/TC57/CIM100#"


def _shape_cbd(annotated):
    import rdflib
    g = rdflib.Graph()
    shape, prop = rdflib.URIRef(_SHAPE), rdflib.BNode("nameProperty")
    g.add((shape, rdflib.RDF.type, rdflib.URIRef(_SH + "NodeShape")))
    g.add((shape, rdflib.URIRef(_SH + "targetClass"),
           rdflib.URIRef(_CIM + "IdentifiedObject")))
    g.add((shape, rdflib.URIRef(_SH + "property"), prop))
    g.add((prop, rdflib.URIRef(_SH + "path"),
           rdflib.URIRef(_CIM + "IdentifiedObject.name")))
    g.add((prop, rdflib.URIRef(_SH + "minCount"), rdflib.Literal(1)))
    if annotated:
        dct = rdflib.Namespace("http://purl.org/dc/terms/")
        prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
        g.add((shape, dct.source, rdflib.Literal("shapes.ttl")))
        g.add((shape, dct.creator, rdflib.Literal("ENTSO-E")))
        g.add((shape, dct.references, rdflib.Literal("QoCDC.ttl")))
        g.add((shape, prov.generatedAtTime, rdflib.Literal(
            "2024-01-01T00:00:00Z",
            datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))))
    return g


def _with_attrs(violations, annotated):
    frame = violations.copy()
    frame.attrs = {"validation": {
        "generated_at": "2026-01-01T00:00:00Z",
        "source_shapes": {_SHAPE: _shape_cbd(annotated)},
    }}
    return frame


VARIANTS = [("A shape CBD", False), ("B annotated shape CBD", True)]


def _variant_runs():
    here = harness.Path(__file__).resolve().parent
    diffs = []
    for label, annotated in VARIANTS:
        outcomes = []
        for exec_side, name in ((harness._exec_python, "original.py"),
                                (harness._exec_ldpy, "translated.ldpy")):
            ns, _ = exec_side(here / name)
            ns["VIOLATIONS"] = _with_attrs(ns["VIOLATIONS"], annotated)
            outcomes.append(harness._outcome(ns["test_report_metadata"], (), {}))
        oo, ot = outcomes
        if isinstance(oo, harness.Raised) or isinstance(ot, harness.Raised):
            if oo != ot:
                diffs.append(f"variant {label}: outcome differs ({oo!r} vs {ot!r})")
        else:
            harness._compare_value(oo, ot, f"variant {label}: result", diffs)
    return diffs


_EXTRA = _variant_runs()
_emit = harness._emit


def _emit_with_variants(verdict):
    verdict["diffs"] = list(verdict.get("diffs") or []) + _EXTRA
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not _EXTRA
    _emit(verdict)


harness._emit = _emit_with_variants

VERDICT = run_pair(
    __file__,
    entry='test_report_metadata',
    calls=[((), {})],
)
