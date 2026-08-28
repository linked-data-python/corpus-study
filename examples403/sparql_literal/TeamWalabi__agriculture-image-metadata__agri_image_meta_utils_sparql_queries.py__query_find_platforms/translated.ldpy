# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : agri_image_meta/utils/sparql_queries.py
# region: query_find_platforms (lines 37-50, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph

def query_find_platforms(g: Graph):
    query = """
    PREFIX agimage: <https://w3id.org/agri-image/>
    SELECT ?platform ?platformName
    WHERE {
        ?platform a agimage:Platform ;
            <https://w3id.org/agri-image/platformName> ?platformName .
    }
    """
    print("\n🤖 Query: Find all platforms")
    results = g.query(query)
    for row in results:
        print(f"   - {row.platformName}")
    return results
