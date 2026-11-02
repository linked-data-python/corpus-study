"""Validation driver for EntityResolutionWorkflow.get_keys_for_class.

The region READS a graph and returns the members of the rdf:List that
`owl:hasKey` points to (or None), logging a warning when the list cannot be
read. Oracle: the values (and log records) both versions produce from the
same fixture graph.

Calls (fixture.ttl is parsed afresh for each side; `self` is unused by the
region and passed as None):

* ex:Person   a three-element key list;
* ex:Country  a one-element key list;
* ex:Broken   a cyclic list: Collection iteration raises, the region logs a
              warning and returns None (the log record is compared);
* ex:Weird    a literal as hasKey object: an empty list, not None;
* ex:Company  its key is under ex:hasKey, a neighbour that must NOT match: None;
* ex:Other    no key at all: None.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"
EX = "http://example.org/"


def _case(name):
    def make():
        return (None, fixture_graph(FIXTURE), URIRef(EX + name)), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="get_keys_for_class",
    calls=[_case(n) for n in ("Person", "Country", "Broken", "Weird",
                              "Company", "Other")],
    ordered=True,  # a key list is ordered: its order is the region's value
)
