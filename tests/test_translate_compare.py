"""End-to-end tests of the mechanical draft, the harness and pair metrics."""

import subprocess
import sys
from pathlib import Path

from rdfeval.compare import measure_pair
from rdfeval.translate import draft_translation

ORIGINAL = """\
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF

EX = Namespace("http://example.org/")

g = Graph()
g.add((EX.alice, FOAF.name, Literal("Alice", lang="en")))
g.add((EX.alice, FOAF.knows, EX.bob))
g.add((EX.bob, FOAF.name, Literal("Bob", lang="en")))
g.add((EX.bob, FOAF.mbox, URIRef("mailto:bob@example.org")))
"""


def test_draft_translation_produces_valid_ldpy():
    from ldpy.transpiler import transpile
    draft, notes = draft_translation(ORIGINAL)
    assert "@prefix ex: <http://example.org/> ." in draft
    assert "@prefix foaf: <http://xmlns.com/foaf/0.1/> ." in draft
    assert "g += g{" in draft
    assert "URIRef" not in draft.replace("from rdflib import Graph, Literal, Namespace, URIRef", "")
    transpile(draft)            # must be syntactically valid ldpy


def test_draft_is_semantics_preserving():
    """The mechanical draft of ORIGINAL builds an isomorphic graph."""
    from ldpy.transpiler import transpile
    from rdflib.compare import to_isomorphic
    draft, _ = draft_translation(ORIGINAL)
    ns1: dict = {}
    exec(compile(ORIGINAL, "orig", "exec"), ns1)
    ns2: dict = {}
    exec(compile(transpile(draft).code, "draft", "exec"), ns2)
    assert to_isomorphic(ns1["g"]) == to_isomorphic(ns2["g"])


def test_measure_pair_shows_reduction():
    draft, _ = draft_translation(ORIGINAL)
    pair = measure_pair(ORIGINAL, draft)
    assert pair["python"]["triples_added"] == 4
    assert pair["ldpy"]["triples_semantic"] == 4
    assert pair["ratios"]["tokens"] < 1.0
    assert pair["ldpy"]["corr_scaffolding_tokens_per_triple"] \
        < pair["python"]["corr_scaffolding_tokens_per_triple"]


def test_harness_module_state(tmp_path):
    ex = tmp_path / "example"
    ex.mkdir()
    (ex / "original.py").write_text(ORIGINAL)
    draft, _ = draft_translation(ORIGINAL)
    (ex / "translated.ldpy").write_text(draft)
    (ex / "driver.py").write_text(
        "from rdfeval.harness import run_pair\n"
        "run_pair(__file__)\n")
    proc = subprocess.run([sys.executable, str(ex / "driver.py")],
                          capture_output=True, text=True, cwd=ex, timeout=60)
    assert "RDFEVAL-VERDICT" in proc.stderr
    import json
    verdict = json.loads(proc.stderr.split("RDFEVAL-VERDICT ", 1)[1].splitlines()[0])
    assert verdict["equivalent"] is True, verdict


def test_harness_detects_difference(tmp_path):
    ex = tmp_path / "example"
    ex.mkdir()
    (ex / "original.py").write_text(ORIGINAL)
    wrong = ORIGINAL.replace('Literal("Bob", lang="en")', 'Literal("Eve", lang="en")')
    (ex / "translated.ldpy").write_text(wrong)
    (ex / "driver.py").write_text(
        "from rdfeval.harness import run_pair\n"
        "run_pair(__file__)\n")
    proc = subprocess.run([sys.executable, str(ex / "driver.py")],
                          capture_output=True, text=True, cwd=ex, timeout=60)
    import json
    verdict = json.loads(proc.stderr.split("RDFEVAL-VERDICT ", 1)[1].splitlines()[0])
    assert verdict["equivalent"] is False


PROJECT_NS = """\
from rdflib import Namespace, RDF

BRICK = Namespace("https://brickschema.org/schema/Brick#")
SH = Namespace("http://www.w3.org/ns/shacl#")
A = RDF.type
"""

REGION_WITH_PROJECT_NS = """\
from .namespaces import BRICK, A, SH
from rdflib import BNode, Literal


def build(G):
    prop = BNode("myprop")
    G.add((BRICK.Thing, A, SH.NodeShape))
    G.add((prop, SH.path, BRICK.hasPart))
    G.add((BRICK.Thing, SH.property, prop))
"""


