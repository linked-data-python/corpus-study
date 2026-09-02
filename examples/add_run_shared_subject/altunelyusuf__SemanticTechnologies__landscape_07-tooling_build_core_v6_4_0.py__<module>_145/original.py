# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_4_0.py
# region: <module> (lines 145-152, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
from context_shim import BASEDIR, S
SEM = Namespace("http://example.org/semtech#")
g2 = Graph().parse(f"{BASEDIR}/02-ontology/semtech_tbox_v6_3_0.ttl")

for cid, clab, cdef in [
    ("GovernanceRole", "Governance role", "A governance role is a position of accountability for some part of how semantic-technology adoption is governed -- distinct from a taxonomy class or a case-study instance."),
    ("GovernanceActivity", "Governance activity", "A governance activity is a recurring action a governance role performs to keep the domain's models fit for use."),
    ("GovernanceRule", "Governance rule", "A governance rule is a decision procedure a governance activity applies when a change or dispute arises."),
]:
    c = SEM[cid]
    g2.add((c, RDF.type, OWL.Class)); g2.add((c, RDFS.label, Literal(clab, lang="en")))
    g2.add((c, SKOS.definition, Literal(cdef, lang="en"))); g2.add((c, DCTERMS.source, Literal(S("R-TOGAF", "R-DAMA"), lang="en")))
