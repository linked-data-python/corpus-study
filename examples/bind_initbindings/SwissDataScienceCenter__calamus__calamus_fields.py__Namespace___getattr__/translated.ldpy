# Extracted from SwissDataScienceCenter/calamus@c59d6fe968 : calamus/fields.py
# region: Namespace.__getattr__ (lines 92-103, stratum bind_initbindings)
# licence of the source repository: see meta.json
from calamus.utils import ONTOLOGY_QUERY, Proxy, normalize_type, normalize_value

def __getattr__(self, name):
    reference = IRIReference(self, name)

    if self.ontology:
        from rdflib.term import URIRef

        p = URIRef(str(reference))
        qres = self.ontology.query(ONTOLOGY_QUERY, initBindings={"property": p})
        if not next(iter(qres), False):
            raise ValueError(f"Property {name} does not exist in namespace {self.namespace}")

    return reference