def _resolver(module, level):
    return PROJECT_NS if module.endswith("namespaces") else None


def test_project_namespaces_become_prefixes():
    draft, notes = draft_translation(REGION_WITH_PROJECT_NS, resolve_module=_resolver)
    assert "@prefix brick: <https://brickschema.org/schema/Brick#> ." in draft
    assert "@prefix sh: <http://www.w3.org/ns/shacl#> ." in draft
    assert "brick:Thing a sh:NodeShape" in draft      # A alias -> Turtle `a`
    assert "_:myprop" in draft                        # single-island bnode label
    assert "BNode(" not in draft.split("def build")[1]
    from ldpy.transpiler import transpile
    transpile(draft)


def test_bnode_label_kept_as_python_when_shared_across_islands():
    src = """\
from rdflib import BNode, Graph, Namespace

EX = Namespace("http://e/")


def build(g, other):
    b = BNode("shared")
    g.add((EX.a, EX.p, b))
    other.do_something()
    g.add((b, EX.q, EX.c))
"""
    draft, _ = draft_translation(src)
    # two separate islands -> the blank node must stay a Python BNode
    assert "BNode(\"shared\")" in draft or "BNode('shared')" in draft
    assert "_:shared" not in draft


def test_interpolated_local_part():
    src = """\
from rdflib import Graph, Namespace

EX = Namespace("http://e/")


def build(g, name):
    g.add((EX[name], EX.p, EX.o))
"""
    draft, _ = draft_translation(src)
    assert "ex:{name}" in draft
    from ldpy.transpiler import transpile
    transpile(draft)


PARENTHESISED = """\
from rdflib import (
    Graph,
    Namespace,
    RDF,
)

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/")

g = Graph()
g.add((EX.a, RDF.type, OWL_NS.Class))
"""


def test_prefix_declarations_land_after_a_parenthesised_import():
    """A `@prefix` inserted between the lines of `from x import (…)` does
    not parse; the insertion point must respect bracket depth."""
    from ldpy.transpiler import transpile
    draft, _ = draft_translation(PARENTHESISED)
    lines = draft.splitlines()
    assert lines[:5] == ["from rdflib import (", "    Graph,", "    Namespace,",
                         "    RDF,", ")"]
    assert draft.index("@prefix ex:") > draft.index(")\n")
    transpile(draft, filename="<parenthesised>")


def test_prefix_label_is_usable_outside_islands():
    """`-` stays subtraction outside an island, so `OWL_NS` may not become
    `owl-ns:` (reference/language/lexical.md)."""
    draft, _ = draft_translation(PARENTHESISED)
    assert "@prefix owl: <http://www.w3.org/2002/07/owl#> ." in draft
    assert "owl-ns" not in draft


def test_prefix_label_keeps_distinct_names_distinct():
    from rdfeval.translate import _label_for
    taken: set[str] = set()
    for var, expected in (("EX", "ex"), ("OWL_NS", "owl"), ("SCHEMA_ORG", "schemaorg"),
                          ("brick_", "brick"), ("_private", "private"), ("NS2", "ns2")):
        label = _label_for(var, taken)
        assert label == expected, (var, label)
        if label:
            taken.add(label)
    assert _label_for("EX", taken) is None       # collision: left to the human


def test_indented_import_does_not_move_the_declarations_into_a_body():
    src = """\
from rdflib import Graph, Namespace

EX = Namespace("http://example.org/")

def build():
    import json
    g = Graph()
    g.add((EX.a, EX.p, EX.b))
    return g
"""
    from ldpy.transpiler import transpile
    draft, _ = draft_translation(src)
    assert draft.splitlines()[1].startswith("@prefix ex:")
    transpile(draft, filename="<indented>")


# --- the reading oracle (design record corpus/403) ---------------------------

FIXTURE_TTL = """\
@prefix ex: <http://example.org/> .
ex:a a ex:Sensor ; ex:v 1 ; ex:label "A" .
ex:b a ex:Sensor ; ex:v 2 ; ex:label "B" .
ex:c a ex:Other  ; ex:v 3 .
"""

