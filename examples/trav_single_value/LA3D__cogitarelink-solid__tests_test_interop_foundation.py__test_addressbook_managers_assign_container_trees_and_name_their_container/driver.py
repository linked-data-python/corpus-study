"""Validation driver for LA3D__cogitarelink-solid__tests_test_interop_foundation.py__test_addressbook_managers_assign_container_trees_and_name_their_container.

This region reads FOUR separate Turtle documents (one per addressbook
manager slug -- person/organization/group/membership), each independently
parsed by the original code (`g = rdflib.Graph(); g.parse(f, ...)`), not one
shared graph.  The region's restored parameter `manager_graphs` maps each
slug to its own graph.

`fixture.ttl` holds all four managers' data (plus a decoy assignment),
addressed by synthetic root IRIs (`urn:ex:mgr:<slug>`) instead of the real
files' relative `<>` (four physical files can't share one `<>` in a single
parsed document).  `_manager_graphs()` parses it once, then re-partitions it
into four isolated per-slug graphs by subject closure from each manager root.

The region is a test: every read feeds an `assert` (each with a message) or
a bare `next()`.  run_pair compares a raise like a value (same exception
type, same message), so each call below either passes on both sides or
raises the same exception on both.  Every scenario after the first two
REPLACES the "person" graph (the first slug the loop visits, so it decides
the outcome) and keeps the three others from fixture.ttl:

  shipped          fixture.ttl, all four managers valid
  real             the four REAL manager files of the origin repository
                   (corpus/repos/LA3D__cogitarelink-solid/overlays/addressbook/
                   interop/managers/*.shapetree.ttl, commit 4912150), parsed
                   as the test parses them: `<>` resolves to the file's URI
  empty            no triple: next() raises StopIteration
  no-manager       the assignment is there, but no `a st:Manager`; two
                   neighbours carry a VALID assignment, one typed with another
                   class, one pointing at st:Manager through another
                   predicate: StopIteration, where a widened subject pattern
                   would pass
  two-managers-ok-first / -bad-first
                   two st:Manager subjects, one valid and one without an
                   assignment, in both store orders: next() takes the first
                   the store yields (passes in one order, fails in the other)
  no-assignment    the manager has no st:hasAssignment; a neighbour subject
                   has a valid one: AssertionError "person: no ..."
  two-assignments-ok-first / -bad-first
                   two st:hasAssignment values, one valid and one wrong:
                   g.value takes the first, the translation must take the same
  no-assigns       the assignment lacks st:assigns; the right tree hangs off
                   it through another predicate written FIRST, and a
                   neighbour assignment has st:assigns the right tree
  no-manages       the same for st:manages
  wrong-assigns    st:assigns names another tree: AssertionError "person"
  assignment-empty-literal / assignment-zero-literal
                   st:hasAssignment is "" or 0: `a is not None` holds (no
                   truth test), and the next reads find nothing on a literal
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph
from rdflib import Graph, URIRef

HERE = Path(__file__).resolve().parent
REAL_DIR = (HERE.parents[2] / "corpus" / "repos" / "LA3D__cogitarelink-solid"
            / "overlays" / "addressbook" / "interop" / "managers")
HAS_ASSIGNMENT = URIRef("http://www.w3.org/ns/shapetrees#hasAssignment")
SLUGS = ("person", "organization", "group", "membership")


def _manager_graphs():
    whole = fixture_graph(HERE / "fixture.ttl")
    graphs = {}
    for slug in SLUGS:
        mgr = URIRef(f"urn:ex:mgr:{slug}")
        g = Graph()
        for t in whole.triples((mgr, None, None)):
            g.add(t)
        for a in whole.objects(mgr, HAS_ASSIGNMENT):
            for t in whole.triples((a, None, None)):
                g.add(t)
        graphs[slug] = g
    return graphs


def _real_graphs():
    graphs = {}
    for slug in SLUGS:
        g = Graph()
        g.parse(REAL_DIR / f"{slug}.shapetree.ttl", format="turtle")
        graphs[slug] = g
    return graphs


_PRE = """\
@prefix st: <http://www.w3.org/ns/shapetrees#> .
@prefix ab: <https://pod.vardeman.me/vault/meta/shapetrees/addressbook.tree#> .
@prefix ex: <http://example.org/> .
"""
_A1_OK = """
<urn:p#a1> st:assigns ab:PersonContainerTree ;
    st:manages <https://pod.vardeman.me/vault/contacts/Person/> .
"""
_A2_BAD = """
<urn:p#a2> st:assigns ab:GroupContainerTree ;
    st:manages <https://pod.vardeman.me/vault/contacts/Group/> .
"""

PERSON = {
    "empty": "",
    "no-manager": _PRE + _A1_OK + """
<urn:p> st:hasAssignment <urn:p#a1> .
<urn:x> a st:Other ; st:hasAssignment <urn:p#a1> .
<urn:y> ex:seeAlso st:Manager ; st:hasAssignment <urn:p#a1> .
""",
    "two-managers-ok-first": _PRE + _A1_OK + """
<urn:p1> a st:Manager ; st:hasAssignment <urn:p#a1> .
<urn:p2> a st:Manager .
""",
    "two-managers-bad-first": _PRE + _A1_OK + """
<urn:p2> a st:Manager .
<urn:p1> a st:Manager ; st:hasAssignment <urn:p#a1> .
""",
    "no-assignment": _PRE + _A1_OK + """
<urn:p> a st:Manager .
<urn:other> st:hasAssignment <urn:p#a1> .
""",
    "two-assignments-ok-first": _PRE + _A1_OK + _A2_BAD + """
<urn:p> a st:Manager ; st:hasAssignment <urn:p#a1> , <urn:p#a2> .
""",
    "two-assignments-bad-first": _PRE + _A1_OK + _A2_BAD + """
<urn:p> a st:Manager ; st:hasAssignment <urn:p#a2> , <urn:p#a1> .
""",
    "no-assigns": _PRE + """
<urn:p> a st:Manager ; st:hasAssignment <urn:p#a1> .
<urn:p#a1> ex:seeAlso ab:PersonContainerTree ;
    st:manages <https://pod.vardeman.me/vault/contacts/Person/> .
<urn:q#a9> st:assigns ab:PersonContainerTree .
""",
    "no-manages": _PRE + """
<urn:p> a st:Manager ; st:hasAssignment <urn:p#a1> .
<urn:p#a1> ex:seeAlso <https://pod.vardeman.me/vault/contacts/Person/> ;
    st:assigns ab:PersonContainerTree .
<urn:q#a9> st:manages <https://pod.vardeman.me/vault/contacts/Person/> .
""",
    "wrong-assigns": _PRE + _A2_BAD + """
<urn:p> a st:Manager ; st:hasAssignment <urn:p#a2> .
""",
    "assignment-empty-literal": _PRE + """
<urn:p> a st:Manager ; st:hasAssignment "" .
""",
    "assignment-zero-literal": _PRE + """
<urn:p> a st:Manager ; st:hasAssignment 0 .
""",
}


def _with_person(text):
    def case():
        graphs = _manager_graphs()
        graphs["person"] = Graph().parse(data=text, format="turtle")
        return (graphs,), {}
    return case


VERDICT = run_pair(
    __file__,
    entry='test_addressbook_managers_assign_container_trees_and_name_their_container',
    calls=[lambda: ((_manager_graphs(),), {}),
           lambda: ((_real_graphs(),), {})]
    + [_with_person(text) for text in PERSON.values()],
)
