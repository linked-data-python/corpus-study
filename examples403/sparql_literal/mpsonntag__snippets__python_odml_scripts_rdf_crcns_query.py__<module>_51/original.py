# Extracted from mpsonntag/snippets@164fac3966 : python/odml/scripts/rdf_crcns_query.py
# region: <module> (lines 51-62, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
NAMESPACE_MAP = {"odml": Namespace(ODML_NS), "rdf": RDF, "rdfs": RDFS}

q = prepareQuery("""
SELECT * WHERE {
    ?d a odml:Document .
    ?d odml:hasSection* ?doisec .
    ?doisec a odml:Identifier .
    ?doisec odml:hasName ?doiSecName .
    ?doisec odml:hasProperty ?doiprop .
    ?doiprop odml:hasName "identifier" .
    ?doiprop odml:hasValue ?urival .
    ?urival ?pred ?uri .
    FILTER (strstarts(str(?pred), str(rdf:_)))
}""", initNs=NAMESPACE_MAP)
