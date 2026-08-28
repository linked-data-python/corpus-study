# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/sstim-ecosystem-contract.py
# region: check_real_public_artifact (lines 827-885, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, XSD
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

    for agent in agents:
        for curator in artifact.objects(agent, PROV.wasAttributedTo):
            require(
                curator in agents,
                f"{label}: real agent-record curator {curator} must be a verified "
                "EcosystemAgent in the same reviewed aggregate",
                errors,
            )
    for relationship in relationships:
        for curator in artifact.objects(relationship, PROV.wasAttributedTo):
            require(
                curator in agents,
                f"{label}: real relationship curator {curator} must be a verified "
                "EcosystemAgent in the same reviewed aggregate",
                errors,
            )
    for activity in activities:
        for actor in artifact.objects(activity, PROV.wasAssociatedWith):
            require(
                actor in agents,
                f"{label}: real public activity actor {actor} must be a verified "
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

    for term in set(artifact.all_nodes()):
        if not isinstance(term, URIRef):
            continue
        iri = str(term)
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
