"""Validation driver for
aigora-de__rdf-construct__src_rdf_construct_shacl_converters.py__CardinalityConverter_convert_for_class.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`convert_for_class` is a method (`self, cls, source_graph, config`); the
region's own body never touches `config`, so `None` stands in for it.  `self`
only needs the `_is_datatype` override the region calls -- see
context_shim.py.  A single `_RECEIVER` instance is reused for every call on
both sides: it holds no state, so identity equality is exactly the right
comparison (a fresh instance per side would fail `_compare_value`'s default
`==`, which is object identity here, for no reason connected to translation
correctness).

Three calls: `ex:Widget`, which has ten matching restrictions exercising every
branch plus four non-matching neighbours (see fixture.ttl); `ex:Gadget`,
which has no restrictions at all -- the zero-solution case, returning `[]`
on both sides; and `ex:Thing` (added by the 2026-10-30 repair), which carries
what the first two do not reach:

- a restriction with TWO owl:onProperty: `value()` takes one, so the original
  builds one constraint where a join absorbing onProperty builds two;
- an owl:Restriction named by an IRI, and one whose onProperty is an
  anonymous inverse property: each is dropped by exactly one isinstance guard
  (BNode, URIRef), so removing either guard changes the result;
- `owl:cardinality 0` alone: `if exact:` is false on a zero literal, so no
  constraint -- `if exact is not None:` would add one;
- several values for someValuesFrom and onClass: `.first()` must pick the
  value `value()` picks;
- one neighbour per bound term of the restriction motifs (another predicate
  than rdfs:subClassOf, than rdf:type, than owl:onProperty; another class than
  owl:Restriction) and an owl:hasValue-only restriction: each kills the mutant
  that widens that term to a variable.
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import run_pair, fixture_graph
from context_shim import CardinalityConverter

EX = Namespace("http://example.org/")
FIXTURE = Path(__file__).parent / "fixture.ttl"
_RECEIVER = CardinalityConverter()


def _call(cls_local):
    def make():
        return (_RECEIVER, EX[cls_local], fixture_graph(FIXTURE), None), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='convert_for_class',
    calls=[_call("Widget"), _call("Gadget"), _call("Thing")],
    fixture="fixture.ttl",
)
