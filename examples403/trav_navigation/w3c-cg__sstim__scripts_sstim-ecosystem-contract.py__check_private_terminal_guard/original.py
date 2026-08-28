# Extracted from w3c-cg/sstim@39360a81b8 : scripts/sstim-ecosystem-contract.py
# region: check_private_terminal_guard (lines 746-808, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
ECO = Namespace("https://w3id.org/sstim/ecosystem#")
RECORD = "https://w3id.org/sstim/ecosystem-record/relationship/"
ACTIVITY = "https://w3id.org/sstim/ecosystem-record/activity/"

def check_private_terminal_guard(private: Graph) -> list[str]:
    """Prove the cross-store guard rejects both a record and a dangling event."""
    errors: list[str] = []
    withdrawal_relationships = {
        relationship
        for event in private.subjects(RDF.type, ECO.WithdrawalActivity)
        for relationship in private.objects(event, ECO.engagementFor)
    }
    require(
        len(withdrawal_relationships) == 1,
        "private terminal guard fixture must identify exactly one withdrawal relationship",
        errors,
    )
    if len(withdrawal_relationships) != 1:
        return errors

    relationship = next(iter(withdrawal_relationships))
    governed_agent = next(iter(private.objects(relationship, ECO.relationshipAgent)), None)
    leaked_record = Graph()
    leaked_record.add((relationship, RDF.type, ECO.EcosystemRelationship))
    record_errors = check_private_terminal_absence(leaked_record, private)
    require(
        any("remains a public subject" in issue for issue in record_errors),
        "private terminal guard did not reject a leaked relationship subject",
        errors,
    )

    leaked_activity = Graph()
    leaked_activity.add((
        URIRef(ACTIVITY + "synthetic-dangling-withdrawn-reference"),
        ECO.engagementFor,
        relationship,
    ))
    activity_errors = check_private_terminal_absence(leaked_activity, private)
    require(
        any("remains public through" in issue for issue in activity_errors),
        "private terminal guard did not reject a dangling public activity reference",
        errors,
    )
    if governed_agent is not None:
        orphan_public = Graph()
        orphan_public.add((governed_agent, RDF.type, ECO.EcosystemAgent))
        orphan_errors = check_private_terminal_absence(orphan_public, private)
        require(
            any("orphaned" in issue for issue in orphan_errors),
            "private terminal guard did not reject an orphaned public agent",
            errors,
        )

        retained_public = Graph()
        retained_public.add((governed_agent, RDF.type, ECO.EcosystemAgent))
        retained_public.add((
            governed_agent,
            ECO.hasEcosystemRelationship,
            URIRef(RECORD + "synthetic-unaffected-relationship"),
        ))
        retained_errors = check_private_terminal_absence(retained_public, private)
        require(
            not any("orphaned" in issue for issue in retained_errors),
            "private terminal guard removed an agent that still has another relationship",
            errors,
        )
    return errors
