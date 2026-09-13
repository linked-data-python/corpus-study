"""Validation driver for binary-array-ld__bald__nc2rdf_nc2rdf.py__baldgraph2schemaorg.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair


def _input_graph():
    """A fresh bald:Container graph, matching the SPARQL pattern the region
    queries (?c a bald:Container ; ?c ?pred ?value), with values covering
    the mapping table (bald2schemaorg_mappings.json): a plain field, a
    'keywords' field with several comma-separated entries (including one
    that is blank, to exercise the skip), and an unmapped predicate that
    must NOT produce any output triple.
    """
    from rdflib import Graph, Literal, Namespace, RDF, URIRef

    BALD = Namespace("http://binary-array-ld.net/latest/")
    NC = Namespace("http://example.org/nc/")
    g = Graph()
    c = URIRef("http://example.org/dataset/1")
    g.add((c, RDF.type, BALD.Container))
    g.add((c, NC.summary, Literal("A test dataset")))
    g.add((c, NC.keywords, Literal("alpha, beta, , gamma")))
    # Unmapped predicate: must not appear at all in the schema.org graph.
    g.add((c, NC.unmapped_field, Literal("ignored")))
    return g


VERDICT = run_pair(
    __file__,
    entry='baldgraph2schemaorg',
    calls=[lambda: ((_input_graph(),), {})],
)
