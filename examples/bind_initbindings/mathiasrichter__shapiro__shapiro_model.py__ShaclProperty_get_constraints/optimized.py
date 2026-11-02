# Extracted from mathiasrichter/shapiro@3954ef2148 : shapiro_model.py
# region: ShaclProperty.get_constraints (lines 645-677, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode
from typing import Tuple, List
from urllib.parse import urlparse

# Context shim: ShaclConstraint (and, for the original, the class attributes
# it reads through `self`) lived elsewhere in shapiro_model.py (see shim.py).
from shim import ShaclConstraint

def get_constraints(self) -> List[ShaclConstraint]:
    # get prop and potential super-properties
    props = [str(r.superproperty) for r in self.graph.query(
        self.TRANSITIVE_SUPERPROPERTIES_QUERY,
        initBindings={"subproperty": self.get_node(self.iri)})]
    constraints = []
    for p in props: # get all constraints including those from super-properties
        for r in self.graph.query(self.SHACL_CONSTRAINTS_QUERY,
                                  initBindings={"property": self.get_node(p)}):
            c = str(r.constraint)
            v = str(r.value)
            is_enum = c.endswith("shacl#in")
            if is_enum:
                #  if p is a blank node
                prop = BNode(self.iri) if urlparse(p).scheme == "" else URIRef(self.iri)
                v = [i.item for i in self.graph.query(
                    self.SHACL_IN_QUERY, initBindings={"source": prop})]
            constraints.append(ShaclConstraint(self, c, v, is_enum))
    constraints.sort(key=lambda c: c.constraint_iri)
    return constraints
