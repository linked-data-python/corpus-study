"""Tests of the design-oriented surface analysis.

Each test pins one shape the language-design decision depends on: if a counter
moves, a claim in corpus/402 moves with it.
"""

from rdfeval.surface import _query_shape, surface_source

PREAMBLE = (
    "from rdflib import Graph, Namespace, URIRef, Literal, RDF\n"
    "EX = Namespace('http://example.org/')\n"
    "g = Graph()\n"
)


# --- Q1: namespaces --------------------------------------------------------

def test_namespace_definition_module_level():
    s = surface_source(PREAMBLE)
    assert s.counts["ns_def_total"] == 1
    assert s.counts["ns_def_module"] == 1
    assert s.ns_defined == {"EX": "http://example.org/"}


def test_namespace_definition_inside_function_is_local():
    src = (
        "from rdflib import Namespace\n"
        "def f():\n"
        "    EX = Namespace('http://example.org/')\n"
        "    return EX.thing\n"
    )
    s = surface_source(src)
    assert s.counts["ns_def_local"] == 1
    assert s.counts.get("ns_def_module", 0) == 0


def test_namespace_imported_from_project_module():
    """`from .vocab import EX` where EX is then used as a namespace."""
    src = (
        "from .vocab import EX\n"
        "from rdflib import Namespace\n"
        "EX = Namespace('http://example.org/')\n"   # seeds the binding
        "x = EX.thing\n"
    )
    s = surface_source(src)
    assert s.counts["ns_imported_from_project"] == 1
    assert s.counts["ns_imported_relative"] == 1
    assert "EX" in s.ns_project_imports


def test_namespace_uses_are_counted_per_object():
    src = PREAMBLE + "a = EX.one\nb = EX.two\nc = RDF.type\n"
    s = surface_source(src)
    assert s.ns_uses["EX"] == 2
    assert s.ns_uses["RDF"] == 1


def test_defined_namespace_subclass():
    src = (
        "from rdflib.namespace import DefinedNamespace\n"
        "class SOSA(DefinedNamespace):\n"
        "    pass\n"
    )
    s = surface_source(src)
    assert s.counts["ns_def_class"] == 1


# --- Q2/Q4: SPARQL and bindings -------------------------------------------

def test_query_literal_is_classified_and_measured():
    src = PREAMBLE + (
        "rows = g.query('''\n"
        "PREFIX ex: <http://example.org/>\n"
        "SELECT ?s WHERE { ?s a ex:Thing }\n"
        "''')\n"
    )
    s = surface_source(src)
    assert s.counts["sparql_query"] == 1
    assert s.query_text_forms["literal"] == 1
    assert s.query_forms["select"] == 1
    assert s.counts["sparql_assigned"] == 1


def test_query_shape_skips_prologue_and_comments():
    assert _query_shape("PREFIX ex: <u#>\nCONSTRUCT { } WHERE { }") == "construct"
    assert _query_shape("# a comment\nASK { }") == "ask"
    assert _query_shape("BASE <u>\nPREFIX a: <b>\nDELETE { } WHERE { }") == "delete"
    assert _query_shape("\n  SELECT * WHERE { }") == "select"
    assert _query_shape("nonsense") == "other"


def test_interpolated_query_is_flagged():
    src = PREAMBLE + (
        "iri = 'http://example.org/x'\n"
        "g.query(f'SELECT ?p WHERE {{ <{iri}> ?p ?o }}')\n"
    )
    s = surface_source(src)
    assert s.query_text_forms["fstring"] == 1
    assert s.counts["sparql_interpolated"] == 1
    assert s.query_forms["non_literal"] == 1


def test_init_bindings_counted():
    src = PREAMBLE + (
        "g.query('SELECT ?p WHERE { ?s ?p ?o }', initBindings={'s': EX.a})\n"
    )
    s = surface_source(src)
    assert s.counts["bind_initbindings"] == 1


def test_query_consumed_by_for_loop():
    src = PREAMBLE + "for row in g.query('SELECT ?s WHERE { ?s ?p ?o }'):\n    pass\n"
    s = surface_source(src)
    assert s.counts["sparql_consumed_for"] == 1


