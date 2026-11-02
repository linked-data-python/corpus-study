"""Driver for PropertyInstantiator._create_property_blank_node.

`self` is a stand-in with the four members the region uses: _aspect_graph
(the fixture), _samm (the real SAMM class, version 2.1.0), _get_child (the
body of InstantiatorBase._get_child @5ca56eb51c, with the element factory
replaced by a tuple that records its arguments) and _get_base_attributes
(records its argument).  DefaultProperty keeps its arguments, so what the
region reads and passes on is compared attribute by attribute.

Each call selects its element_node in the freshly parsed fixture by its
ex:tag (blank node identifiers differ between the two sides' parses).
"""
from pathlib import Path

from rdflib import BNode, Literal, Namespace, URIRef

from esmf_context import SAMM
from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")


class Instantiator:
    def __init__(self, graph):
        self._aspect_graph = graph
        self._samm = SAMM("2.1.0")

    def _get_child(self, parent_subject, child_predicate, required=False):
        child_subject = self._aspect_graph.value(subject=parent_subject, predicate=child_predicate)
        if child_subject is None and required:
            raise ValueError(f"Child {child_predicate} is required for element {parent_subject}")
        elif child_subject is None:
            return None
        elif isinstance(child_subject, Literal):
            return child_subject.toPython()
        else:
            return ("element", child_subject, parent_subject, child_predicate)

    def _get_base_attributes(self, node):
        return ("base-attributes", node)


def tagged(graph, tag):
    return next(graph.subjects(EX.tag, Literal(tag)))


def relabelled(graph, node, label):
    """The blank node under a fixed identifier, in every triple of the graph.

    The ValueError of a missing property names the node, and the two sides
    parse the fixture into different blank node identifiers: the cases that
    raise on a blank node give it the same name on both sides.
    """
    fixed = BNode(label)
    for s, p, o in list(graph):
        if node in (s, o):
            graph.remove((s, p, o))
            graph.add((fixed if s == node else s, p, fixed if o == node else o))
    return fixed


def call(tag=None, node=None, label=None):
    def make():
        graph = fixture_graph(FIXTURE)
        element = node if node is not None else tagged(graph, tag)
        if label is not None:
            element = relabelled(graph, element, label)
        return (Instantiator(graph), element), {}
    return make


CALLS = [
    call("full"),
    call("minimal"),
    call("optional-only"),
    call("payload-only"),
    call("nested"),
    call("two-values"),
    call("no-characteristic"),
    call("literal-property"),
    call("other"),
    call("no-property", label="noproperty"),   # only the OLD version's terms: raises
    call("reverse", label="reverse"),          # a blank node that is only an object: raises
    call(node=EX.emptyprop),                   # falsy property node (empty literal): raises
    call(node=EX.unknown),                     # not in the graph: raises
]

VERDICT = run_pair(__file__, entry="_create_property_blank_node", fixture="fixture.ttl", calls=CALLS)
