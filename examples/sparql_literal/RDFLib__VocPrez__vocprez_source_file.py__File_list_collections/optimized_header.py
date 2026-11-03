# Extracted from RDFLib/VocPrez@ce3c0ea42f : vocprez/source/file.py
# region: File.list_collections (lines 160-169, stratum sparql_literal)
# licence of the source repository: see meta.json
def list_collections(self):
    return list(map(tuple, self.gr.query("""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?c ?l
        WHERE {
          ?c a skos:Concept .
          ?c rdfs:label ?l .
        }""")))
