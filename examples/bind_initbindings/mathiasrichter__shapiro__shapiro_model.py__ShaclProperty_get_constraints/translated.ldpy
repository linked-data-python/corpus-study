# Extracted from mathiasrichter/shapiro@3954ef2148 : shapiro_model.py
# region: ShaclProperty.get_constraints (lines 645-677, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode
from typing import Tuple, List
from urllib.parse import urlparse

def get_constraints(self) -> List[ShaclConstraint]:
    props = []
    result = self.graph.query( # get prop and potential super-properties
        self.TRANSITIVE_SUPERPROPERTIES_QUERY, initBindings={"subproperty": self.get_node(self.iri)}
    )
    for r in result:
        props.append(str(r.superproperty))
    result = []
    for p in props: # get all constraints including those from super-properties
        result += self.graph.query(
            self.SHACL_CONSTRAINTS_QUERY, initBindings={"property": self.get_node(str(p))}
        )
    constraints = []
    for r in result:
        p = str(r.property)
        c = str(r.constraint)
        v = str(r.value)
        is_enum = False
        if c.endswith("shacl#in"):
            is_enum = True
            v = []
            if urlparse(p).scheme == "":  #  if p is a blank node
                prop = BNode(self.iri)
            else:
                prop = URIRef(self.iri)
            items = self.graph.query(
                self.SHACL_IN_QUERY, initBindings={"source": prop}
            )
            for i in items:
                v.append(i.item)
        constraints.append(ShaclConstraint(self, c, v, is_enum))
    constraints.sort(key=lambda c: c.constraint_iri)
    return constraints
