# Extracted from mathiasrichter/shapiro@3954ef2148 : shapiro_model.py
# region: NodeShape.get_shacl_properties (lines 409-417, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode
from typing import Tuple, List

def get_shacl_properties(self) -> List["ShaclProperty"]:
    result = self.graph.query(
        self.SHACL_PROP_QUERY, initBindings={"shape": URIRef(self.iri)}
    )
    props = []
    for r in result:
        props.append(ShaclProperty(str(r.shacl_prop), self.graph))
    props.sort(key=lambda p: p.label)
    return props
