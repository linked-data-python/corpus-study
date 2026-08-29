# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/nodesetparser.py
# region: NodesetParser.get_all_references (lines 337-340, stratum sparql_literal)
# licence of the source repository: see meta.json
query_references = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?id ?namespaceUri ?name
WHERE {
  ?subclass rdfs:subPropertyOf* <http://opcfoundation.org/UA/References> .
  ?node base:definesType ?subclass .
  ?node base:hasNodeId ?id .
  ?node base:hasNamespace ?ns .
  ?ns base:hasUri ?namespaceUri .
  ?node base:hasBrowseName ?name .
}
"""

def get_all_references(self):
    query_result = self.ig.query(query_references, initNs=self.rdf_ns)
    for id, namespace_uri, name in query_result:
        self.known_references.append((id, namespace_uri, name))
