# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/applications/linkedin/pipelines/LinkedInExportConnectionsPipeline.py
# region: LinkedInExportConnectionsPipeline.generate_graph_date (lines 132-149, stratum ns_import_project)
# licence of the source repository: see meta.json
from datetime import UTC, datetime
from naas_abi_core.utils.Graph import ABI, BFO, CCO
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

def generate_graph_date(
    self, date: datetime | str, date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"
) -> tuple[URIRef, Graph]:
    """Generates a URI for a date based on the given datetime object."""
    if isinstance(date, datetime):
        date_str = date.strftime(date_format)
        date_epoch = int(date.timestamp() * 1000)
        date_uri = ABI[str(date_epoch)]  # Create URI using timestamp
        date_literal = Literal(date_str, datatype=XSD.dateTime)
    elif isinstance(date, str):
        date_str = date
        date_uri = ABI[date_str]
        date_literal = Literal(date_str)
    graph = Graph()
    graph.add((date_uri, RDF.type, OWL.NamedIndividual))
    graph.add((date_uri, RDF.type, ABI.ISO8601UTCDateTime))
    graph.add((date_uri, RDFS.label, date_literal))
    return date_uri, graph
