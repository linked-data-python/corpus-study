"""Validation driver for AttachPropertyFromTargetToSource.transform.

The region is a method that READS the graph with a SPARQL query and then
REWRITES it in place, so the oracle of design record corpus/405 applies twice
over: `fixture.ttl` is parsed fresh for each side, and the harness compares
both the return value (None) and the mutated graph, by isomorphism.

`self` is a stand-in for the enclosing transformer: it carries the two query
templates verbatim from the source file and the six constructor attributes the
region reads.  It compares by configuration, since `transform` does not touch
it.

Four calls cover the four branches the region has:
  A / keep   use case A, delete_target_node=False  — the two per-solution writes
  A / delete use case A, delete_target_node=True   — plus the two wildcard removes
  B / delete use case B, delete_target_node=True   — the computed predicate
  B / convert use case B, convert_literal_to_uri=True — the object as an IRI,
             on ex:codeValue, whose values have no space (namespace[value] of
             "Target Value" is a URIRef rdflib refuses to serialise)

The namespace is `http://example.org/neat_/` and not neat's own
DEFAULT_NAMESPACE because `as_neat_compliant_uri` calls rdflib's `split_uri`
with `split_start="#_"`, which only ever splits at an underscore: a namespace
without one raises ValueError upstream, before any of the code under
translation runs.
"""
from pathlib import Path

from rdflib import Namespace, URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")


class Transformer:
    """Stand-in for AttachPropertyFromTargetToSource: the templates and the
    attributes `transform` reads, copied from the source class."""

    _query_template_use_case_a: str = """
    SELECT ?sourceNode ?sourceProperty ?targetNode ?newSourceProperty ?newSourcePropertyValue WHERE {{
        ?sourceNode ?sourceProperty ?targetNode .
        BIND( <{target_property}> as ?newSourceProperty ) .
        ?targetNode a <{target_node_type}> .
        ?targetNode <{target_property}> ?newSourcePropertyValue . }}"""

    _query_template_use_case_b: str = """
    SELECT ?sourceNode ?sourceProperty ?targetNode ?newSourceProperty ?newSourcePropertyValue WHERE {{
        ?sourceNode ?sourceProperty ?targetNode .
        ?targetNode a <{target_node_type}> .
        ?targetNode <{target_property_holding_new_property_name}> ?newSourceProperty .
        ?targetNode <{target_property}> ?newSourcePropertyValue . }}"""

    def __init__(
        self,
        target_node_type: URIRef,
        target_property: URIRef,
        target_property_holding_new_property: URIRef | None = None,
        delete_target_node: bool = False,
        convert_literal_to_uri: bool = False,
        namespace: Namespace | None = None,
    ):
        self.target_node_type = target_node_type
        self.target_property = target_property
        self.delete_target_node = delete_target_node
        self.target_property_holding_new_property = target_property_holding_new_property
        self.convert_literal_to_uri = convert_literal_to_uri
        self.namespace = namespace or Namespace("http://example.org/neat_/")

    def _config(self):
        return (self.target_node_type, self.target_property,
                self.target_property_holding_new_property,
                self.delete_target_node, self.convert_literal_to_uri,
                str(self.namespace))

    def __eq__(self, other):
        return isinstance(other, Transformer) and self._config() == other._config()

    def __hash__(self):
        return 0


def call(target_property=EX.propertyWhichValueWeWant, **kwargs):
    return lambda: ((Transformer(EX.TargetType, target_property, **kwargs),
                     fixture_graph(FIXTURE)), {})


VERDICT = run_pair(
    __file__,
    entry='transform',
    fixture="fixture.ttl",
    calls=[
        call(),                                                  # A, keep
        call(delete_target_node=True),                           # A, delete
        call(target_property_holding_new_property=EX.propertyWhichValueWeMightWantAsNameForNewProperty,
             delete_target_node=True),                           # B, delete
        call(target_property=EX.codeValue,
             target_property_holding_new_property=EX.propertyWhichValueWeMightWantAsNameForNewProperty,
             convert_literal_to_uri=True),                       # B, convert
    ],
)
