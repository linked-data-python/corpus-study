# Extracted from mathiasrichter/shapiro@3954ef2148 : shapiro_model.py
# region: RdfProperty.get_shacl_properties (lines 352-360, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode
from typing import Tuple, List

def get_shacl_properties(self) -> List[str]:
    result = self.graph.query(
        self.SHACL_PROP_QUERY, initBindings={"property": URIRef(self.iri)}
    )
    props = []
    for r in result:
        props.append(ShaclProperty(str(r.shacl_prop), self.graph))
    props.sort(key=lambda p: p.label)
    return props
