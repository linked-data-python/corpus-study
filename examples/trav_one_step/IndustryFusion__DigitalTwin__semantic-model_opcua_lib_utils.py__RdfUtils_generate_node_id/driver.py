"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_lib_utils.py__RdfUtils_generate_node_id.

This region READS a graph (six one-step traversals) and returns a computed
value, so the oracle is not isomorphism but the equality of the values both
versions produce from the same input graph (design record corpus/405),
despite meta.json's auto-detected default of "isomorphism" -- see
translation_notes. `fixture.ttl` is parsed fresh for each side.

generate_node_id(self, graph, rootentity, node, id) needs more than the
graph (and reads only `self.basens`, an rdflib Namespace), so `calls=`
supplies (self, graph, rootentity, node, id) explicitly. `self` is a bare
object exposing just `.basens`, matching what the extracted function's body
actually touches.

Five calls, shaped after the source repository's own
semantic-model/opcua/tests/test_libutils.py::test_generate_node_id:

1. node/root share a namespace (is_entityns ends up True) and a non-empty,
   non-IRI id: the id is prepended.
2. id=None: no instance-id prefix is used regardless of is_entityns.
3. node/root do NOT share a namespace (is_entityns ends up False): a
   non-empty id is ignored.
4. node/root share a namespace again, and id is itself a full IRI
   (http://...): nodeId_to_iri's is_iri(instance_id) branch fires.
5. the zero-solution case: node/root carry none of hasNodeId,
   hasIdentifierType or hasNamespace, so all six one-step reads come back
   empty and fall back to 'unknown' on both sides.

ex:decoy and ex:node1's base:hasOldNodeId in fixture.ttl are the
neighbourhood that must not leak into any of the five results: same
predicates (or a look-alike predicate name), different/unrelated subjects.

Repair 2026-10-30 (triage: equivalence-doubt, weak-oracle):

* ex:root1, ex:ns1, ex:ns3node, ex:ns3root, ex:ns4 now carry another
  predicate BEFORE the one read (same subject, other predicate): a read of
  rootentity/hasNamespace, rootns/hasUri or ns/hasUri whose predicate were
  widened takes it, and the result changes (calls 1, 3, 4).
* 6. several values: two hasNodeId, two hasUri -- the first inserted wins
  on both sides.
* 7, 8. falsy values that are present ("" and 0): next(..., 'unknown')
  keeps them, so must the translation (a truth test would not).
* 9. the node's namespace is a blank node; the root has no namespace.
* 10-12. rootentity and/or node is None.  The repository reaches it:
  owl2instances.py:831-832 sets rootentities = [next(g.subjects(RDF.type,
  rootinstancetype), None)] when the type has no instance, then :838-840
  calls scan_entity(None, ...), whose first line (:455) is
  generate_node_id(g, rootentity, node, id) with both None; the scan then
  recurses into real nodes with the module-level rootentity still None
  (:455, :499, :666).  graph.objects(None, p) is a WILDCARD: the original
  takes the first value of p anywhere in the graph, and the node id it
  builds goes into the JSON-LD output (instance['id']).  Call 12 (a node
  with rootentity present) is not reached by the repository but costs
  nothing.
"""
from pathlib import Path
from types import SimpleNamespace

from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

EX = Namespace("http://example.org/")
BASENS = Namespace("http://example.org/base/")
SELF = SimpleNamespace(basens=BASENS)  # the region's body reads only self.basens


def call_same_namespace_id_prepended():
    return ((SELF, fixture_graph(FIXTURE), EX.root1, EX.node1, "testID:"), {})


def call_id_none():
    return ((SELF, fixture_graph(FIXTURE), EX.root2, EX.node2, None), {})


def call_different_namespace_id_ignored():
    return ((SELF, fixture_graph(FIXTURE), EX.root3, EX.node3, "whatever"), {})


def call_id_is_full_iri():
    return ((SELF, fixture_graph(FIXTURE), EX.root4, EX.node4, "http://whatever:"), {})


def call_zero_solutions():
    return ((SELF, fixture_graph(FIXTURE), EX.root5, EX.node5, "z"), {})


def call_several_values():
    return ((SELF, fixture_graph(FIXTURE), EX.root6, EX.node6, "six:"), {})


def call_falsy_strings():
    return ((SELF, fixture_graph(FIXTURE), EX.root7, EX.node7, "seven:"), {})


def call_falsy_integer():
    return ((SELF, fixture_graph(FIXTURE), EX.root8, EX.node8, "eight:"), {})


def call_blank_namespace_no_root_namespace():
    return ((SELF, fixture_graph(FIXTURE), EX.root9, EX.node9, "nine:"), {})


def call_root_and_node_none():
    """scan_entity(None, ...) -> generate_node_id(g, None, None, id)."""
    return ((SELF, fixture_graph(FIXTURE), None, None, "x"), {})


def call_root_none():
    """The recursion under rootentity=None: a real node."""
    return ((SELF, fixture_graph(FIXTURE), None, EX.node1, "testID:"), {})


def call_node_none():
    return ((SELF, fixture_graph(FIXTURE), EX.root1, None, "testID:"), {})


VERDICT = run_pair(
    __file__,
    entry='generate_node_id',
    fixture="fixture.ttl",
    calls=[call_same_namespace_id_prepended, call_id_none,
           call_different_namespace_id_ignored, call_id_is_full_iri,
           call_zero_solutions,
           # repair 2026-10-30
           call_several_values, call_falsy_strings, call_falsy_integer,
           call_blank_namespace_no_root_namespace,
           call_root_and_node_none, call_root_none, call_node_none],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