READ_ORIGINAL = """\
from rdflib import Graph, Namespace, RDF

EX = Namespace("http://example.org/")


def read(g: Graph):
    sensors = g.subjects(RDF.type, EX.Sensor)
    label = g.value(EX.a, EX.label)
    values = [int(v) for v in g.objects(EX.b, EX.v)]
    return sorted(str(s) for s in sensors), label, values
"""

READ_TRANSLATED = """\
from rdflib import Graph
@prefix ex: <http://example.org/> .


def read(g: Graph):
    @graph g
    sensors = m{ ?s a ex:Sensor }
    label = m{ ex:a ex:label ?l }.first()
    values = [int(v) for v in m{ ex:b ex:v ?v }]
    return sorted(str(s) for s in sensors), label, values
"""


def _read_pair(tmp_path, translated=READ_TRANSLATED, driver_kwargs="fixture='fixture.ttl'"):
    (tmp_path / "fixture.ttl").write_text(FIXTURE_TTL)
    (tmp_path / "original.py").write_text(READ_ORIGINAL)
    (tmp_path / "translated.ldpy").write_text(translated)
    (tmp_path / "driver.py").write_text(
        "from rdfeval.harness import run_pair\n"
        f"VERDICT = run_pair(__file__, entry='read', {driver_kwargs})\n")
    proc = subprocess.run([sys.executable, str(tmp_path / "driver.py")],
                          capture_output=True, text=True, cwd=tmp_path,
                          timeout=120)
    import json
    for line in proc.stderr.splitlines():
        if line.startswith("RDFEVAL-VERDICT "):
            return json.loads(line[len("RDFEVAL-VERDICT "):])
    raise AssertionError(proc.stderr or proc.stdout)


def test_reading_oracle_proves_a_read_region_equivalent(tmp_path):
    """The oracle for reading is not isomorphism but the equality of the
    values both versions produce from the same input graph."""
    verdict = _read_pair(tmp_path)
    assert verdict["error"] is None, verdict["error"]
    assert verdict["equivalent"], verdict["diffs"]
    assert verdict["method"] == "fixture:fixture.ttl entry:read"
    assert verdict["ordered"] is False


def test_reading_oracle_catches_a_wrong_pattern(tmp_path):
    wrong = READ_TRANSLATED.replace("m{ ?s a ex:Sensor }", "m{ ?s a ex:Other }")
    verdict = _read_pair(tmp_path, translated=wrong)
    assert not verdict["equivalent"]
    assert any("result" in d for d in verdict["diffs"])


def test_a_lazy_result_is_materialised_before_comparison():
    """A generator compares equal to nothing, including itself: both sides
    must be walked first."""
    from rdflib import Graph, Literal, URIRef
    from rdfeval.harness import materialise
    g = Graph()
    g.add((URIRef("http://e/a"), URIRef("http://e/p"), Literal(1)))
    assert materialise(g.objects()) == [Literal(1)]
    assert materialise(iter([1, 2])) == [1, 2]
    assert materialise({"k": iter([1])}) == {"k": [1]}
    assert materialise(g) is g                      # a graph stays a graph
    assert materialise("abc") == "abc"              # a string is not a sequence


def test_a_sparql_result_is_materialised_as_rows():
    from rdflib import Graph
    from rdfeval.harness import materialise
    g = Graph().parse(data=FIXTURE_TTL, format="turtle")
    rows = materialise(g.query(
        "SELECT ?s WHERE { ?s a <http://example.org/Sensor> } ORDER BY ?s"))
    assert [str(r[0]) for r in rows] == ["http://example.org/a",
                                         "http://example.org/b"]
    assert materialise(g.query("ASK { <http://example.org/a> a "
                               "<http://example.org/Sensor> }")) is True


def test_solution_order_is_not_meaning_unless_the_driver_says_so():
    """No store promises an order, so a fixture run compares multisets."""
    from rdfeval.harness import _compare_value
    diffs: list = []
    _compare_value([1, 2], [2, 1], "r", diffs, ordered=False)
    assert diffs == []
    _compare_value([1, 2], [2, 1], "r", diffs, ordered=True)
    assert len(diffs) == 1
    _compare_value([1, 1, 2], [1, 2, 2], "r", diffs, ordered=False)
    assert len(diffs) == 2, "a multiset still counts multiplicity"


