# Extracted from OpenEnergyPlatform/oeplatform@ff28ef6390 : factsheet/helper.py
# region: _division_members (lines 247-254, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, Graph, URIRef
from context_shim import _label  # see meta.json: restores the missing helper
SECTOR_MEMBERS_QUERY = """
PREFIX oeo:  <https://openenergyplatform.org/ontology/oeo/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?sector WHERE {
  {
    ?sector oeo:OEO_00000504 ?division .
  }
  UNION
  {
    ?sector rdf:type ?restriction .
    ?restriction a owl:Restriction ;
                 owl:onProperty oeo:OEO_00000504 ;
                 owl:someValuesFrom ?division .
  }
  UNION
  {
    ?sector rdfs:subClassOf ?restriction2 .
    ?restriction2 a owl:Restriction ;
                  owl:onProperty oeo:OEO_00000504 ;
                  owl:someValuesFrom ?division .
  }
  FILTER (?sector != ?division)
}
"""

def _division_members(g: Graph, division: URIRef):
    """The sectors defined by ``division``, sorted by label (both patterns)."""
    members = {
        row[0]
        for row in g.query(SECTOR_MEMBERS_QUERY, initBindings={"division": division})
        if isinstance(row[0], URIRef)
    }
    return sorted(members, key=lambda node: (_label(g, node) or str(node)).lower())
