# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v6_10_0.py
# region: <module> (lines 403-410, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD
SEM = Namespace("http://example.org/semtech#")
ab = Graph().parse(f"{HERE}/02-ontology/semtech_abox_v6_9_0.ttl")
IRI = {n["id"]: cls_iri(n) for n in nodes}
EM2 = load("enrichment_m", "v5_4_0")
hs_detail = []

for miid, mlab, mkind, mcid, mdfn, mrefs in EM2.NEW_INSTANCES:
    ind = SEM[miid]
    typed = (ind, RDF.type, IRI[mcid]) in ab and (ind, RDF.type, SEM[f"Kind{mkind}"]) in ab
    labeled = str(ab.value(ind, RDFS.label) or "") == mlab
    sourced = bool(ab.value(ind, DCTERMS.source))
    prov = (ind, SEM.hasSourceProvenance, None) in ab
    if not (typed and labeled and sourced and prov): hs_ok = False
    hs_detail.append(mlab)
