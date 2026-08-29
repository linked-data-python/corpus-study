# Extracted from mathiasrichter/shapiro@3954ef2148 : shapiro_model.py
# region: ShaclProperty.get_nodeshapes (lines 824-835, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode
from typing import Tuple, List
from urllib.parse import urlparse

def get_nodeshapes(self) -> List[NodeShape]:
    prop = None
    if urlparse(self.iri).scheme == "":  #  if this is a blank node
        prop = BNode(self.iri)
    else:
        prop = URIRef(self.iri)
    result = self.graph.query(self.SHAPE_QUERY, initBindings={"property": prop})
    shapes = []
    for r in result:
        shapes.append(NodeShape(str(r.shape), self.graph))
    shapes.sort(key=lambda s: s.label)
    return shapes
