# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/owl2instances.py
# region: <module> (lines 855-859, stratum sparql_literal)
# licence of the source repository: see meta.json
query_subclasses = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

CONSTRUCT {
  ?subclass rdfs:subClassOf ?superclass .
  ?subclass a owl:Class .
  ?superclass a owl:Class .
}
WHERE {
  ?subclass rdfs:subClassOf* <http://opcfoundation.org/UA/BaseObjectType> .
  ?subclass rdfs:subClassOf ?superclass .

  # Ensure both subclasses and superclasses are marked as owl:Class
  {
    ?subclass a owl:Class .
  } UNION {
    ?superclass a owl:Class .
  }
}
"""
opcuans = None  # dito

if entitiesname is not None:
    result = g.query(query_subclasses)
    e.add_subclasses(result)
    e.add_subclasses_recursive(g, opcuans['BaseNodeClass'])
    e.serialize(destination=entitiesname)
