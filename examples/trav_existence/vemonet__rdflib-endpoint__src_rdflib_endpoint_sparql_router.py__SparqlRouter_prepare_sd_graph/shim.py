# Context shim (see meta.json): stand-in for the surrounding
# SparqlRouter.prepare_sd_graph method body from
# vemonet/rdflib-endpoint@1427c77829, so the region executes outside the
# package (`rdflib_endpoint` is not installed here). `SD` and `FORMATS` are
# the real, standard W3C vocabularies rdflib_endpoint.utils binds them to
# (SPARQL 1.1 Service Description, and the W3C formats namespace used to
# name serialisation formats). `self` stands for the SparqlRouter instance:
# only the one attribute the region touches, `service_description`, is
# reproduced. `sd_subj` stands for the local variable bound earlier in the
# method to the graph's service-description subject.
# Identical bindings for both representations.
from rdflib import Graph, Namespace, URIRef

SD = Namespace("http://www.w3.org/ns/sparql-service-description#")
FORMATS = Namespace("http://www.w3.org/ns/formats/")


class _Self:
    def __init__(self) -> None:
        self.service_description = Graph()


self = _Self()
sd_subj = URIRef("http://example.org/sparql")
