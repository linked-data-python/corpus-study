# Context shim (see meta.json): the subset of spdx-tools 0.8.5 (spdx/tools-python,
# cef432adee) that external_document_ref_writer.py imports, so the region
# executes without installing spdx-tools and its eight dependencies.
# Identical bindings for both representations.
#
#   * SPDX_NAMESPACE: spdx_tools/spdx/rdfschema/namespace.py, verbatim.
#   * Checksum, ChecksumAlgorithm, ExternalDocumentRef: spdx_tools/spdx/model/,
#     plain dataclasses (the original adds a runtime type check on __init__).
#   * add_checksum_to_graph, algorithm_to_rdf_string:
#     spdx_tools/spdx/writer/rdf/checksum_writer.py, verbatim.
from dataclasses import dataclass
from enum import Enum, auto

from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef

SPDX_NAMESPACE = Namespace("http://spdx.org/rdf/terms#")


class ChecksumAlgorithm(Enum):
    SHA1 = auto()
    SHA224 = auto()
    SHA256 = auto()
    SHA384 = auto()
    SHA512 = auto()
    SHA3_256 = auto()
    SHA3_384 = auto()
    SHA3_512 = auto()
    BLAKE2B_256 = auto()
    BLAKE2B_384 = auto()
    BLAKE2B_512 = auto()
    BLAKE3 = auto()
    MD2 = auto()
    MD4 = auto()
    MD5 = auto()
    MD6 = auto()
    ADLER32 = auto()


@dataclass
class Checksum:
    algorithm: ChecksumAlgorithm
    value: str


@dataclass
class ExternalDocumentRef:
    document_ref_id: str  # of the form "DocumentRef-[idstring]"
    document_uri: str
    checksum: Checksum


def add_checksum_to_graph(checksum: Checksum, graph: Graph, parent: URIRef):
    checksum_node = BNode()
    graph.add((checksum_node, RDF.type, SPDX_NAMESPACE.Checksum))
    graph.add((checksum_node, SPDX_NAMESPACE.algorithm, algorithm_to_rdf_string(checksum.algorithm)))
    graph.add((checksum_node, SPDX_NAMESPACE.checksumValue, Literal(checksum.value)))

    graph.add((parent, SPDX_NAMESPACE.checksum, checksum_node))


def algorithm_to_rdf_string(algorithm: ChecksumAlgorithm) -> URIRef:
    if "BLAKE2B" in algorithm.name:
        algorithm_rdf_string = algorithm.name.replace("_", "").lower()
    else:
        algorithm_rdf_string = algorithm.name.lower()

    return SPDX_NAMESPACE[f"checksumAlgorithm_{algorithm_rdf_string}"]
