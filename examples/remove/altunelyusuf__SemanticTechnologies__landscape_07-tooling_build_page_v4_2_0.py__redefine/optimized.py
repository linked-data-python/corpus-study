# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_page_v4_2_0.py
# region: redefine (lines 56-60, stratum remove)
# licence of the source repository: see meta.json
from page_context import HERE, SP  # context shim, see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v4_1_0.ttl")

def redefine(iri, label=None, defn=None, note=None, scope=None):
    for predicate, value in ((RDFS.label, label), (SKOS.definition, defn),
                             (SKOS.note, note), (SKOS.scopeNote, scope)):
        if value is not None:
            g.remove((iri, predicate, None))
            g.add((iri, predicate, Literal(value, lang="en")))

# Demo harness (see meta.json), verbatim on both sides: redefine mutates the
# module graph, so the module-state oracle needs the calls that the builder
# makes at lines 61-70 of the source file, shortened to their shape, plus the
# calls that the repository never makes (scope on subjects that carry one, an
# empty string, several annotations at once), see driver.py.
redefine(SP.Page,
    label="Interactive landscape page v4.2.0",
    defn="The Stage-4 conversational rendering of the v4.0.0 landscape.",
    note="Rebuilt by the v4.2.0 builder.")
redefine(SP.ReferencesRegion,
    defn="The references region lists all ninety-three verified entries.")
redefine(SP.Doc, scope="Stage-3 document, v4.2.0.")
redefine(SP.W1)
redefine(SP.Page, scope="Covers the sixty class taxonomy.")
redefine(SP.ReferencesRegion, scope="Rendered once, in the footer.")
redefine(SP.W1, note="")
redefine(SP.Doc, label="", scope="")
redefine(SP.ReferencesRegion, defn="")
