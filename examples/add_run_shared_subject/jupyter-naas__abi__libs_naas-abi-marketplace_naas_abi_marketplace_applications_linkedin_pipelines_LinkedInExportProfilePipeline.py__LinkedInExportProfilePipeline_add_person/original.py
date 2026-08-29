# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/applications/linkedin/pipelines/LinkedInExportProfilePipeline.py
# region: LinkedInExportProfilePipeline.add_person (lines 220-270, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import uuid
from datetime import UTC, datetime
from naas_abi_core import logger
from naas_abi_core.utils.Graph import ABI, BFO, CCO
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
PERSON = CCO["ont00001262"]

def add_person(
    self,
    graph: Graph,
    linkedin_profile_page_uri: URIRef,
    backing_datasource_component_uri: URIRef,
    first_name: str,
    last_name: str,
    maiden_name: str | None = None,
    birth_date: str | None = None,
) -> tuple[Graph, URIRef]:
    """Add a person to the graph."""
    person_uri = self.get_person_uri_from_linkedin_profile_page_uri(
        linkedin_profile_page_uri
    )
    if person_uri is None:
        # If no such person, create the new person as before
        def parse_birth_date(birth_date_str: str) -> str:
            """Convert a birth date string (e.g., 'Aug 18, 1992') to 'YYYY-MM-DD' format."""
            from datetime import datetime

            try:
                if birth_date_str:
                    # Common LinkedIn export format: 'Aug 18, 1992'
                    date_obj = datetime.strptime(birth_date_str, "%b %d, %Y").replace(tzinfo=UTC)
                    return date_obj.strftime("%Y-%m-%d")
            except Exception:  # noqa: BLE001,S110
                pass
            return ""

        person_name = f"{first_name} {last_name}"
        logger.debug(f"Step 3.3: Adding person '{person_name}'")
        person_uri = ABI[str(uuid.uuid4())]
        graph.add((person_uri, RDF.type, OWL.NamedIndividual))
        graph.add((person_uri, RDF.type, PERSON))
        graph.add((person_uri, RDFS.label, Literal(person_name)))
        graph.add((person_uri, ABI.first_name, Literal(first_name)))
        graph.add((person_uri, ABI.last_name, Literal(last_name)))
        if maiden_name:
            graph.add((person_uri, ABI.maiden_name, Literal(maiden_name)))
        if birth_date:
            birth_date = parse_birth_date(birth_date)
            graph.add(
                (person_uri, ABI.birth_date, Literal(birth_date, datatype=XSD.date))
            )
        graph.add(
            (person_uri, ABI.hasBackingDataSource, backing_datasource_component_uri)
        )
        graph.add((linkedin_profile_page_uri, ABI.isLinkedInPageOf, person_uri))
        graph.add((person_uri, ABI.hasLinkedInPage, linkedin_profile_page_uri))

    return graph, URIRef(person_uri)
