# Extracted from mapsa/blathers@cad7822217 : src/blathers/extract.py
# region: _extract_individuals (lines 293-315, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS

def _extract_individuals(g: Graph, namespace: str) -> list[ExtractedIndividual]:
    """Extract all owl:NamedIndividual subjects in the ontology namespace."""
    individuals = []
    for ind_iri in g.subjects(RDF.type, OWL.NamedIndividual):
        iri_str = str(ind_iri)
        if not iri_str.startswith(namespace):
            continue
        label = _str_or_none(g.value(ind_iri, RDFS.label))
        comment = _str_or_none(g.value(ind_iri, RDFS.comment))
        types = [
            str(t)
            for t in g.objects(ind_iri, RDF.type)
            if isinstance(t, URIRef) and str(t) != str(OWL.NamedIndividual)
        ]
        individuals.append(ExtractedIndividual(
            iri=iri_str,
            local_name=_local_name(iri_str),
            label=label,
            comment=comment,
            types=types,
            nested_sections=_extract_nested_sections(g, ind_iri),
        ))
    return individuals