def test_order_is_ignored_at_every_depth_not_just_the_top():
    """A region returning {"Add": {"hasReagent": [...]}} built from solutions
    has the same non-determinism one level down: comparing only the outer
    list fails such a pair for a reason that is not its meaning."""
    from rdfeval.harness import _compare_value
    a = {"Add": {"hasReagent": ["B", "A"], "label": "Add Water"}}
    b = {"Add": {"hasReagent": ["A", "B"], "label": "Add Water"}}
    diffs: list = []
    _compare_value(a, b, "r", diffs, ordered=False)
    assert diffs == []
    _compare_value(a, b, "r", diffs, ordered=True)
    assert len(diffs) == 1, "ordered=True still holds the order to account"
    _compare_value(a, {"Add": {"hasReagent": ["A"], "label": "Add Water"}},
                   "r", diffs, ordered=False)
    assert len(diffs) == 2, "a missing element is still a difference"


def test_a_row_keeps_its_column_order_when_rows_are_unordered():
    """ordered=False frees the order of the rows, not of a row's columns: a
    glue that swaps (concept, label) into (label, concept) is a difference."""
    from rdfeval.harness import _compare_value
    a = [("c1", "Alpha"), ("c2", "Beta")]
    diffs: list = []
    _compare_value(a, list(reversed(a)), "r", diffs, ordered=False)
    assert diffs == []
    _compare_value(a, [(l, c) for c, l in a], "r", diffs, ordered=False)
    assert len(diffs) == 1
    _compare_value({"k": [("c1", "x")]}, {"k": [("x", "c1")]}, "r", diffs,
                   ordered=False)
    assert len(diffs) == 2, "at every depth"


def test_turtle_a_abbreviates_rdf_type_in_predicate_position_only():
    """`a` is a predicate abbreviation: `RDF.type` as an OBJECT stays a term."""
    from ldpy.transpiler import transpile
    src = ("from rdflib import Graph, BNode, RDF\n"
           "g = Graph()\n"
           "bn = BNode()\n"
           "g.add((bn, RDF.type, RDF.Statement))\n"
           "g.add((bn, RDF.first, RDF.type))\n")
    draft, _ = draft_translation(src)
    assert "rdf:type a" not in draft
    assert "rdf:first rdf:type" in draft
    assert "{bn} a rdf:Statement" in draft
    transpile(draft, filename="<a-position>")


def test_stdout_of_the_called_region_is_compared(tmp_path):
    """A region whose whole effect is printing has nothing else to compare:
    the entry-point path must capture what each side writes."""
    (tmp_path / "original.py").write_text(
        "from rdflib import Graph, Namespace\n"
        "EX = Namespace('http://e/')\n"
        "def show(g: Graph):\n"
        "    for o in g.objects(EX.a, EX.p):\n"
        "        print('seen', o)\n")
    (tmp_path / "translated.ldpy").write_text(
        "from rdflib import Graph\n"
        "@prefix ex: <http://e/> .\n"
        "def show(g: Graph):\n"
        "    for o in m{ ex:a ex:p ?o }(g):\n"
        "        print('SEEN', o)\n")          # deliberately different
    (tmp_path / "fixture.ttl").write_text(
        "@prefix ex: <http://e/> .\nex:a ex:p 1 .\n")
    (tmp_path / "driver.py").write_text(
        "from rdfeval.harness import run_pair\n"
        "VERDICT = run_pair(__file__, entry='show', fixture='fixture.ttl')\n")
    proc = subprocess.run([sys.executable, "driver.py"], cwd=tmp_path,
                          capture_output=True, text=True, timeout=120)
    import json
    verdict = next(json.loads(line[len("RDFEVAL-VERDICT "):])
                   for line in proc.stderr.splitlines()
                   if line.startswith("RDFEVAL-VERDICT "))
    assert not verdict["equivalent"]
    assert any("stdout differs" in d for d in verdict["diffs"]), verdict["diffs"]


