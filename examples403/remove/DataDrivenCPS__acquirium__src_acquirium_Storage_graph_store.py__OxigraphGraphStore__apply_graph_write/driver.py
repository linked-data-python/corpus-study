"""Validation driver for OxigraphGraphStore._apply_graph_write.

The region empties a target graph, copies an incoming one into it and
propagates the incoming prefix bindings.  It is a method, so each fixture
passes a stand-in `self` holding a fresh query Dataset; the stand-in compares
by the prefixes bound on that dataset, which is the only effect of the region
that graph isomorphism cannot see.

Three calls:
  replace=True   the wildcard remove has work to do (the target is not empty)
  replace=False  the target keeps what it had and the incoming is merged in
  replace=True with an empty incoming — the target ends up empty, which is the
                 case a mistranslated wildcard would get wrong in the other
                 direction
"""
from rdflib import Dataset, Graph

from rdfeval.harness import run_pair

INCOMING = """
@prefix ex:   <http://example.org/> .
@prefix unit: <http://qudt.org/vocab/unit/> .

ex:sensor1 a ex:Sensor ; ex:unit unit:DEG_C ; ex:label "one" .
ex:sensor2 a ex:Sensor ; ex:unit unit:PERCENT .
"""

EXISTING = """
@prefix ex:  <http://example.org/> .
@prefix old: <http://example.org/old/> .

ex:sensor1 ex:label "stale" .
old:gone a old:Thing .
"""


class Store:
    """Stand-in for the enclosing OxigraphGraphStore: the region reads only
    `self.query_dataset`, on whose namespace manager it binds prefixes."""

    def __init__(self):
        self.query_dataset = Dataset()

    def _prefixes(self):
        return sorted((p, str(n)) for p, n in self.query_dataset.namespaces())

    def __eq__(self, other):
        return isinstance(other, Store) and self._prefixes() == other._prefixes()

    def __hash__(self):
        return 0


def _graph(ttl):
    return Graph().parse(data=ttl, format="turtle") if ttl else Graph()


def call(incoming_ttl, existing_ttl, replace):
    return lambda: ((Store(), _graph(incoming_ttl)),
                    {"target": _graph(existing_ttl), "replace": replace})


VERDICT = run_pair(
    __file__,
    entry='_apply_graph_write',
    calls=[
        call(INCOMING, EXISTING, True),
        call(INCOMING, EXISTING, False),
        call(None, EXISTING, True),
    ],
)
