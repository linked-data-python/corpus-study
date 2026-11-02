# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_9_0.py
# region: <module> (lines 101-108, stratum coercion_datatype)
# licence of the source repository: see meta.json
# Executability: BASEDIR and load() -- defined earlier in the same source
# file, just outside this region -- restored via context_predecl.py (context
# shim, see meta.json).
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
from context_predecl import BASEDIR, load
eo = load("enrichment_o", "v6_1_0")
g1 = Graph().parse(f"{BASEDIR}/01-research/semtech_research_v6_8_0.ttl")
SRNS = Namespace("http://example.org/semtech/research#")
RO_PUB = URIRef("http://example.org/rdodi/research-ontology#Publication")
corpus = SRNS.ResearchCorpus

for key, e in eo.EXT8.items():
    pub = SRNS[f"Pub_{key.replace('-', '_')}"]
    g1 += [
        (corpus, RDFS.member, pub),
        (pub, RDF.type, RO_PUB),
        (pub, RDF.type, OWL.NamedIndividual),
        (pub, RDFS.label, Literal(e["cite"][:180], lang="en")),
        (pub, DCTERMS.source, Literal(e["cite"], lang="en")),
        (pub, SKOS.note, Literal(f"Verification level {e['level']}: {e['ev']}", lang="en")),
        (pub, RDFS.seeAlso, URIRef(e["url"])),
    ]
