# Extracted from spdx/tools-python@cef432adee : src/spdx_tools/spdx/writer/rdf/external_document_ref_writer.py
# region: <module> (lines 1-21, stratum ns_import_project)
# licence of the source repository: see meta.json
# SPDX-FileCopyrightText: 2023 spdx contributors
#
# SPDX-License-Identifier: Apache-2.0
from rdflib import RDF, Graph, URIRef

from spdx_context import ExternalDocumentRef  # spdx_tools.spdx.model
from spdx_context import SPDX_NAMESPACE  # spdx_tools.spdx.rdfschema.namespace
from spdx_context import add_checksum_to_graph  # spdx_tools.spdx.writer.rdf.checksum_writer


def add_external_document_ref_to_graph(
    external_document_ref: ExternalDocumentRef, graph: Graph, doc_node: URIRef, doc_namespace: str
):
    external_document_ref_resource = URIRef(f"{doc_namespace}#{external_document_ref.document_ref_id}")
    graph.add((external_document_ref_resource, RDF.type, SPDX_NAMESPACE.ExternalDocumentRef))
    graph.add(
        (external_document_ref_resource, SPDX_NAMESPACE.spdxDocument, URIRef(external_document_ref.document_uri))
    )
    graph.add((doc_node, SPDX_NAMESPACE.externalDocumentRef, external_document_ref_resource))
    add_checksum_to_graph(external_document_ref.checksum, graph, external_document_ref_resource)
