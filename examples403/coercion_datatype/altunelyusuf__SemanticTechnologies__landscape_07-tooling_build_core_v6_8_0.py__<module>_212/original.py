# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_8_0.py
# region: <module> (lines 212-219, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
el = load("enrichment_l", "v5_3_0")
SEM = Namespace("http://example.org/semtech#")
IRI = {n["id"]: cls_iri(n) for n in nodes}
g3 = Graph().parse(f"{BASEDIR}/02-ontology/semtech_abox_v6_7_0.ttl"); bump(g3)
KINDCLS = {"Role": SEM.GovernanceRole, "Activity": SEM.GovernanceActivity, "Rule": SEM.GovernanceRule}

for iid, lab, kind, defn, refs in el.ALL_ITEMS:
    ind = SEM[iid]
    g3.add((ind, RDF.type, KINDCLS[kind])); g3.add((ind, RDF.type, OWL.NamedIndividual))
    g3.add((ind, RDFS.label, Literal(lab, lang="en")))
    g3.add((ind, SKOS.definition, Literal(defn, lang="en")))
    g3.add((ind, DCTERMS.source, Literal(S(*refs), lang="en")))
    if iid in el.GOVERNS:
        g3.add((ind, SEM.governsSubject, IRI[el.GOVERNS[iid]]))
