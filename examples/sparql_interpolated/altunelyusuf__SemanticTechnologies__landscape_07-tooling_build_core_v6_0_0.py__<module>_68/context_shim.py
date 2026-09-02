# Context shim (see meta.json): the SNIPPETS registry and SNIPPET_PREFIXES
# constant from landscape/07-tooling/enrichment_g_v3_0_0.py in
# altunelyusuf/SemanticTechnologies@bad0fa7c46, reproduced verbatim -- this
# is the only data the region reads (the rest of that module -- TERMS,
# TIPS -- and everything upstream of it in build_core_v6_0_0.py's own
# `load()` chain is untouched by this region). A subset of the real
# SNIPPETS dict: kept every entry whose `check` is "turtle"/"sparql"/"json"
# (these are what the region actually validates) plus one "none" entry
# (T1C1, real) so the "check matches nothing, skip silently" branch is
# exercised too. Identical for both representations.
#
# The two entries marked SYNTHETIC below are NOT from the source repository
# -- the real SNIPPETS are all valid (they are the project's own reviewed
# documentation examples), so nothing in the real data exercises the
# `except Exception` / "snippet invalid" branch. Added deliberately broken
# turtle/sparql text so that branch is exercised too, same shape as the
# real entries otherwise.
SNIPPETS = {
    "T1C1": ("turtle", "One product fact as RDF (Turtle)",
             """:lcw:Product_8680000000017 a gs1:Product ;
    gs1:gtin "08680000000017" ;
    rdfs:label "Basic crew-neck t-shirt"@en .""", "none"),
    "T1C2": ("turtle", "Three schema levels in one file",
             """ex:Garment a owl:Class .
ex:TShirt rdfs:subClassOf ex:Garment .
ex:fit a owl:DatatypeProperty ; rdfs:domain ex:Garment .
ex:CasualWear a skos:Concept ; skos:prefLabel "Casual wear"@en .""", "turtle"),
    "T1C3": ("sparql", "Transitive reach with a property path",
             """SELECT ?type WHERE {
  ex:TShirt rdfs:subClassOf+ ?type .
}""", "sparql"),
    "T1C4": ("turtle", "A complete two-constraint SHACL shape",
             """ex:ProductShape a sh:NodeShape ;
  sh:targetClass gs1:Product ;
  sh:property [ sh:path gs1:gtin ;
                sh:minCount 1 ; sh:maxCount 1 ;
                sh:pattern "^[0-9]{14}$" ] .""", "turtle"),
    "T1C6": ("json", "A JSON-LD context making plain JSON semantic",
             """{ "@context": {
    "gtin": "https://gs1.org/voc/gtin",
    "name": "http://www.w3.org/2000/01/rdf-schema#label"
} }""", "json"),
    "T2C1": ("turtle", "A DCAT dataset entry",
             """ex:SalesCube a dcat:Dataset ;
  dcterms:title "Daily sales cube"@en ;
  dcat:distribution [ dcat:accessURL <https://data.example/sales> ] .""", "turtle"),
    "T6C2": ("turtle", "A CI quality gate as a SHACL SPARQL constraint",
             """ex:LabelledShape a sh:NodeShape ;
  sh:targetClass owl:Class ;
  sh:property [ sh:path rdfs:label ; sh:minCount 1 ;
                sh:message "Every class needs a label." ] .""", "turtle"),
    "T12C1": ("turtle", "A grounded answer's provenance (PROV-O)",
              """:answer_42 prov:wasDerivedFrom :fact_gtin_supplier ;
    prov:wasGeneratedBy :graphrag_run_2026_08_04 ;
    prov:wasAttributedTo :lcw_assistant .""", "turtle"),
    "SYN1": ("turtle", "SYNTHETIC: unterminated triple (not from the source repo)",
             """ex:Broken a owl:Class""", "turtle"),
    "SYN2": ("sparql", "SYNTHETIC: malformed SELECT (not from the source repo)",
             """SELECT ?x WHERE ?x a ex:Thing }""", "sparql"),
}
SNIPPET_PREFIXES = """@prefix ex: <http://example.org/x#> . @prefix lcw: <http://example.org/lcw#> .
@prefix gs1: <https://gs1.org/voc/> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> . @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix sh: <http://www.w3.org/ns/shacl#> . @prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> . @prefix prov: <http://www.w3.org/ns/prov#> .
@prefix : <http://example.org/x#> .\n"""
