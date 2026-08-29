# Extracted from zwelz3/holonic@d8d1758752 : src/holonic/test/test_ontology_utilization.py
# region: TestOntologyHygiene.test_no_term_is_declared_twice_with_different_types (lines 390-400, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, RDFS, SKOS, Graph
CGA = "urn:holonic:ontology:"
ONTOLOGY_DIR = Path(__file__).parent.parent / "ontology"
DECLARED_TYPES = (
    OWL.Class,
    OWL.ObjectProperty,
    OWL.DatatypeProperty,
    OWL.AnnotationProperty,
    RDFS.Class,
)

def test_no_term_is_declared_twice_with_different_types(self):
    """A term typed as both a class and a property is a copy-paste artifact."""
    graph = Graph().parse(ONTOLOGY_DIR / "cga.ttl", format="turtle")
    conflicted = []
    for subject in set(graph.subjects(RDF.type, None)):
        if not str(subject).startswith(CGA):
            continue
        types = {t for t in graph.objects(subject, RDF.type) if t in DECLARED_TYPES}
        if len(types) > 1:
            conflicted.append((str(subject)[len(CGA) :], sorted(str(t) for t in types)))
    assert not conflicted, f"terms with conflicting declarations: {conflicted}"
