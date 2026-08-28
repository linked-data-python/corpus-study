# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v4_4_0.py
# region: <module> (lines 101-101, stratum remove)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
g1 = Graph().parse(f"{BASEDIR}/01-research/semtech_research_v4_3_0.ttl")
corpus = SRNS.ResearchCorpus

g1.remove((corpus, SKOS.note, None))
