# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_9_0.py
# region: <module> (lines 101-108, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
eo = load("enrichment_o", "v6_1_0")
g1 = Graph().parse(f"{BASEDIR}/01-research/semtech_research_v6_8_0.ttl")
SRNS = Namespace("http://example.org/semtech/research#")
RO_PUB = URIRef("http://example.org/rdodi/research-ontology#Publication")
corpus = SRNS.ResearchCorpus

for key, e in eo.EXT8.items():
    pub = SRNS[f"Pub_{key.replace(chr(45), chr(95))}"]
    g1.add((corpus, RDFS.member, pub))
    g1.add((pub, RDF.type, RO_PUB)); g1.add((pub, RDF.type, OWL.NamedIndividual))
    g1.add((pub, RDFS.label, Literal(e["cite"][:180], lang="en")))
    g1.add((pub, DCTERMS.source, Literal(e["cite"], lang="en")))
    g1.add((pub, SKOS.note, Literal(f"Verification level {e['level']}: {e['ev']}", lang="en")))
    g1.add((pub, RDFS.seeAlso, URIRef(e["url"])))
