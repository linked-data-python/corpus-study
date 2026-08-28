# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_7_0.py
# region: <module> (lines 124-132, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
SEM = Namespace("http://example.org/semtech#")
g2 = Graph().parse(f"{BASEDIR}/02-ontology/semtech_tbox_v6_6_0.ttl")

for ap, lab, dfn in [
    ("criticalTerm", "critical term", "This annotation carries one critical term of the subject area as 'TERM | expansion | gloss' for glossary and lens rendering."),
    ("syntacticExample", "syntactic example", "This annotation carries a small validated example in the subject area's concrete syntax as 'language | caption | code'."),
    ("criticalTip", "critical tip", "This annotation carries the chapter's one critical practitioner consideration.")]:
    p = SEM[ap]
    g2.add((p, RDF.type, OWL.AnnotationProperty))
    g2.add((p, RDFS.label, Literal(lab, lang="en")))
    g2.add((p, SKOS.definition, Literal(dfn, lang="en")))
    g2.add((p, DCTERMS.source, Literal(S("R1"), lang="en")))
