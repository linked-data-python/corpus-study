"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_dataservice_tests_server_binding_server.py__parse_rdf_to_mapping.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The function itself calls ``g.parse(rdf_file, format="turtle")`` on its first
argument, so it wants a *path*, not a pre-parsed Graph -- the harness's
default fixture= wiring (which passes a parsed Graph as the sole argument)
does not fit, hence the explicit ``calls=``.  ``binding_ns``/``uaentity_ns``
are supplied directly so the run never takes the
``g.namespace_manager.store.namespace(...)`` fallback branch, which is
unrelated to this region's stratum (ns_def_local: the local ``BASE =
Namespace(base_ns)``) and to the constructions this pair exercises.
"""
from pathlib import Path

from rdfeval.harness import run_pair

_FIXTURE = str(Path(__file__).parent / "fixture.ttl")
_BASE_NS = "http://example.org/vocab#"


def _args():
    return (
        (_FIXTURE, _BASE_NS),
        {"binding_ns": "http://example.org/binding#", "uaentity_ns": "http://example.org/uaentity#"},
    )


VERDICT = run_pair(
    __file__,
    entry='parse_rdf_to_mapping',
    calls=[_args],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
