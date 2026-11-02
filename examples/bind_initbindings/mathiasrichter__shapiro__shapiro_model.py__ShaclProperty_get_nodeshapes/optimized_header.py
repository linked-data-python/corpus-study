# Extracted from mathiasrichter/shapiro@3954ef2148 : shapiro_model.py
# region: ShaclProperty.get_nodeshapes (lines 824-835, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode
from typing import List
from urllib.parse import urlparse

# Context shim: NodeShape lived elsewhere in shapiro_model.py; restoring the
# binding so the region executes standalone (see shim.py).
from shim import NodeShape

def get_nodeshapes(self) -> List[NodeShape]:
    #  if this is a blank node
    prop = BNode(self.iri) if urlparse(self.iri).scheme == "" else URIRef(self.iri)
    shapes = [NodeShape(str(r.shape), self.graph)
              for r in self.graph.query(self.SHAPE_QUERY, initBindings={"property": prop})]
    return sorted(shapes, key=lambda s: s.label)