def test_update_call():
    src = PREAMBLE + "g.update('INSERT DATA { <a> <b> <c> }')\n"
    s = surface_source(src)
    assert s.counts["sparql_update"] == 1
    assert s.query_forms["insert"] == 1


# --- Q3: traversal ---------------------------------------------------------

def test_selector_in_for_loop():
    src = PREAMBLE + "for o in g.objects(EX.s, RDF.type):\n    pass\n"
    s = surface_source(src)
    assert s.selectors["objects"] == 1
    assert s.selector_contexts["for"] == 1
    assert s.counts["trav_term_selector"] == 1


def test_selector_in_comprehension():
    src = PREAMBLE + "xs = [o for o in g.objects(EX.s, EX.p)]\n"
    s = surface_source(src)
    assert s.selector_contexts["comprehension"] == 1


def test_selector_wrapped_in_next_is_single_value():
    src = PREAMBLE + "o = next(g.objects(EX.s, EX.p))\n"
    s = surface_source(src)
    assert s.counts["trav_single_value"] == 1
    assert s.selector_contexts["next"] == 1


def test_chained_selectors():
    src = PREAMBLE + "x = g.value(g.value(EX.s, EX.p), EX.q)\n"
    s = surface_source(src)
    assert s.selectors["value"] == 2
    assert s.counts["trav_chained"] == 1


def test_triples_is_a_tuple_selector():
    src = PREAMBLE + "for s, p, o in g.triples((None, None, None)):\n    pass\n"
    s = surface_source(src)
    assert s.counts["trav_tuple_selector"] == 1


def test_selector_on_unknown_receiver_is_ignored():
    """`.objects` on something that is not a known graph must not count."""
    src = "class C:\n    pass\nc = C()\nfor o in c.objects(1, 2):\n    pass\n"
    s = surface_source(src)
    assert s.counts.get("trav_calls", 0) == 0


# --- Q5: adds --------------------------------------------------------------

def test_isolated_add():
    src = PREAMBLE + "g.add((EX.s, RDF.type, EX.T))\n"
    s = surface_source(src)
    assert s.counts["add_triples"] == 1
    assert s.counts["add_isolated"] == 1
    assert s.add_runs[1] == 1


def test_run_of_adds_with_shared_subject():
    src = PREAMBLE + (
        "g.add((EX.s, RDF.type, EX.T))\n"
        "g.add((EX.s, EX.p, Literal(1)))\n"
        "g.add((EX.s, EX.q, Literal(2)))\n"
    )
    s = surface_source(src)
    assert s.add_runs[3] == 1
    assert s.add_runs_same_subject[3] == 1
    assert s.counts["add_in_run"] == 3
    assert s.counts["add_run_shared_subject_triples"] == 3
    assert s.counts.get("add_isolated", 0) == 0


def test_run_broken_by_other_statement():
    src = PREAMBLE + (
        "g.add((EX.s, EX.p, EX.o))\n"
        "print('hello')\n"
        "g.add((EX.s, EX.q, EX.o))\n"
    )
    s = surface_source(src)
    assert s.add_runs[1] == 2
    assert s.counts["add_isolated"] == 2


def test_run_broken_by_different_receiver():
    src = PREAMBLE + (
        "h = Graph()\n"
        "g.add((EX.s, EX.p, EX.o))\n"
        "h.add((EX.s, EX.q, EX.o))\n"
    )
    s = surface_source(src)
    assert s.add_runs[1] == 2


def test_adds_in_loop_are_flagged():
    src = PREAMBLE + (
        "for i in range(3):\n"
        "    g.add((EX.s, EX.p, Literal(i)))\n"
    )
    s = surface_source(src)
    assert s.counts["add_in_loop"] == 1


def test_long_receiver_is_measured():
    src = (
        "from rdflib import Graph, Namespace, RDF\n"
        "EX = Namespace('http://example.org/')\n"
        "class C:\n"
        "    def f(self):\n"
        "        self.graph = Graph()\n"
        "        self.graph.add((EX.s, RDF.type, EX.T))\n"
    )
    s = surface_source(src)
    assert s.counts["add_long_receiver"] == 1
    assert s.counts["add_receiver_chars"] == len("self.graph")


