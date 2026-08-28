# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v5_3_0.py
# region: <module> (lines 147-155, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
SEM = Namespace("http://example.org/semtech#")
g2 = Graph().parse(f"{BASEDIR}/02-ontology/semtech_tbox_v5_2_0.ttl")

for pid, plab, pdef, prange in [
    ("governsSubject", "governs subject", "This property links a governance role, activity or rule to the taxonomy subject area it governs.", None),
    ("performsActivity", "performs activity", "This property links a governance role to the activity it performs.", SEM.GovernanceActivity),
    ("appliesRule", "applies rule", "This property links a governance activity to the rule it applies when a change or dispute arises.", SEM.GovernanceRule),
]:
    p = SEM[pid]
    g2.add((p, RDF.type, OWL.ObjectProperty)); g2.add((p, RDFS.label, Literal(plab, lang="en")))
    g2.add((p, SKOS.definition, Literal(pdef, lang="en"))); g2.add((p, DCTERMS.source, Literal(S("R-TOGAF"), lang="en")))
    if prange: g2.add((p, RDFS.range, prange))