def test_module_state_mode_compares_computed_values_not_just_graphs(tmp_path):
    """A region that only READS a graph leaves its result in a variable.
    Comparing graphs alone gives a hollow green: they are equal because
    nothing touched them."""
    (tmp_path / "original.py").write_text(
        "from rdflib import Graph, Namespace, Literal\n"
        "EX = Namespace('http://e/')\n"
        "g = Graph()\n"
        "g.add((EX.a, EX.p, Literal('yes')))\n"
        "name = g.value(EX.a, EX.p)\n")
    (tmp_path / "translated.ldpy").write_text(
        "@prefix ex: <http://e/> .\n"
        "@graph as g\n"
        "+{ ex:a ex:p \"yes\" }\n"
        "name = m{ ex:a ex:q ?v }.first()\n")     # wrong predicate
    (tmp_path / "driver.py").write_text(
        "from rdfeval.harness import run_pair\nVERDICT = run_pair(__file__)\n")
    proc = subprocess.run([sys.executable, "driver.py"], cwd=tmp_path,
                          capture_output=True, text=True, timeout=120)
    import json
    verdict = next(json.loads(line[len("RDFEVAL-VERDICT "):])
                   for line in proc.stderr.splitlines()
                   if line.startswith("RDFEVAL-VERDICT "))
    assert not verdict["equivalent"], "a wrong read must not pass"
    assert any("value name" in d for d in verdict["diffs"]), verdict["diffs"]
    assert "name" in verdict["values_compared"]
    assert verdict["names_only_original"] == ["EX"], \
        "a name only one side defines is reported, not silently skipped"


def test_only_judgeable_values_are_compared():
    """Two runs build two instances: an object without __eq__ compares by
    identity and would report a difference on every pair."""
    import logging
    from rdflib import Literal, URIRef
    from rdfeval.harness import _comparable
    assert _comparable(Literal("x")) and _comparable(URIRef("http://e/"))
    assert _comparable("s") and _comparable(3) and _comparable(None)
    assert _comparable([Literal(1), "a"]) and _comparable({"k": URIRef("http://e/")})
    assert not _comparable(logging.getLogger("x"))
    assert not _comparable(object())
    assert not _comparable([object()])


def test_a_call_that_observes_nothing_is_not_a_green(tmp_path):
    """A region whose only effect is a file write returns None, mutates no
    argument and prints nothing: a green would say only "it did not crash"."""
    for name in ("original.py", "translated.ldpy"):
        (tmp_path / name).write_text(
            "def main():\n"
            "    open('out.txt', 'w').write('x')\n")
    (tmp_path / "driver.py").write_text(
        "from rdfeval.harness import run_pair\n"
        "VERDICT = run_pair(__file__, entry='main', calls=[((), {})])\n")
    proc = subprocess.run([sys.executable, "driver.py"], cwd=tmp_path,
                          capture_output=True, text=True, timeout=120)
    import json
    verdict = next(json.loads(line[len("RDFEVAL-VERDICT "):])
                   for line in proc.stderr.splitlines()
                   if line.startswith("RDFEVAL-VERDICT "))
    assert not verdict["equivalent"]
    assert verdict["observed"] is False
    assert any("nothing observable" in d for d in verdict["diffs"])


RAISING = """\
from rdflib import Graph, URIRef

def add(g, s):
    if not s:
        raise ValueError("empty subject")
    g.add((URIRef(s), URIRef("http://e/p"), URIRef("http://e/o")))
"""


def _raising_pair(tmp_path, translated):
    ex = tmp_path / "ex"
    ex.mkdir()
    (ex / "original.py").write_text(RAISING)
    (ex / "translated.ldpy").write_text(translated)
    (ex / "driver.py").write_text(
        "from rdflib import Graph\nfrom rdfeval.harness import run_pair\n"
        "run_pair(__file__, entry='add', calls=[lambda: ((Graph(), 'http://e/s'), {}),"
        " lambda: ((Graph(), ''), {})])\n")
    proc = subprocess.run([sys.executable, str(ex / "driver.py")],
                          capture_output=True, text=True, cwd=ex, timeout=60)
    import json
    return json.loads(proc.stderr.split("RDFEVAL-VERDICT ", 1)[1].splitlines()[0])


def test_two_identical_raises_are_an_agreement(tmp_path):
    verdict = _raising_pair(tmp_path, RAISING)
    assert verdict["equivalent"] is True, verdict


