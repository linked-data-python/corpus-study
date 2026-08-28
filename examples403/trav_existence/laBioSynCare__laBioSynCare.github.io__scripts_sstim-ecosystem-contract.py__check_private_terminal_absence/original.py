# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/sstim-ecosystem-contract.py
# region: check_private_terminal_absence (lines 512-589, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, XSD
ECO = Namespace("https://w3id.org/sstim/ecosystem#")
TERMINAL_PRIVATE_OUTCOMES = {
    ECO.outcomeChangesRequested,
    ECO.outcomeObjected,
    ECO.outcomeConsentDeclined,
    ECO.outcomePublicationWithheld,
    ECO.outcomeRecordAmended,
    ECO.outcomeRemovalRequested,
    ECO.outcomeConsentWithdrawn,
}

def check_private_terminal_absence(
    public: Graph, private: Graph, *, require_terminal: bool = True
) -> list[str]:
    """Prove that private terminal events have no identifying public chain."""
    errors: list[str] = []
    terminal_events = {
        event
        for outcome in TERMINAL_PRIVATE_OUTCOMES
        for event in private.subjects(ECO.engagementOutcome, outcome)
    }
    if require_terminal:
        require(bool(terminal_events), "private terminal fixture has no blocking event", errors)
    terminal_relationships: set = set()

    for event in terminal_events:
        require(
            not any(public.triples((event, None, None))),
            f"terminal private event remains a public subject: {event}",
            errors,
        )
        require(
            not any(public.triples((None, ECO.hasEngagementActivity, event))),
            f"terminal private event remains linked from a public relationship: {event}",
            errors,
        )
        governed = values(private, event, ECO.engagementFor)
        require(
            len(governed) == 1,
            f"private terminal event {event} must govern exactly one relationship",
            errors,
        )
        if (
            (event, RDF.type, ECO.WithdrawalActivity) in private
            or (event, RDF.type, ECO.AmendmentActivity) in private
        ):
            invalidated = values(private, event, PROV.invalidated)
            require(
                governed == invalidated,
                f"private amendment/withdrawal {event} must invalidate its governed relationship",
                errors,
            )
        terminal_relationships.update(governed)

    backlink_predicates = {
        ECO.hasEcosystemRelationship,
        ECO.engagementFor,
        ECO.hasEngagementActivity,
    }
    for relationship in terminal_relationships:
        governed_agents = values(private, relationship, ECO.relationshipAgent)
        require(
            len(governed_agents) == 1,
            f"private terminal relationship {relationship} must retain exactly "
            "one private relationshipAgent projection for orphan cleanup",
            errors,
        )
        require(
            not any(public.triples((relationship, None, None))),
            f"terminal private relationship remains a public subject: {relationship}",
            errors,
        )
        for predicate in backlink_predicates:
            require(
                not any(public.triples((None, predicate, relationship))),
                f"terminal private relationship remains public through {predicate}: {relationship}",
                errors,
            )
        for agent in governed_agents:
            if not any(public.triples((agent, None, None))):
                continue
            remaining = set(public.objects(agent, ECO.hasEcosystemRelationship))
            remaining.difference_update(terminal_relationships)
            require(
                bool(remaining),
                f"agent orphaned by terminal private relationship remains public: {agent}",
                errors,
            )
    return errors
