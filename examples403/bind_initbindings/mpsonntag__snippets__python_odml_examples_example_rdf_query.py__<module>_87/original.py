# Extracted from mpsonntag/snippets@164fac3966 : python/odml/examples/example_rdf_query.py
# region: <module> (lines 87-108, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
NAMESPACE_MAP = {"odml": Namespace(ODML_NS), "rdf": RDF, "rdfs": RDFS}

q = prepareQuery("""SELECT * 
             WHERE { 
                ?d a odml:Document . 
                ?d odml:hasSection* ?s .
                ?s a odml:Section . 
                ?s odml:hasType ?t . 
                ?s odml:hasName ?secname . 
                { SELECT ?dataSecName ?uri
                   WHERE {
                   ?d odml:hasSection ?datasec .
                   ?datasec odml:hasType "DataReference" .
                   ?datasec odml:hasName ?dataSecName .
                   ?datasec odml:hasProperty ?uriprop .
                   ?uriprop odml:hasName ?nameValue .
                   ?uriprop odml:hasValue ?urival .
                   ?urival ?pred ?uri. 
                   FILTER (?nameValue in ("DataDOI", "DataURI"))
                   FILTER (strstarts(str(?pred), str(rdf:_)))
                   }
                 }
                FILTER (?t in ("setup/daq/preprocessing", "stimulus/white_noise"))
             }""", initNs=NAMESPACE_MAP)