def test_a_raise_on_one_side_only_is_a_difference(tmp_path):
    lenient = RAISING.replace('raise ValueError("empty subject")', "return")
    verdict = _raising_pair(tmp_path, lenient)
    assert verdict["equivalent"] is False and not verdict["error"]
    assert any("outcome differs" in d for d in verdict["diffs"])


def test_a_different_message_is_a_difference(tmp_path):
    verdict = _raising_pair(tmp_path, RAISING.replace("empty subject", "no subject"))
    assert verdict["equivalent"] is False


def _run_driver(tmp_path, original, translated, driver, fixture=None,
                name="ex"):
    import json
    ex = tmp_path / name
    ex.mkdir()
    (ex / "original.py").write_text(original)
    (ex / "translated.ldpy").write_text(translated)
    (ex / "driver.py").write_text(driver)
    if fixture is not None:
        (ex / "fixture.ttl").write_text(fixture)
    proc = subprocess.run([sys.executable, str(ex / "driver.py")],
                          capture_output=True, text=True, cwd=ex, timeout=60)
    return json.loads(proc.stderr.split("RDFEVAL-VERDICT ", 1)[1].splitlines()[0])


METHOD = """\
from rdflib import URIRef

def tag(self, s):
    self.g.add((URIRef(s), URIRef("http://e/p"), URIRef("http://e/o")))
"""

STUB_DRIVER = """\
from rdflib import Graph
from rdfeval.harness import run_pair

class Stub:
    def __init__(self):
        self.g = Graph()

run_pair(__file__, entry="tag", calls=[lambda: ((Stub(), "http://e/s"), {})])
"""


def test_a_stub_self_is_compared_by_its_graph_not_its_identity(tmp_path):
    """One stub per side: by identity they always differed, and drivers grew
    a `demo()` harness on both sides to get around it."""
    verdict = _run_driver(tmp_path, METHOD, METHOD, STUB_DRIVER)
    assert verdict["equivalent"] is True, verdict


def test_a_stub_self_still_shows_what_the_region_wrote(tmp_path):
    wrong = METHOD.replace("http://e/o", "http://e/other")
    verdict = _run_driver(tmp_path, METHOD, wrong, STUB_DRIVER)
    assert verdict["equivalent"] is False
    assert any("arg[0]" in d for d in verdict["diffs"])


NAMES = """\
from rdflib import URIRef

def names(g):
    return {b: str(n) for b, n in g.subject_objects(URIRef("http://e/name"))}
"""

TWO_BNODES = """\
@prefix e: <http://e/> .
e:a e:knows [ e:name "x" ], [ e:name "y" ; e:age 3 ] .
"""

FIXTURE_DRIVER = """\
from rdfeval.harness import run_pair
run_pair(__file__, entry="names", fixture="fixture.ttl")
"""


def test_a_result_keyed_by_blank_nodes_compares(tmp_path):
    """Each side parses its own fixture, so the keys had fresh identifiers
    on each and the dicts never matched."""
    verdict = _run_driver(tmp_path, NAMES, NAMES, FIXTURE_DRIVER, TWO_BNODES)
    assert verdict["equivalent"] is True, verdict


def test_two_blank_nodes_in_different_places_are_not_equal(tmp_path):
    swapped = NAMES.replace("str(n)", "('y' if str(n) == 'x' else 'x')")
    verdict = _run_driver(tmp_path, NAMES, swapped, FIXTURE_DRIVER, TWO_BNODES)
    assert verdict["equivalent"] is False


def test_blank_node_labels_come_from_the_graph_not_the_identifiers():
    from rdflib import Graph
    from rdfeval.harness import bnode_labels, normalise
    g1 = Graph().parse(data=TWO_BNODES, format="turtle")
    g2 = Graph().parse(data=TWO_BNODES, format="turtle")
    l1, l2 = bnode_labels(g1), bnode_labels(g2)
    assert len(set(l1.values())) == 2
    assert sorted(l1.values()) == sorted(l2.values())
    b1 = sorted(normalise(b, l1) for b in l1)
    b2 = sorted(normalise(b, l2) for b in l2)
    assert b1 == b2
    # without labels, any two blank nodes are equal, as before
    assert len({normalise(b) for b in l1}) == 1


PICK = """\
from rdflib import Literal, URIRef

def pick(g):
    return g.value(predicate=URIRef("http://e/name"), object=Literal("x"))
"""


