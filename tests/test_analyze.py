"""Tests of the AST-based RDF-usage analyser."""

from rdfeval.analyze import analyze_source


def test_no_rdf():
    a = analyze_source("x = 1\nprint(x + 2)\n")
    assert a.rdf_ops == 0
    assert not a.imports_rdflib
    assert a.rdf_node_density == 0.0
    assert a.total_loc == 2


def test_incidental_import_only():
    """An imported name that is never used is not an RDF operation."""
    a = analyze_source("from rdflib import URIRef, Literal\nx = 1\n")
    assert a.imports_rdflib
    assert a.rdf_ops == 0


def test_term_constructors_direct_and_aliased():
    src = (
        "from rdflib import URIRef, Literal as L\n"
        "import rdflib\n"
        "s = URIRef('http://ex.org/s')\n"
        "o = L('hello', lang='en')\n"
        "b = rdflib.BNode()\n"
    )
    a = analyze_source(src)
    assert a.category_counts["term_constructor"] == 3
    assert a.terms_constructed == 3
    assert a.constructors == 3


def test_shadowed_name_not_counted():
    """A local function called URIRef unrelated to rdflib is not counted."""
    src = (
        "def URIRef(x):\n"
        "    return x\n"
        "u = URIRef('http://ex.org/')\n"
    )
    a = analyze_source(src)
    assert a.rdf_ops == 0


def test_namespace_and_derived_terms():
    src = (
        "from rdflib import Namespace, Graph\n"
        "from rdflib.namespace import FOAF\n"
        "EX = Namespace('http://example.org/')\n"
        "g = Graph()\n"
        "g.add((EX.alice, FOAF.name, EX['bob']))\n"
    )
    a = analyze_source(src)
    c = a.category_counts
    assert c["namespace_ctor"] == 1
    assert c["graph_ctor"] == 1
    assert c["triple_add"] == 1
    # EX.alice, FOAF.name, EX['bob']
    assert c["namespace_term"] == 3
    assert a.triples_added == 1


def test_set_add_on_plain_set_not_counted():
    src = (
        "s = set()\n"
        "s.add((1, 2, 3))\n"
    )
    a = analyze_source(src)
    assert a.rdf_ops == 0


def test_add_with_rdf_terms_on_unknown_receiver_counted():
    """g comes from elsewhere but the tuple holds RDF terms -> counted."""
    src = (
        "from rdflib import URIRef\n"
        "def fill(g):\n"
        "    g.add((URIRef('http://a'), URIRef('http://b'), URIRef('http://c')))\n"
    )
    a = analyze_source(src)
    assert a.category_counts["triple_add"] == 1
    assert a.category_counts["term_constructor"] == 3


def test_graph_ops_on_known_graph():
    src = (
        "from rdflib import Graph\n"
        "g = Graph()\n"
        "g.parse('file.ttl')\n"
        "for s, p, o in g.triples((None, None, None)):\n"
        "    pass\n"
        "res = g.query('SELECT * WHERE { ?s ?p ?o }')\n"
        "g.serialize(destination='out.ttl')\n"
        "g.bind('ex', 'http://example.org/')\n"
    )
    a = analyze_source(src)
    c = a.category_counts
    assert c["serialize_parse"] == 2
    assert c["graph_read"] == 1
    assert c["sparql"] == 1
    assert c["graph_write"] == 1   # bind


def test_graph_through_parse_chain():
    src = (
        "import rdflib\n"
        "g = rdflib.Graph().parse('x.ttl')\n"
        "n = g.value(None, None)\n"
    )
    a = analyze_source(src)
    assert a.category_counts["graph_read"] == 1


def test_use_before_binding_flow_insensitive():
    """Flow-insensitive: NS used in a function defined before the binding."""
    src = (
        "from rdflib import Namespace\n"
        "def f():\n"
        "    return EX.thing\n"
        "EX = Namespace('http://example.org/')\n"
    )
    a = analyze_source(src)
    assert a.category_counts["namespace_term"] == 1


def test_no_double_count_nested_subtrees():
    """URIRef inside g.add: nodes counted once in rdf_ast_nodes."""
    src = (
        "from rdflib import Graph, URIRef\n"
        "g = Graph()\n"
        "g.add((URIRef('http://a'), URIRef('http://b'), URIRef('http://c')))\n"
    )
    a = analyze_source(src)
    assert a.rdf_ast_nodes <= a.ast_nodes
    # the add subtree contains the three URIRef subtrees; ensure no inflation
    add_op = next(o for o in a.ops if o.category == "triple_add")
    assert a.rdf_ast_nodes >= add_op.subtree_nodes
    assert 0.0 < a.rdf_node_density <= 1.0


def test_quad_add_and_dataset():
    src = (
        "from rdflib import Dataset, URIRef\n"
        "ds = Dataset()\n"
        "ds.add((URIRef('http://s'), URIRef('http://p'), URIRef('http://o'), URIRef('http://g')))\n"
    )
    a = analyze_source(src)
    assert a.quads_added == 1


def test_sparql_prepare():
    src = (
        "from rdflib.plugins.sparql import prepareQuery\n"
        "q = prepareQuery('SELECT ?s WHERE { ?s ?p ?o }')\n"
    )
    a = analyze_source(src)
    assert a.category_counts["sparql"] == 1


def test_defined_namespace_subclass():
    src = (
        "from rdflib.namespace import DefinedNamespace, Namespace\n"
        "class MYNS(DefinedNamespace):\n"
        "    _NS = Namespace('http://my.org/')\n"
        "    Thing: object\n"
        "x = MYNS.Thing\n"
    )
    a = analyze_source(src)
    assert a.category_counts["namespace_ctor"] >= 1
    assert a.category_counts["namespace_term"] >= 1


def test_syntax_error_reported_not_dropped():
    a = analyze_source("def broken(:\n")
    assert a.error is not None
    assert a.rdf_ops == 0


def test_metrics_sanity():
    src = (
        "from rdflib import Graph\n"
        "\n"
        "# a comment\n"
        "g = Graph()\n"
    )
    a = analyze_source(src)
    assert a.total_loc == 4
    assert a.code_loc == 2          # comment/blank lines excluded
    assert a.logical_loc == 2       # import + assign
    assert a.tokens > 0
    assert a.ast_nodes > 0


def test_self_attribute_graph_tracking():
    src = (
        "from rdflib import Graph, URIRef\n"
        "class C:\n"
        "    def __init__(self):\n"
        "        self.g = Graph()\n"
        "    def fill(self):\n"
        "        self.g.add((URIRef('http://a'), URIRef('http://b'), URIRef('http://c')))\n"
        "        self.g.serialize()\n"
    )
    a = analyze_source(src)
    assert a.category_counts["triple_add"] == 1
    assert a.category_counts["serialize_parse"] == 1
