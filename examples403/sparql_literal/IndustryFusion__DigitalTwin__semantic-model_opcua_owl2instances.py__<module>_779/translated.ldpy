# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/owl2instances.py
# region: <module> (lines 779-779, stratum sparql_literal)
# licence of the source repository: see meta.json
query_namespaces = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?uri ?prefix ?ns WHERE {
    ?ns rdf:type base:Namespace .
    ?ns base:hasUri ?uri .
    ?ns base:hasPrefix ?prefix .
}
"""
basens = None  # Will be defined by the imported ontologies
opcuans = None  # dito

result = g.query(query_namespaces, initNs={'base': basens, 'opcua': opcuans})
