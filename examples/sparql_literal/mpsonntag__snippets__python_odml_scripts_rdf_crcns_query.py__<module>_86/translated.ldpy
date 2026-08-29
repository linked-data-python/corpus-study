# Extracted from mpsonntag/snippets@164fac3966 : python/odml/scripts/rdf_crcns_query.py
# region: <module> (lines 86-88, stratum sparql_literal)
# licence of the source repository: see meta.json
curr_graph = Graph()
q = prepareQuery("""SELECT *
                   WHERE {
                   ?datasec a odml:DataReference .
                   ?datasec odml:hasName ?dataSecName .
                   ?datasec odml:hasProperty ?uriprop .
                   ?uriprop odml:hasName ?nameValue .
                   ?uriprop odml:hasValue ?urival .
             }""", initNs=NAMESPACE_MAP)
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
q = prepareQuery("""
SELECT * WHERE {
    ?d a odml:Document .
    ?d odml:hasSection* ?doisec .
    ?doisec a odml:Identifier .
    ?doisec odml:hasName ?dataSecName .
    ?doisec odml:hasProperty ?uriprop .
    ?uriprop odml:hasName "identifier" .
    ?uriprop odml:hasValue ?urival .
    ?urival ?uripred ?uri .
    ?doisec odml:hasProperty ?tprop .
    ?tprop odml:hasName "identifierType" .
    ?tprop odml:hasValue ?tpropval .
    ?tval ?tpred "DOI" .
    FILTER (strstarts(str(?uripred), str(rdf:_)))
}""", initNs=NAMESPACE_MAP)
q = prepareQuery("""
SELECT * WHERE {
    ?d a odml:Document .
    ?d odml:hasSection* ?s .
    ?s odml:hasType ?sectype . 
    ?s odml:hasName ?secname .
    { SELECT ?doiSecName ?uri WHERE {
        ?d a odml:Document .
        ?d odml:hasSection* ?doisec .
        ?doisec a odml:Identifier .
        ?doisec odml:hasName ?doiSecName .
        ?doisec odml:hasProperty ?uriprop .
        ?uriprop odml:hasName "identifier" .
        ?uriprop odml:hasValue ?urival .
        ?urival ?uripred ?uri .
        ?doisec odml:hasProperty ?tprop .
        ?tprop odml:hasName "identifierType" .
        ?tprop odml:hasValue ?tpropval .
        ?tval ?tpred "DOI" .
        FILTER (strstarts(str(?uripred), str(rdf:_)))
    }}
    FILTER (?sectype in ("Extracellular recordings", "Behavior"))
}""", initNs=NAMESPACE_MAP)
q = prepareQuery("""
SELECT * WHERE {
    ?d a odml:Document .
    ?d odml:hasSection* ?s .
    ?s odml:hasName ?secname .
    ?s odml:hasProperty ?p .
    ?p odml:hasName "task_keyword" .
    ?p odml:hasValue ?pval .
    ?pval ?valpred ?val .
    { SELECT ?doiSecName ?uri WHERE {
        ?d a odml:Document .
        ?d odml:hasSection* ?doisec .
        ?doisec a odml:Identifier .
        ?doisec odml:hasName ?doiSecName .
        ?doisec odml:hasProperty ?uriprop .
        ?uriprop odml:hasName "identifier" .
        ?uriprop odml:hasValue ?urival .
        ?urival ?uripred ?uri .
        ?doisec odml:hasProperty ?tprop .
        ?tprop odml:hasName "identifierType" .
        ?tprop odml:hasValue ?tpropval .
        ?tval ?tpred "DOI" .
        FILTER (strstarts(str(?uripred), str(rdf:_)))
    }}
    FILTER (?val in ("reward", "response"))
    FILTER (strstarts(str(?valpred), str(rdf:_)))
}""", initNs=NAMESPACE_MAP)
q = prepareQuery("""
SELECT * WHERE {
    ?d a odml:Document .
    ?d odml:hasSection* ?s .
    ?s odml:hasName ?secname .
    ?s odml:hasProperty ?p .
    ?p odml:hasName ?propName .
    ?p odml:hasValue ?pval .
    ?pval ?valpred ?val .
    { SELECT ?uri ?doiSecName WHERE {
        ?d a odml:Document .
        ?d odml:hasSection* ?doisec .
        ?doisec a odml:Identifier .
        ?doisec odml:hasName ?doiSecName .
        ?doisec odml:hasProperty ?doiprop .
        ?doiprop odml:hasName ?nameValue .
        ?doiprop odml:hasValue ?urival .
        ?urival ?uripred ?uri .
        FILTER (?nameValue in ("identifier"))
        FILTER (strstarts(str(?uripred), str(rdf:_)))
    }}
    FILTER (?val in ("Dataset/Neurophysiology", "CRCNS.org", "mice"))
    FILTER (strstarts(str(?valpred), str(rdf:_)))
}""", initNs=NAMESPACE_MAP)

for row in curr_graph.query(q):
    print(f"Doc: {row.d}, Sec: {row.doisec}, "
          f"DataSecName: {row.dataSecName}, Prop: {row.uri}")
