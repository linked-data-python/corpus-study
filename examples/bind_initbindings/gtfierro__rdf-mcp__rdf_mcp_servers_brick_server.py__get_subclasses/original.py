# Extracted from gtfierro/rdf-mcp@b6aa50fd53 : rdf_mcp/servers/brick_server.py
# region: get_subclasses (lines 68-82, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, BRICK, RDFS
mcp = FastMCP("GraphDemo", dependencies=["rdflib", "oxrdflib"])
ontology = Graph().parse("https://brickschema.org/schema/1.4/Brick.ttl")

@mcp.tool()
def get_subclasses(parent_class: str) -> list[str]:
    """Get all classes that inherit from a specific parent class in the Brick ontology"""
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT DISTINCT ?subclass WHERE {
        ?subclass rdfs:subClassOf* ?parent .
        ?subclass a owl:Class .
        FILTER NOT EXISTS { ?subclass owl:deprecated true }
        FILTER (?subclass != ?parent)
    }"""
    results = ontology.query(query, initBindings={"parent": BRICK[parent_class]})
    return [str(row[0]).split("#")[-1] for row in results]