# --- Q6: graphs ------------------------------------------------------------

def test_single_graph_file():
    src = PREAMBLE + "g.add((EX.s, EX.p, EX.o))\ng.serialize()\n"
    s = surface_source(src)
    assert s.counts["file_single_graph"] == 1
    assert s.counts["graphs_distinct"] == 1


def test_two_graphs_in_one_file():
    src = PREAMBLE + (
        "h = Graph()\n"
        "g.add((EX.s, EX.p, EX.o))\n"
        "h.add((EX.s, EX.p, EX.o))\n"
    )
    s = surface_source(src)
    assert s.counts["graphs_distinct"] == 2
    assert s.counts.get("file_single_graph", 0) == 0


def test_named_graph_identifier():
    src = (
        "from rdflib import Graph, URIRef\n"
        "g = Graph(identifier=URIRef('http://example.org/g'))\n"
    )
    s = surface_source(src)
    assert s.counts["graph_named_identifier"] == 1


def test_dataset_constructor():
    src = "from rdflib import Dataset\nd = Dataset()\n"
    s = surface_source(src)
    assert s.counts["graph_ctor_dataset"] == 1


# --- robustness ------------------------------------------------------------

def test_syntax_error_is_recorded_not_raised():
    s = surface_source("def broken(:\n")
    assert s.counts["parse_error"] == 1


def test_plain_python_yields_nothing():
    s = surface_source("xs = [1, 2, 3]\nfor x in xs:\n    print(x)\n")
    assert not s.counts


# --- Q3 (continued): navigation across nested loops ------------------------

def test_navigation_via_nested_loops():
    """The common traversal shape: the outer loop's variable feeds the inner."""
    src = PREAMBLE + (
        "for s in g.subjects(RDF.type, EX.T):\n"
        "    for o in g.objects(s, EX.p):\n"
        "        print(o)\n"
    )
    s = surface_source(src)
    assert s.counts["trav_navigation_loop"] == 1
    assert s.counts["trav_navigation_depth_1"] == 1


def test_navigation_three_levels_deep():
    src = PREAMBLE + (
        "for a in g.subjects(RDF.type, EX.T):\n"
        "    for b in g.objects(a, EX.p):\n"
        "        for c in g.objects(b, EX.q):\n"
        "            print(c)\n"
    )
    s = surface_source(src)
    assert s.counts["trav_navigation_loop"] == 2
    assert s.counts["trav_navigation_depth_2"] == 1


def test_navigation_in_comprehension():
    src = PREAMBLE + (
        "xs = [o for s in g.subjects(RDF.type, EX.T) for o in g.objects(s, EX.p)]\n"
    )
    s = surface_source(src)
    assert s.counts["trav_navigation_loop"] == 1


def test_independent_loops_are_not_navigation():
    """Two selector loops in sequence share no variable: not a traversal."""
    src = PREAMBLE + (
        "for s in g.subjects(RDF.type, EX.T):\n"
        "    print(s)\n"
        "for o in g.objects(EX.a, EX.p):\n"
        "    print(o)\n"
    )
    s = surface_source(src)
    assert s.counts.get("trav_navigation_loop", 0) == 0


def test_distinct_query_texts_counted_once_for_lines():
    """A query constant used twice occupies its source lines only once."""
    src = PREAMBLE + (
        "Q = '''SELECT ?s\nWHERE { ?s ?p ?o }'''\n"
        "a = g.query(Q)\n"
        "b = g.query(Q)\n"
    )
    s = surface_source(src)
    assert s.counts["sparql_query"] == 2
    assert s.counts["sparql_query_calls_literal"] == 2
    assert s.counts["sparql_queries_distinct"] == 1
    assert s.counts["sparql_query_lines"] == 2
    assert s.query_text_forms["literal_via_name"] == 2


