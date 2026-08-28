# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_ns (lines 659-699, band high)
# licence of the source repository: see meta.json
from rdflib.namespace import (
    DC,
    DCTERMS,
    FOAF,
    ORG,
    OWL,
    PROF,
    PROV,
    QB,
    RDF,
    RDFS,
    SDO,
    SH,
    SKOS,
    VANN,
)

def get_ns(self) -> tuple[str, str]:
    ont = self.graph
    """Gets the default Namespace for the given graph (ontology)"""
    # if this ontology declares a preferred URI, use that
    pref_iri = None
    for s_, o in ont.subject_objects(predicate=VANN.preferredNamespaceUri):
        pref_iri = str(o)

    pref_prefix = None
    for s_, o in ont.subject_objects(predicate=VANN.preferredNamespacePrefix):
        pref_prefix = str(o)
    if pref_prefix is None:
        pref_prefix = ""

    if pref_iri is not None:
        return pref_prefix, pref_iri

    # if not, try the URI of the main object, compared to all prefixes
    else:
        default_iri = None

        for s_ in ont.subjects(predicate=RDF.type, object=PROF.Profile):
            default_iri = str(s_)

        if default_iri is None:
            for s_ in ont.subjects(predicate=RDF.type, object=OWL.Ontology):
                default_iri = str(s_)
                if default_iri is not None:
                    ont.add((s_, RDF.type, PROF.Profile))

        if default_iri is not None:
            prefix = ont.compute_qname(default_iri, True)[0]
            if prefix is not None:
                return prefix, default_iri
        else:
            # can't find either a declared or default namespace
            # so we have an error
            raise Exception(
                "pyLODE can't detect a URI for an owl:Ontology, "
                "a skos:ConceptScheme or a prof:Profile"
            )
