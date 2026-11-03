# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_page_v6_9_0.py
# region: redefine (lines 61-65, stratum remove)
# licence of the source repository: see meta.json
from context_shim import HERE, replay  # context shim, see meta.json
from rdflib import Graph, Literal, RDFS, SKOS
g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v6_8_0.ttl")

def redefine(iri, label=None, defn=None, note=None, scope=None):
    for predicate, value in ((RDFS.label, label), (SKOS.definition, defn),
                             (SKOS.note, note), (SKOS.scopeNote, scope)):
        if value is not None:
            g.set((iri, predicate, Literal(value, lang="en")))

replay(redefine)  # demo harness in the shim, identical on both sides
