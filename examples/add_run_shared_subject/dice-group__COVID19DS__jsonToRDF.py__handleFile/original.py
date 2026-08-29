# Extracted from dice-group/COVID19DS@7842845de5 : jsonToRDF.py
# region: handleFile (lines 292-292, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, DCTERMS, OWL
g = Graph()
swc = Namespace("http://data.semanticweb.org/ns/swc/ontology#")

g.add( (dice, RDF.type, swc.Paper) )
