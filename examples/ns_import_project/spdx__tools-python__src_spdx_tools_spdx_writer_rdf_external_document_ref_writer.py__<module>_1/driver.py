"""Validation driver for spdx__tools-python__src_spdx_tools_spdx_writer_rdf_external_document_ref_writer.py__<module>_1.

The region is a module with one function that WRITES into the graph it is
given.  The oracle is therefore the mutation of that argument, which the
harness compares by isomorphism (and by prefix bindings) after each call:
the function returns None, so the graph handed in is all there is to see.

Each call builds its own objects (a callable case), so the two sides never
share a graph or a blank node.  The calls cover:

  * a SHA1 checksum into an empty graph;
  * a BLAKE2B_256 checksum (checksum_writer renames that algorithm
    differently), a document namespace with a trailing slash, and a
    graph that already holds other triples -- the neighbours must survive
    and nothing else may be written;
  * a document URI that is relative, and a document ref id with characters
    a prefixed name would not take: the IRIs are built as given.
"""
from rdflib import RDF, Graph, Literal, URIRef

from rdfeval.harness import run_pair


def _doc(ref_id, uri, algo, value):
    from spdx_context import Checksum, ChecksumAlgorithm, ExternalDocumentRef
    return ExternalDocumentRef(ref_id, uri, Checksum(ChecksumAlgorithm[algo], value))


def _empty():
    return ((_doc("DocumentRef-spdx-tool-1.2", "http://example.org/spdx/other.spdx", "SHA1",
                  "d6a770ba38583ed4bb4525bd96e50461655d2759"),
             Graph(), URIRef("http://example.org/spdx/doc#SPDXRef-DOCUMENT"),
             "http://example.org/spdx/doc"), {})


def _busy():
    g = Graph()
    node = URIRef("http://example.org/spdx/doc2#SPDXRef-DOCUMENT")
    g.add((node, RDF.type, URIRef("http://spdx.org/rdf/terms#SpdxDocument")))
    g.add((node, URIRef("http://spdx.org/rdf/terms#name"), Literal("doc 2")))
    g.add((URIRef("http://example.org/spdx/doc2#DocumentRef-old"), RDF.type,
           URIRef("http://spdx.org/rdf/terms#ExternalDocumentRef")))
    return ((_doc("DocumentRef-b2", "https://example.org/spdx/b2.json", "BLAKE2B_256",
                  "0f1e2d"), g, node, "https://example.org/spdx/doc2"), {})


def _odd():
    return ((_doc("DocumentRef-x_y.z", "relative/other.spdx", "SHA3_512", "ABCDEF"),
             Graph(), URIRef("urn:doc:3#SPDXRef-DOCUMENT"), "urn:doc:3"), {})


VERDICT = run_pair(
    __file__,
    entry="add_external_document_ref_to_graph",
    calls=[_empty, _busy, _odd],
)
