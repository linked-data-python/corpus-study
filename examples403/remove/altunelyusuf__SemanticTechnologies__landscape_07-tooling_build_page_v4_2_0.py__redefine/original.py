# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_page_v4_2_0.py
# region: redefine (lines 56-60, stratum remove)
# licence of the source repository: see meta.json
from page_context import HERE, SP  # context shim, see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v4_1_0.ttl")

def redefine(iri, label=None, defn=None, note=None, scope=None):
    if label is not None: g.remove((iri, RDFS.label, None)); g.add((iri, RDFS.label, Literal(label, lang="en")))
    if defn is not None: g.remove((iri, SKOS.definition, None)); g.add((iri, SKOS.definition, Literal(defn, lang="en")))
    if note is not None: g.remove((iri, SKOS.note, None)); g.add((iri, SKOS.note, Literal(note, lang="en")))
    if scope is not None: g.remove((iri, SKOS.scopeNote, None)); g.add((iri, SKOS.scopeNote, Literal(scope, lang="en")))

# Demo harness (see meta.json), verbatim on both sides: redefine mutates the
# module graph, so the module-state oracle needs the calls that the builder
# makes at lines 61-70 of the source file, shortened to their shape.
redefine(SP.Page,
    label="Interactive landscape page v4.2.0",
    defn="The Stage-4 conversational rendering of the v4.0.0 landscape.",
    note="Rebuilt by the v4.2.0 builder.")
redefine(SP.ReferencesRegion,
    defn="The references region lists all ninety-three verified entries.")
redefine(SP.Doc, scope="Stage-3 document, v4.2.0.")
redefine(SP.W1)
