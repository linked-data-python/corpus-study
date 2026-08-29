# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_page_v5_1_0.py
# region: <module> (lines 85-92, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
SEM = Namespace(T.BASE); IPO = Namespace("http://example.org/rdodi/interactive-page-ontology#")
g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v5_0_0.ttl")
lo15 = SP.LO15
w20 = SP.W20
n13 = byid["T1C3"]

for tr in [(RDF.type, IPO.InstructionalWidget), (RDF.type, OWL.NamedIndividual),
           (RDFS.label, Literal("Runnable code panel", lang="en")),
           (SKOS.definition, Literal("This panel lets the reader paste, type or upload their own structured (CSV/JSON) or unstructured (free text) content, converts it into RDF/Turtle with a pure-standard-library Python pipeline running in-browser via Pyodide, and runs a triple-pattern query or a minimal SHACL-like shape check over the result — the exact Python source is shown alongside static Turtle/SPARQL/SHACL examples.", lang="en")),
           (DCTERMS.source, Literal(S(*n13["refs"]) + " | " + S("NR-PYODIDE"), lang="en")),
           (SKOS.scopeNote, Literal("Warrant: primitive=hands-on-worked-example, generalized to the reader's own data; discourse feature=the read-convert-run pipeline structure this whole page's own tooling follows.", lang="en")),
           (SKOS.note, Literal("Design test PASS — content input (paste/upload), run-option dispatch, and Pyodide orchestration are executed in DOM smoke v5.0 with a mocked Pyodide runtime verifying the correct code and arguments are dispatched; live in-browser Python execution is a browser capability outside the Node-based smoke harness.", lang="en")),
           (IPO.coversLearningObjective, lo15)]:
    g.add((w20, tr[0], tr[1]))
