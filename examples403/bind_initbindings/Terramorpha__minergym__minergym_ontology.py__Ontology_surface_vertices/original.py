# Extracted from Terramorpha/minergym@1d2d586bb1 : minergym/ontology.py
# region: Ontology.surface_vertices (lines 137-153, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.term import Node
Point: TypeAlias = tuple[float, float, float]

def surface_vertices(self, surface: Node) -> list[Point]:
    """Return the vertices of a surface."""
    q = """# -*- mode: sparql -*-

SELECT ?x ?y ?z
WHERE {
  ?surface idf:vertices ?vertices .
  ?vertices rdf:rest*/rdf:first ?vertex .

  ?vertex idf:vertex_x_coordinate ?x .
  ?vertex idf:vertex_y_coordinate ?y .
  ?vertex idf:vertex_z_coordinate ?z .
}"""
    return [
        (x.toPython(), y.toPython(), z.toPython())
        for (x, y, z) in self.rdf.query(q, initBindings={"surface": surface})
    ]