def test_static_versus_computed_terms():
    """A triple of namespace terms is writable in Turtle as-is; one with a
    computed term needs an interpolation."""
    src = PREAMBLE + (
        "name = 'x'\n"
        "g.add((EX.s, RDF.type, EX.T))\n"
        "g.add((EX.s, EX.p, URIRef('http://example.org/' + name)))\n"
    )
    s = surface_source(src)
    assert s.counts["add_terms_all_static"] == 1
    assert s.counts["add_terms_computed"] == 1


def test_literal_with_datatype_is_static():
    src = PREAMBLE + (
        "from rdflib import XSD\n"
        "g.add((EX.s, EX.p, Literal('3', datatype=XSD.integer)))\n"
    )
    s = surface_source(src)
    assert s.counts["add_terms_all_static"] == 1


def test_run_lines_are_measured():
    src = PREAMBLE + (
        "g.add((EX.s, EX.p, EX.o))\n"
        "g.add((EX.s, EX.q, EX.o))\n"
    )
    s = surface_source(src)
    assert s.counts["add_run_lines"] == 2


# --- Q1 (continued): repository-wide namespace export index ----------------

def test_namespace_index_and_relative_import(tmp_path):
    """`from .namespaces import EX` resolves to the exporting module."""
    from rdfeval.surface import build_namespace_index, make_import_resolver

    pkg = tmp_path / "bricksrc"
    pkg.mkdir()
    (pkg / "namespaces.py").write_text(
        "from rdflib import Namespace\n"
        "BRICK = Namespace('https://brickschema.org/schema/Brick#')\n"
        "NOT_A_NS = 3\n"
    )
    (pkg / "shapes.py").write_text("from .namespaces import BRICK\n")

    index = build_namespace_index(tmp_path)
    assert index["bricksrc/namespaces"]["BRICK"] == \
        "https://brickschema.org/schema/Brick#"
    assert "NOT_A_NS" not in index["bricksrc/namespaces"]

    resolve = make_import_resolver(index, "bricksrc/shapes.py")
    assert resolve("namespaces", 1, "BRICK") == \
        "https://brickschema.org/schema/Brick#"
    assert resolve("namespaces", 1, "MISSING") is None


def test_namespace_index_absolute_import(tmp_path):
    from rdfeval.surface import build_namespace_index, make_import_resolver

    pkg = tmp_path / "src" / "mypkg"
    pkg.mkdir(parents=True)
    (pkg / "vocab.py").write_text(
        "from rdflib import Namespace\nEX = Namespace('http://example.org/')\n")

    index = build_namespace_index(tmp_path)
    resolve = make_import_resolver(index, "src/mypkg/app.py")
    assert resolve("mypkg.vocab", 0, "EX") == "http://example.org/"


def test_namespace_index_skips_modules_without_namespaces(tmp_path):
    from rdfeval.surface import build_namespace_index

    (tmp_path / "plain.py").write_text("x = 1\n")
    assert build_namespace_index(tmp_path) == {}


def test_import_resolution_feeds_the_counter(tmp_path):
    """End to end: the resolver makes a project import count for Q1."""
    from rdfeval.surface import build_namespace_index, make_import_resolver

    (tmp_path / "vocab.py").write_text(
        "from rdflib import Namespace\nEX = Namespace('http://example.org/')\n")
    index = build_namespace_index(tmp_path)
    resolve = make_import_resolver(index, "app.py")

    s = surface_source("from vocab import EX\nprint(EX)\n", "app.py",
                       resolve_import=resolve)
    assert s.counts["ns_imported_from_project"] == 1
    assert s.ns_imported_iris == {"EX": "http://example.org/"}


# --- the site index of the strata study (design record corpus/403) ----------

STRATA_SOURCE = '''\
from rdflib import Graph, Namespace, Literal, RDF, XSD, URIRef

EX = Namespace("http://example.org/")
g = Graph()

def build(rows):
    LOCAL = Namespace("http://local/")
    for row in rows:
        s = URIRef(EX + row["id"])
        g.add((s, RDF.type, EX.Thing))
        g.add((s, EX.v, Literal(row["v"], datatype=XSD.integer)))
    g.add((EX.a, EX.p, EX.b))
    g.remove((EX.a, None, None))

def read(graph: Graph):
    label = graph.value(EX.a, EX.name)
    first = next(graph.subjects(RDF.type, EX.Thing))
    if any(graph.objects(EX.a, EX.p)):
        pass
    for s in graph.subjects(RDF.type, EX.Thing):
        for o in graph.objects(s, EX.p):
            print(o)
    graph.query("SELECT ?s WHERE { ?s a ?c }")
    graph.query(f"SELECT ?s WHERE {{ ?s <{EX.p}> ?o }}")
    graph.query("SELECT ?s WHERE { ?s ?p ?o }", initBindings={"p": EX.p})
    return label, first
'''


