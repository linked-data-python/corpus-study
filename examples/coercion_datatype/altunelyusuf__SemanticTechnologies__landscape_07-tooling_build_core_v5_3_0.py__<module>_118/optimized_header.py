# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v5_3_0.py
# region: <module> (lines 118-126, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS
from context_shim import BASEDIR, S  # context shim, see meta.json
SEM = Namespace("http://example.org/semtech#")
g2 = Graph().parse(f"{BASEDIR}/02-ontology/semtech_tbox_v5_2_0.ttl")

for ap, lab, dfn in [
    ("criticalTerm", "critical term", "This annotation carries one critical term of the subject area as 'TERM | expansion | gloss' for glossary and lens rendering."),
    ("syntacticExample", "syntactic example", "This annotation carries a small validated example in the subject area's concrete syntax as 'language | caption | code'."),
    ("criticalTip", "critical tip", "This annotation carries the chapter's one critical practitioner consideration.")]:
    p = SEM[ap]
    g2 += [
        (p, RDF.type, OWL.AnnotationProperty),
        (p, RDFS.label, Literal(lab, lang="en")),
        (p, SKOS.definition, Literal(dfn, lang="en")),
        (p, DCTERMS.source, Literal(S("R1"), lang="en")),
    ]
