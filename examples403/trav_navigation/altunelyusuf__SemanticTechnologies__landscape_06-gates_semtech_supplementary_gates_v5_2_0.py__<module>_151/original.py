# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v5_2_0.py
# region: <module> (lines 151-151, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD
SEM = Namespace("http://example.org/semtech#")
kind_cls = {SEM[f"Kind{k}"] for k in EC.KIND_DEFNS}
f2 = Graph(); f2 += ab

neg2 = any(len([t for t in f2.objects(i, RDF.type) if t in kind_cls]) != 1 for i in f2.subjects(SEM.hasSourceProvenance, None))
