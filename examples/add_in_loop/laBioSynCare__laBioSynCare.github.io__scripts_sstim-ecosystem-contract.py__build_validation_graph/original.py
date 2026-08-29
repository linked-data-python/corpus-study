# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/sstim-ecosystem-contract.py
# region: build_validation_graph (lines 383-409, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, XSD
CONTEXT_FILES = tuple(
    ROOT / MANIFEST_MODULES[module_id]["source"]["path"]
    for module_id in FULL_PROFILE["modules"]
) + (
    ONTOLOGY_DIR / "instances" / "frameworks" / "bsc.ttl",
    # The programme node is a relationship target (ADR 0047); include it so a
    # ledger record pointing at a programme that does not exist is dangling.
    ONTOLOGY_DIR / "instances" / "programmes" / "biosyncare-ecosystem.ttl",
)
IMPLEMENTATION_CATALOG = (
    ONTOLOGY_DIR / "instances" / "implementations" / "implementations.ttl"
)
SSTIM = Namespace("https://w3id.org/sstim#")
ECO = Namespace("https://w3id.org/sstim/ecosystem#")

def build_validation_graph(artifact: Graph) -> Graph:
    """Add only the closed implementation profile needed by relationship targets.

    Loading the full implementation catalog would also pull its protocol links;
    RDFS range inference would then target incomplete protocol stubs in an
    otherwise isolated ecosystem artifact. This projection keeps external
    dependencies explicit without allowing another ecosystem file to complete
    the artifact under test.
    """
    merged = parse_graph(list(CONTEXT_FILES))
    for triple in artifact:
        merged.add(triple)

    catalog = parse_graph([IMPLEMENTATION_CATALOG])
    profile_predicates = {
        RDF.type,
        RDFS.label,
        DCTERMS.description,
        SSTIM.implementsFramework,
    }
    for target in artifact.objects(None, ECO.relationshipTarget):
        if (target, RDF.type, SSTIM.SensoryStimulationImplementation) not in catalog:
            continue
        for predicate in profile_predicates:
            for obj in catalog.objects(target, predicate):
                merged.add((target, predicate, obj))
    return merged
