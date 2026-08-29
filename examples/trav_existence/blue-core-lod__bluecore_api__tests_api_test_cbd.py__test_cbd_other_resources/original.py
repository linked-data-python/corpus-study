# Extracted from blue-core-lod/bluecore_api@f07d76c83a : tests/api/test_cbd.py
# region: test_cbd_other_resources (lines 128-194, stratum trav_existence)
# licence of the source repository: see meta.json
from bluecore_models.bluecore_graph import BluecoreGraph
from bluecore_models.models import Instance, Work
from bluecore_models.namespaces import BF
from fastapi.testclient import TestClient
from lxml import etree
from rdflib import RDF, Graph, URIRef
from sqlalchemy.orm import Session
from bluecore_api.app.utils.serialize.cbd import (
    XPATH_NAMESPACES,
    generate_cbd_graph,
    generate_cbd_xml,
    related_works,
    reorder_instance_types,
    reorder_work_types,
)
from bluecore_api.constants import BibframeType

def test_cbd_other_resources(client: TestClient, db_session: Session):
    # save_graph wants a sessionmaker rather than a Session, so we make a fake one
    def sessionmaker(*args, **kwargs):
        return db_session

    # parse a CBD json-ld file
    graph = Graph()
    graph.parse("tests/23807141.jsonld")

    # persist the graph to the database
    bc_graph = BluecoreGraph(graph)
    bc_graph.save(sessionmaker)

    assert (
        URIRef("http://id.loc.gov/authorities/subjects/sh85065889")
        in bc_graph.graph.subjects()
    )

    # get one of the instance URIs that was created
    assert len(bc_graph.instances()) == 2
    instance_graph = bc_graph.instances()[1]

    # determine its local path
    instance_uri = next(instance_graph.subjects(RDF.type, BF.Instance))
    uuid = instance_uri.split("/")[-1]

    response = client.get(f"/instances/{uuid}.cbd.jsonld")
    response_graph = Graph()
    response_graph.parse(data=response.content, format=response.headers["Content-Type"])
    assert (
        URIRef("http://id.loc.gov/authorities/subjects/sh85065889")
        in response_graph.subjects()
    )

    response = client.get(f"/instances/{uuid}.cbd.jsonld")
    response_graph = Graph()
    response_graph.parse(data=response.content, format="json-ld")
    assert (
        URIRef("http://id.loc.gov/authorities/subjects/sh85065889")
        in response_graph.subjects()
    )

    instance = db_session.query(Instance).filter(Instance.uuid == uuid).first()
    cbd_graph = generate_cbd_graph(instance)
    cbd_xml = generate_cbd_xml(cbd_graph)
    # This record has two Works, each with an Instance, and they reference each
    # other through bf:relation. LC's CBD carries all four, so ours does too.
    assert len(cbd_xml) == 4, "Expected 4 top-level elements in CBD XML"
    top_level_tags: list[BibframeType] = [BibframeType.WORK, BibframeType.INSTANCE]
    for elem in cbd_xml:
        local_name = etree.QName(elem).localname
        assert local_name in top_level_tags, (
            f"Unexpected top-level element: {local_name}"
        )
    xpath = "bf:Work/bf:contribution/bf:Contribution/bf:agent/bf:Agent[@rdf:about='http://id.loc.gov/rwo/agents/n2024040883']"
    match = cbd_xml.xpath(xpath, namespaces=XPATH_NAMESPACES)
    # Both Works credit this agent, and each nests its own copy of the description.
    assert len(match) == 2, (
        "Expected to find a matching Agent element for "
        "http://id.loc.gov/rwo/agents/n2024040883 under each Work"
    )
    for agent in match:
        label = agent.find("{http://www.w3.org/2000/01/rdf-schema#}label")
        assert label is not None, "Expected to find rdfs:label element for the Agent"
        assert label.text == "Farri, Elisa", (
            f"Expected Agent label to be 'Farri, Elisa' but got '{label.text}'"
        )
