# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/ontology.py
# region: _OWLToSHACLConverter._iter_supported_restrictions (lines 1362-1383, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef

def _iter_supported_restrictions(self):
    """
    Yield (base_class, property, restriction_type, value) tuples
    for supported OWL restrictions.
    """
    for r in self.owl_graph.subjects(RDF.type, OWL.Restriction):
        if self.excluded_nodes is not None and r in self.excluded_nodes:
            continue
        prop = self.owl_graph.value(r, OWL.onProperty)
        if prop is None:
            continue
        for restriction_type in (
            OWL.someValuesFrom,
            OWL.hasValue,
            OWL.allValuesFrom,
        ):
            value = self.owl_graph.value(r, restriction_type)
            if value is None:
                continue

            for base_cls in self.owl_graph.subjects(RDFS.subClassOf, r):
                yield base_cls, prop, restriction_type, value