def test_returning_the_wrong_blank_node_is_a_difference(tmp_path):
    """Labels dropped, any two blank nodes were equal: this pair was green."""
    wrong = PICK.replace('Literal("x")', 'Literal("y")')
    driver = FIXTURE_DRIVER.replace('"names"', '"pick"')
    assert _run_driver(tmp_path, PICK, PICK, driver, TWO_BNODES)["equivalent"]
    verdict = _run_driver(tmp_path, PICK, wrong, driver, TWO_BNODES,
                          name="wrong")
    assert verdict["equivalent"] is False


# The hollow-green screen, calibrated on pairs whose emptiness is known.

def test_a_fixture_without_solutions_is_hollow(tmp_path):
    nothing = "@prefix e: <http://e/> .\ne:a e:knows e:b .\n"
    verdict = _run_driver(tmp_path, NAMES, NAMES, FIXTURE_DRIVER, nothing)
    assert verdict["equivalent"] is True and verdict["hollow"] is True


def test_a_fixture_with_solutions_is_not_hollow(tmp_path):
    verdict = _run_driver(tmp_path, NAMES, NAMES, FIXTURE_DRIVER, TWO_BNODES)
    assert verdict["hollow"] is False


def test_a_call_that_only_writes_into_its_self_is_not_hollow(tmp_path):
    verdict = _run_driver(tmp_path, METHOD, METHOD, STUB_DRIVER)
    assert verdict["hollow"] is False


def test_a_raise_is_a_demonstration(tmp_path):
    driver = ("from rdflib import Graph\nfrom rdfeval.harness import run_pair\n"
              "run_pair(__file__, entry='add', calls=[lambda: ((Graph(), ''), {})])\n")
    verdict = _run_driver(tmp_path, RAISING, RAISING, driver)
    assert verdict["hollow"] is False


def test_a_lazy_result_is_read_once_for_both_checks(tmp_path):
    lazy = NAMES.replace("return {b: str(n) for b, n in",
                         "return (str(n) for b, n in").replace(
        'URIRef("http://e/name"))}', 'URIRef("http://e/name")))')
    verdict = _run_driver(tmp_path, lazy, lazy, FIXTURE_DRIVER, TWO_BNODES)
    assert verdict["equivalent"] is True and verdict["hollow"] is False


def test_a_binding_the_original_poses_must_survive():
    """Design record ldpy/027: equivalence covers the triples and the
    bindings the original poses; an added binding is tolerated."""
    from rdflib import Graph, Namespace
    from rdfeval.harness import _compare_value, bindings_lost
    XS = Namespace("http://www.w3.org/2001/XMLSchema#")
    original, moved, extra = Graph(), Graph(), Graph()
    original.bind("xs", XS)
    moved.bind("xs", XS)
    moved.bind("xsd", XS)              # what `@graph` + `@prefix xsd:` does
    extra.bind("xs", XS)
    extra.bind("ex", Namespace("http://example.org/"))
    assert bindings_lost(original, moved) == [("xs", str(XS))]
    assert bindings_lost(original, extra) == []
    diffs: list = []
    _compare_value(original, moved, "graph g", diffs)
    assert diffs and "xs: <http://www.w3.org/2001/XMLSchema#>" in diffs[0]


def test_the_demo_harness_is_not_measured():
    """corpus/403: `demo()` is scaffolding of the study, on neither side."""
    from rdfeval.compare import measure_pair, strip_demo
    body = ("from rdflib import Graph, URIRef\n"
            "def f(g):\n"
            "    g.add((URIRef('http://e/a'), URIRef('http://e/p'),"
            " URIRef('http://e/b')))\n")
    demo = ("\n\ndef demo():\n    g = Graph()\n    f(g)\n"
            "    # a comment inside\n\n    return g\n")
    assert strip_demo(body + demo) == body
    assert strip_demo(body) == body
    assert strip_demo(body + demo + "X = 1\n") == body + "X = 1\n"
    bare = measure_pair(body, body)
    with_demo = measure_pair(body + demo, body + demo)
    assert with_demo["python"]["loc"] == bare["python"]["loc"]
    assert with_demo["ldpy"]["loc"] == bare["ldpy"]["loc"]
