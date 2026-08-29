# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/sstim-ecosystem-contract.py
# region: check_positive_contract (lines 1096-1125, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, XSD
ECO = Namespace("https://w3id.org/sstim/ecosystem#")
PERSON = URIRef("https://w3id.org/sstim/specialist/synthetic-alex-rivera")
CURATOR = URIRef("https://example.org/agent/synthetic-curator")

for event in activities:
    inbound = set(fixture.subjects(ECO.hasEngagementActivity, event))
    governed = values(fixture, event, ECO.engagementFor)
    require(len(inbound) == 1 and inbound == governed,
            f"{event}: activity must belong to exactly one matching relationship", errors)
    expected_actor = {CURATOR}
    if (event, RDF.type, ECO.ConsentDecisionActivity) in fixture:
        relationship = next(iter(governed), None)
        if relationship is not None and values(
            fixture, relationship, ECO.relationshipAgent
        ) == {PERSON}:
            expected_actor = {PERSON}
    require(values(fixture, event, PROV.wasAssociatedWith) == expected_actor,
            f"{event}: expected actor {expected_actor}", errors)
    actor = next(iter(expected_actor))
    require((actor, RDF.type, PROV.Agent) in merged,
            f"{event}: actor {actor} is not explicitly a prov:Agent", errors)

    event_times = values(fixture, event, PROV.endedAtTime)
    require(len(event_times) == 1 and next(iter(event_times)).datatype == XSD.dateTime,
            f"{event}: event time must be one xsd:dateTime", errors)
    if len(event_times) == 1:
        current = next(iter(event_times)).toPython()
        for predecessor in fixture.objects(event, PROV.wasInformedBy):
            prior_times = values(fixture, predecessor, PROV.endedAtTime)
            require(len(prior_times) == 1,
                    f"{event}: predecessor {predecessor} has no unique timestamp", errors)
            if len(prior_times) == 1:
                require(next(iter(prior_times)).toPython() < current,
                        f"{event}: predecessor {predecessor} is not strictly earlier", errors)
