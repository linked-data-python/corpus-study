# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_onts_props (lines 509-517, band high)
# licence of the source repository: see meta.json
from collections import defaultdict
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
from pylode.rdf_elements import (
    AGENT_PROPS,
    OBJECT_PROPERTY_SUBCLASSES,
    ONTOLOGY_PROPS,
    ONTPUB,
)

def get_onts_props(self) -> dict[str, list]:
    # get all ONT_PROPS props and their (multiple) values
    this_onts_props = defaultdict(list)
    for s_ in self.graph.subjects(predicate=RDF.type, object=PROF.Profile):
        for p_, o in self.graph.predicate_objects(s_):
            if p_ in ONTOLOGY_PROPS:
                this_onts_props[p_].append(o)

    return this_onts_props
