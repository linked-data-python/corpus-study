# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/sstim-ecosystem-contract.py
# region: check_real_public_artifact (lines 827-885, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, XSD
from sstim_context import require
ECO = Namespace("https://w3id.org/sstim/ecosystem#")

def check_real_public_artifact(artifact: Graph, label: str) -> list[str]:
    """Additional fixture/real separation for the future F4 aggregate."""
    errors: list[str] = []
    agents = set(artifact.subjects(RDF.type, ECO.EcosystemAgent))
    relationships = set(artifact.subjects(RDF.type, ECO.EcosystemRelationship))
    activities = set(artifact.subjects(RDF.type, ECO.EngagementActivity))
    require(bool(agents), f"{label}: real public artifact has no EcosystemAgent", errors)
    require(bool(relationships), f"{label}: real public artifact has no EcosystemRelationship", errors)
    require(bool(activities), f"{label}: real public artifact has no EngagementActivity", errors)

    for nodes, predicate, role in (
        (agents, PROV.wasAttributedTo, "agent-record curator"),
        (relationships, PROV.wasAttributedTo, "relationship curator"),
        (activities, PROV.wasAssociatedWith, "public activity actor"),
    ):
        for node in nodes:
            for actor in artifact.objects(node, predicate):
                require(
                    actor in agents,
                    f"{label}: real {role} {actor} must be a verified "
                    "EcosystemAgent in the same reviewed aggregate",
                    errors,
                )

    for subject in set(artifact.subjects()):
        if isinstance(subject, URIRef) and str(subject).startswith(
            "https://w3id.org/sstim/implementation/"
        ):
            errors.append(
                f"{label}: real ecosystem artifacts must reference, not redeclare, "
                f"implementation-owned subject {subject}"
            )

    for iri in {str(term) for term in artifact.all_nodes() if isinstance(term, URIRef)}:
        require(
            "synthetic-" not in iri,
            f"{label}: real public artifact references a synthetic fixture IRI: {iri}",
            errors,
        )
        require(
            not iri.startswith("https://example.org/"),
            f"{label}: real public artifact uses example.org fixture data: {iri}",
            errors,
        )
    return errors
