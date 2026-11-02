"""Validation driver for Dewberry__blobfish__blobfish_ckan_query.py__SpatialRDFHandler_identify_rfc_datasets.

In the repository the method raises NotImplementedError on its first line
("geosparql functions which are not implemented in the SPARQL processor for
RDFLib"): everything after it -- the query and its initBindings -- is
unreachable. What the original shows, and what the translation must
reproduce, is therefore that raise (type and message), for any coordinates;
the harness compares a raise like a value. The graph handed in through
`self` is also compared afterwards, so a translation that touched it
(e.g. by running the query before the raise) would be caught.

The unreachable query itself is not exercised here, and cannot be by any
driver; its translation was checked apart (see meta.json).
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair
from context_shim import SpatialRDFHandler

EX = "http://example.org/"


def _handler():
    h = SpatialRDFHandler()
    h.graph.add((URIRef(EX + "rfc1"), URIRef(EX + "p"), Literal("kept")))
    return h


def _call(x, y):
    return lambda: ((_handler(), x, y), {})


VERDICT = run_pair(
    __file__,
    entry="identify_rfc_datasets",
    calls=[_call(-77.03, 38.89), _call(0.0, 0.0)],
)
