# Extracted from dev365code/iirds-validate@4b3f840df8 : tests/test_shapes_static.py
# region: test_the_shapes_without_a_spec_link_are_exactly_the_known_five (lines 298-316, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, Namespace, URIRef
SHAPE_DIR = ROOT / "shapes" / "iirds-1.3"

def test_the_shapes_without_a_spec_link_are_exactly_the_known_five():
    """The README's dcterms:source claim drifted three times in a
    row (all → all-but-four → the measured truth). Claims about coverage
    live here now, where drift turns red instead of stale."""
    from rdflib import Graph, Namespace

    DCT = Namespace("http://purl.org/dc/terms/")
    SH_NS = Namespace("http://www.w3.org/ns/shacl#")
    graph = Graph()
    for name in ("iirds-core.ttl", "iirds-sparql.ttl",
                 "iirds-handover-core.ttl", "iirds-handover-sparql.ttl"):
        graph.parse(SHAPE_DIR / name, format="turtle")

    missing = set()
    for kind in (SH_NS.NodeShape, SH_NS.PropertyShape):
        for shape in graph.subjects(RDF.type, kind):
            if graph.value(shape, DCT.source) is None:
                missing.add(str(shape).rsplit("#", 1)[-1])
    assert missing == {"L7", "L10", "S4", "S5", "M97.1"}, sorted(missing)
