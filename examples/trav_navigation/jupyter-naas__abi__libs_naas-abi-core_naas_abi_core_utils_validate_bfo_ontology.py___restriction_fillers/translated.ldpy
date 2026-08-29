# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py
# region: _restriction_fillers (lines 150-160, stratum trav_navigation)
# licence of the source repository: see meta.json
def _restriction_fillers(g: Graph, cls: URIRef) -> set[URIRef]:
    fillers: set[URIRef] = set()
    for parent in g.objects(cls, RDFS.subClassOf):
        if isinstance(parent, BNode):
            rdf_type = g.value(parent, RDF.type)
            if rdf_type == OWL.Restriction:
                for pred in (OWL.allValuesFrom, OWL.someValuesFrom):
                    filler = g.value(parent, pred)
                    if isinstance(filler, URIRef):
                        fillers.add(filler)
    return fillers