def _sites_by_kind(source=STRATA_SOURCE):
    from collections import Counter
    from rdfeval.surface import surface_source
    return Counter(s["kind"] for s in surface_source(source, "t.py", "r/r").sites)


def test_every_stratum_has_a_site_producer():
    """Each stratum of corpus/403 must be reachable: a stratum no shape ever
    produces would silently sample nothing."""
    from rdfeval.surface import STRATA
    kinds = _sites_by_kind()
    reachable = set(kinds) | {"ns_import_project"}   # needs a project index
    assert set(STRATA) - reachable == set()


def test_site_kinds_on_a_representative_file():
    k = _sites_by_kind()
    assert k["ns_def_local"] == 1
    assert k["add_isolated"] == 1              # g.add((EX.a, EX.p, EX.b))
    assert k["add_run_shared_subject"] == 1    # the two adds on `s`
    assert k["add_in_loop"] == 1               # same run, second stratum
    assert k["remove"] == 1
    assert k["trav_single_value"] == 2         # .value(...) and next(...)
    assert k["trav_existence"] == 1            # any(...)
    assert k["trav_navigation"] == 1           # objects(s, …) inside subjects
    assert k["sparql_literal"] == 2
    assert k["sparql_interpolated"] == 1
    assert k["bind_initbindings"] == 1
    assert k["coercion_datatype"] == 1         # Literal(row["v"], …)


def test_a_site_locates_its_enclosing_function():
    from rdfeval.surface import surface_source
    sites = surface_source(STRATA_SOURCE, "t.py", "r/r").sites
    by_kind = {s["kind"]: s for s in sites}
    assert by_kind["remove"]["qualname"] == "build"
    assert by_kind["trav_navigation"]["qualname"] == "read"
    assert by_kind["remove"]["snippet"].strip().startswith("g.remove(")
    assert by_kind["add_run_shared_subject"]["end_line"] > \
        by_kind["add_run_shared_subject"]["line"]


def test_remove_counters():
    from rdfeval.surface import surface_source
    counts = surface_source(STRATA_SOURCE, "t.py", "r/r").counts
    assert counts["remove_calls"] == 1
    assert counts["remove_triple_pattern"] == 1
    assert counts["remove_with_wildcard"] == 1
    assert counts["remove_wildcards_2"] == 1


def test_a_constant_literal_is_not_a_coercion_site():
    from rdfeval.surface import surface_source
    src = ('from rdflib import Graph, Literal, XSD\n'
           'g = Graph()\n'
           'x = Literal("1", datatype=XSD.integer)\n')
    s = surface_source(src, "t.py", "r/r")
    assert not [site for site in s.sites if site["kind"] == "coercion_datatype"]
    assert s.counts["literal_constant_typed"] == 1


def test_a_defined_namespace_base_class_is_not_a_namespace():
    """`class AliasingDefinedNamespace(DefinedNamespace)` is machinery for
    building namespaces, not one: importing it is not a namespace import."""
    from rdfeval.surface import _exported_namespaces
    machinery = ("from rdflib.namespace import DefinedNamespace\n"
                 "class AliasingDefinedNamespace(DefinedNamespace):\n"
                 "    @classmethod\n"
                 "    def alias(cls, name):\n"
                 "        return name\n")
    real = ("from rdflib.namespace import DefinedNamespace, Namespace\n"
            "class PSDO(DefinedNamespace):\n"
            "    _NS = Namespace('http://purl.obolibrary.org/obo/')\n"
            "    thing: str\n")
    assert _exported_namespaces(machinery) == {}
    assert _exported_namespaces(real) == {"PSDO": ""}
