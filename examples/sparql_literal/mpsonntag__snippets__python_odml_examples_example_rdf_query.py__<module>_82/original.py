# Extracted from mpsonntag/snippets@164fac3966 : python/odml/examples/example_rdf_query.py
# region: <module> (lines 82-84, stratum sparql_literal)
# licence of the source repository: see meta.json
graph = Graph()
q = prepareQuery("""SELECT *
            WHERE {
               ?d rdf:type odml:Document .
               ?d odml:hasSection ?s .
               ?s rdf:type odml:Section .
               ?s odml:hasType "setup/daq" .
            }""", initNs=NAMESPACE_MAP)
q = prepareQuery("""SELECT * 
             WHERE { 
                ?d a odml:Document . 
                ?d odml:hasSection* ?s . 
                ?s a odml:Section . 
                ?s odml:hasType "setup/daq/preprocessing" . 
                ?s odml:hasName ?name . 
             }""", initNs=NAMESPACE_MAP)
q = prepareQuery("""SELECT * 
                   WHERE {
                   ?datasec a odml:Section .
                   ?datasec odml:hasType "DataReference" .
                   ?datasec odml:hasName ?dataSecName .
                   ?datasec odml:hasProperty ?uriprop .
                   ?uriprop odml:hasName ?nameValue .
                   ?uriprop odml:hasValue ?urival .
                   ?urival ?pred ?uri. 
                   FILTER (?nameValue in ("DataDOI", "DataURI"))
                   FILTER (strstarts(str(?pred), str(rdf:_)))
             }""", initNs=NAMESPACE_MAP)
q = prepareQuery("""SELECT * 
             WHERE { 
                ?d a odml:Document . 
                ?d odml:hasSection* ?s .
                ?s a odml:Section . 
                ?s odml:hasType "setup/daq/preprocessing" . 
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
             }""", initNs=NAMESPACE_MAP)
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

for row in graph.query(q):
    print("Doc: %s, secname: %s, DataSecName: %s, datauri: %s" % (row.d, row.secname,
                                                                  row.dataSecName, row.uri))
