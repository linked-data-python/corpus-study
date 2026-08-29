# Extracted from spdx/tools-python@cef432adee : src/spdx_tools/spdx/writer/rdf/external_document_ref_writer.py
# region: add_external_document_ref_to_graph (lines 11-21, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, URIRef
from spdx_tools.spdx.model import ExternalDocumentRef
from spdx_tools.spdx.rdfschema.namespace import SPDX_NAMESPACE
from spdx_tools.spdx.writer.rdf.checksum_writer import add_checksum_to_graph

def add_external_document_ref_to_graph(
    external_document_ref: ExternalDocumentRef, graph: Graph, doc_node: URIRef, doc_namespace: str
):
    external_document_ref_resource = URIRef(f"{doc_namespace}#{external_document_ref.document_ref_id}")
    graph.add((external_document_ref_resource, RDF.type, SPDX_NAMESPACE.ExternalDocumentRef))
    graph.add(
        (external_document_ref_resource, SPDX_NAMESPACE.spdxDocument, URIRef(external_document_ref.document_uri))
    )
    add_checksum_to_graph(external_document_ref.checksum, graph, external_document_ref_resource)

    graph.add((doc_node, SPDX_NAMESPACE.externalDocumentRef, external_document_ref_resource))
