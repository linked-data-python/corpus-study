# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/check_consistency.py
# region: _strip_ontology_header (lines 151-167, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph
from rdflib.namespace import OWL, RDF

def _strip_ontology_header(g):
    """Drop every triple whose subject is this file's own owl:Ontology
    individual (rdf:type owl:Ontology, owl:imports, owl:versionIRI,
    owl:versionInfo, ...). Necessary once we merge several *.vt.owl.ttl files'
    raw content together: HermiT's underlying OWL API actively tries to
    fetch and parse each owl:imports target itself (including the bare
    rdf:/rdfs: namespace URIs owl2vt.py's ontology header always
    includes), which fails outright since those URLs serve HTML, not OWL --
    the header's imports already got followed structurally above, in
    build_full_owl_output's own recursion, so the header itself is pure
    noise (and, left in, actively breaks HermiT) once merged."""
    ontologies = set(g.subjects(RDF.type, OWL.Ontology))
    out = Graph()
    for s, p, o in g:
        if s not in ontologies:
            out.add((s, p, o))
    return out
