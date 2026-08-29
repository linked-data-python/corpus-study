"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_query_property_shape.py__get_property_by_property_shape.

This region READS a graph: `name = ... or profile_graph.value(property_shape,
SH.name) or ...`, extracted as a bare STATEMENT (not a function) from inside
`get_property_by_property_shape`.  The missing bindings -- `kwargs`,
`profile_graph`, `property_shape`, `sh_path`, `db` -- are restored as
parameters of a wrapping function `compute_name` (see original.py /
translated.ldpy).  That wrapper is also what makes `name` observable at all:
`run_pair`'s module-state path (entry=None) only compares rdflib Graphs and
stdout, and `profile_graph` here is read-only, so comparing it would be
vacuous -- it is identical on both sides by construction, regardless of
whether `.value()` was translated correctly.  entry="compute_name" compares
the actual return value instead, which is the point of the region.

`fixture.ttl` is `profile_graph`.  Two calls exercise the two branches of the
`or` chain that this statement's stratum (trav_single_value) is about:
  * with_sh_name    -- `.value()`/`m{ }.first()` finds ex:hasName's sh:name
                       directly (one of several sh:name solutions in the
                       graph);
  * without_sh_name -- ex:noName has no sh:name, so `.value()`/`.first()`
                       both answer None (the zero-solution case) and the
                       statement falls through to get_name(sh_path, ...),
                       itself reading ex:pathNode's rdfs:label.
Neither call ever reads ex:unrelated's sh:name (the neighbourhood).
"""
from rdflib import Dataset, URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
HAS_NAME = URIRef("http://example.org/shapes/hasName")
NO_NAME = URIRef("http://example.org/shapes/noName")
PATH_NODE = URIRef("http://example.org/shapes/pathNode")


def with_sh_name():
    return (({}, fixture_graph(FIXTURE), HAS_NAME, None, Dataset()), {})


def without_sh_name():
    return (({}, fixture_graph(FIXTURE), NO_NAME, PATH_NODE, Dataset()), {})


VERDICT = run_pair(
    __file__,
    entry='compute_name',
    fixture=FIXTURE,
    calls=[with_sh_name, without_sh_name],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
