# Extracted from mpsonntag/snippets@164fac3966 : python/odml/scripts/rdf_crcns_query.py
# region: <module> (lines 32-32, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
NAMESPACE_MAP = {"odml": Namespace(ODML_NS), "rdf": RDF, "rdfs": RDFS}
q_string = """
SELECT * WHERE {
  ?p rdf:type odml:Property .
  ?p odml:hasName ?prop_name .
  ?p odml:hasValue ?v .
  ?v ?pred ?value .
  FILTER (strstarts(str(?pred), str(rdf:_)))
}"""

curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)
