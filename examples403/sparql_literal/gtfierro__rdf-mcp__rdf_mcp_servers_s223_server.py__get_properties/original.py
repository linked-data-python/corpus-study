# Extracted from gtfierro/rdf-mcp@b6aa50fd53 : rdf_mcp/servers/s223_server.py
# region: get_properties (lines 42-56, stratum sparql_literal)
# licence of the source repository: see meta.json
mcp = FastMCP("GraphDemo", dependencies=["rdflib", "oxrdflib"])
ontology = Graph().parse("https://open223.info/223p.ttl")

@mcp.tool()
def get_properties() -> list[str]:
    """Get all properties in the 223P ontology graph"""
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX s223: <http://data.ashrae.org/standard223#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?class WHERE {
        ?class a rdf:Property .
    }"""
    results = ontology.query(query)
    # return [str(row[0]).split('#')[-1] for row in results]
    r = [str(row[0]).split("#")[-1] for row in results]
    return r
