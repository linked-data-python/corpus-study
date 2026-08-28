"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_query___init__.py__Query_get_superclasses.

`get_superclasses` is a pure read on `rdfs:subClassOf`: it drops blank nodes
and ignored classes, then maps each remaining superclass through
`self.get_component_model_class` and sorts by name.  The region was extracted
as a module-level function, so it is called directly with a stand-in `Query`
whose `get_component_model_class` builds the shim's reduced `Class` dataclass
(shared module -> the results compare by value).  One shared instance is used
for `self` so that the harness's argument comparison is meaningful.
"""
import sys

sys.dont_write_bytecode = True  # the shim next to this driver is imported

from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

from supermodel_shim import Class

EX = "https://example.com/ont/"

DATA = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix ex:   <https://example.com/ont/> .

ex:Parcel a owl:Class ;
    rdfs:subClassOf ex:SpatialUnit, ex:Feature, [ a owl:Restriction ] ,
                    <http://www.w3.org/2002/07/owl#Thing> .
ex:Leaf a owl:Class .
"""


class Query:
    """Stands in for the pyLODE Query object that owns the method."""

    def get_component_model_class(self, iri, graph, ignored_classes):
        return Class(iri=iri, name=str(iri).rsplit("/", 1)[-1])


# one shared instance: the two fixture invocations must yield equal arguments
QUERY = Query()


def _graph():
    g = Graph()
    g.parse(data=DATA, format="turtle")
    return g


def with_superclasses():
    return ((QUERY, URIRef(EX + "Parcel"), _graph(),
             [URIRef("http://www.w3.org/2002/07/owl#Thing")]), {})


def without_superclasses():
    return ((QUERY, URIRef(EX + "Leaf"), _graph(), []), {})


VERDICT = run_pair(__file__, entry="get_superclasses",
                   calls=[with_superclasses, without_superclasses])
