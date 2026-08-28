# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v1_0_0.py
# region: <module> (lines 149-151, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, PROV
SEM = Namespace("http://example.org/semtech#")
g_ab  = Graph(); g_ab.parse(f"{H}/02-ontology/semtech_abox_v1_0_0.ttl")

ex_no_prov = [str(s) for s in g_ab.subjects(RDF.type, OWL.NamedIndividual)
              if list(g_ab.objects(s, RDF.type)) and any(str(t).startswith(str(SEM)+"T") for t in g_ab.objects(s, RDF.type))
              and not g_ab.value(s, SEM.hasSourceProvenance)]
