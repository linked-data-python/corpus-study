# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/sstim-ecosystem-contract.py
# region: check_public_relationship_mirroring_guard (lines 692-714, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
ECO = Namespace("https://w3id.org/sstim/ecosystem#")

def check_public_relationship_mirroring_guard(
    public: Graph, private: Graph
) -> list[str]:
    """Prove the claim-snapshot mirror detects an altered public target."""
    errors: list[str] = []
    relationships = sorted(
        set(public.subjects(RDF.type, ECO.EcosystemRelationship)), key=str
    )
    require(bool(relationships), "relationship mirroring guard requires one record", errors)
    if not relationships:
        return errors

    altered = Graph()
    for triple in private:
        altered.add(triple)
    altered.remove((relationships[0], ECO.relationshipTarget, None))
    mirror_errors = check_public_relationship_mirroring(public, altered)
    require(
        any("private relationship mirror differs" in issue for issue in mirror_errors),
        "public-relationship mirroring guard did not reject an altered snapshot",
        errors,
    )
    return errors
