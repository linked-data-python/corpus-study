# Context shim (see meta.json): what the region imports from
# spdx/tools-python@cef432adee (spdx_tools is not installed, and needs
# beartype, license_expression and boolean.py), so that it executes outside the
# package. Identical bindings for both representations.
#
#   * the namespaces: verbatim from spdx_tools/spdx/rdfschema/namespace.py.
#   * add_file_to_graph, add_namespace_to_spdx_id, add_optional_literal,
#     add_checksum_to_graph, algorithm_to_rdf_string, snake_case_to_camel_case,
#     is_valid_internal_spdx_id: verbatim bodies from the writer modules.
#   * the license-expression writer: the same dispatch as
#     spdx_tools/spdx/writer/rdf/license_expression_writer.py, over a minimal
#     stand-in for the license_expression objects (LicenseSymbol, AND, OR) and
#     for spdx_licensing.validate (a symbol is "on the SPDX list" when its key
#     is in _SPDX_LIST). The exception-symbol branch (WITH) is left out: no
#     fixture of the region reaches it.
#   * File, Checksum, FileType, ChecksumAlgorithm, SpdxNoAssertion, SpdxNone:
#     plain dataclasses / classes with the fields and values of the model.
#   * file_fixture and checksum_fixture: tests/spdx/fixtures.py, with
#     spdx_licensing.parse("MIT and GPL-2.0") replaced by the object it
#     returns (AND of the symbols MIT and GPL-2.0-only, the id the parser
#     normalises "GPL-2.0" to) and likewise parse("MIT"), parse("GPL-2.0").
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from re import match, sub
from typing import Any, Dict, List, Optional

from rdflib import RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
from rdflib.term import Node

SPDX_NAMESPACE = Namespace("http://spdx.org/rdf/terms#")
POINTER_NAMESPACE = Namespace("http://www.w3.org/2009/pointers#")
REFERENCE_NAMESPACE = Namespace("http://spdx.org/rdf/references/")
LICENSE_NAMESPACE = Namespace("http://spdx.org/licenses/")


# --- the model --------------------------------------------------------------

class SpdxNoAssertion:
    def __str__(self):
        return "NOASSERTION"

    def __repr__(self):
        return "NOASSERTION"

    def __eq__(self, other):
        return isinstance(other, SpdxNoAssertion)


class SpdxNone:
    def __str__(self):
        return "NONE"

    def __repr__(self):
        return "NONE"

    def __eq__(self, other):
        return isinstance(other, SpdxNone)


class FileType(Enum):
    SOURCE = auto()
    BINARY = auto()
    ARCHIVE = auto()
    APPLICATION = auto()
    AUDIO = auto()
    IMAGE = auto()
    TEXT = auto()
    VIDEO = auto()
    DOCUMENTATION = auto()
    SPDX = auto()
    OTHER = auto()


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
class File:
    name: str
    spdx_id: str
    checksums: List[Checksum]
    file_types: List[FileType] = field(default_factory=list)
    license_concluded: Any = None
    license_info_in_file: List[Any] = field(default_factory=list)
    license_comment: Optional[str] = None
    copyright_text: Optional[Any] = None
    comment: Optional[str] = None
    notice: Optional[str] = None
    contributors: List[str] = field(default_factory=list)
    attribution_texts: List[str] = field(default_factory=list)


# --- stand-in for license_expression ----------------------------------------

class LicenseExpression:
    pass


class LicenseSymbol(LicenseExpression):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return self.key


class AND(LicenseExpression):
    def __init__(self, *args):
        self.args = args


class OR(LicenseExpression):
    def __init__(self, *args):
        self.args = args


_SPDX_LIST = {"MIT", "GPL-2.0-only", "Apache-2.0", "BSD-3-Clause"}


# --- the writer -------------------------------------------------------------

def snake_case_to_camel_case(snake_case_string: str) -> str:
    each_word_capitalized = sub(r"[_\-]+", " ", snake_case_string).title().replace(" ", "")
    return each_word_capitalized[0].lower() + each_word_capitalized[1:]


def is_valid_internal_spdx_id(spdx_id: str) -> bool:
    return bool(match(r"^SPDXRef-[\da-zA-Z.-]+$", spdx_id))


def add_optional_literal(value: Any, graph: Graph, parent: Node, predicate: Node):
    if value is None:
        return
    if isinstance(value, list):
        for element in value:
            graph.add((parent, predicate, Literal(str(element))))
        return
    graph.add((parent, predicate, Literal(str(value))))


def add_namespace_to_spdx_id(spdx_id: str, doc_namespace: str, external_doc_namespaces: Dict[str, str]) -> str:
    if ":" in spdx_id:
        external_doc_ref_id = spdx_id.split(":")[0]
        if external_doc_ref_id not in external_doc_namespaces.keys():
            logging.warning(f"No namespace for external document reference with id {external_doc_ref_id} provided.")
            return spdx_id
        return f"{external_doc_namespaces[external_doc_ref_id]}#{spdx_id.split(':')[1]}"

    if is_valid_internal_spdx_id(spdx_id):
        return f"{doc_namespace}#{spdx_id}"

    return spdx_id


def algorithm_to_rdf_string(algorithm: ChecksumAlgorithm) -> URIRef:
    if "BLAKE2B" in algorithm.name:
        algorithm_rdf_string = algorithm.name.replace("_", "").lower()
    else:
        algorithm_rdf_string = algorithm.name.lower()

    return SPDX_NAMESPACE[f"checksumAlgorithm_{algorithm_rdf_string}"]


def add_checksum_to_graph(checksum: Checksum, graph: Graph, parent: URIRef):
    checksum_node = BNode()
    graph.add((checksum_node, RDF.type, SPDX_NAMESPACE.Checksum))
    graph.add((checksum_node, SPDX_NAMESPACE.algorithm, algorithm_to_rdf_string(checksum.algorithm)))
    graph.add((checksum_node, SPDX_NAMESPACE.checksumValue, Literal(checksum.value)))

    graph.add((parent, SPDX_NAMESPACE.checksum, checksum_node))


def license_or_exception_is_on_spdx_licensing_list(license_symbol: LicenseSymbol) -> bool:
    return str(license_symbol) in _SPDX_LIST


def add_license_expression_to_graph(
    license_expression, graph: Graph, parent: Node, predicate: Node, doc_namespace: str
):
    if isinstance(license_expression, AND):
        member_node = BNode()
        graph.add((member_node, RDF.type, SPDX_NAMESPACE.ConjunctiveLicenseSet))
        graph.add((parent, predicate, member_node))
        for arg in license_expression.args:
            add_license_expression_to_graph(arg, graph, member_node, SPDX_NAMESPACE.member, doc_namespace)
    if isinstance(license_expression, OR):
        member_node = BNode()
        graph.add((member_node, RDF.type, SPDX_NAMESPACE.DisjunctiveLicenseSet))
        graph.add((parent, predicate, member_node))
        for arg in license_expression.args:
            add_license_expression_to_graph(arg, graph, member_node, SPDX_NAMESPACE.member, doc_namespace)
    if isinstance(license_expression, LicenseSymbol):
        if license_or_exception_is_on_spdx_licensing_list(license_expression):
            graph.add((parent, predicate, LICENSE_NAMESPACE[str(license_expression)]))
        else:
            # assuming that the license expression is a LicenseRef to an instance of ExtractedLicensingInfo
            graph.add((parent, predicate, URIRef(f"{doc_namespace}#{license_expression}")))


def add_license_expression_or_none_or_no_assertion(
    value, graph: Graph, parent: Node, predicate: Node, doc_namespace: str,
):
    if isinstance(value, SpdxNoAssertion):
        graph.add((parent, predicate, SPDX_NAMESPACE.noassertion))
        return
    if isinstance(value, SpdxNone):
        graph.add((parent, predicate, SPDX_NAMESPACE.none))
        return
    if isinstance(value, list):
        for license_expression in value:
            add_license_expression_or_none_or_no_assertion(license_expression, graph, parent, predicate, doc_namespace)
    if isinstance(value, LicenseExpression):
        add_license_expression_to_graph(value, graph, parent, predicate, doc_namespace)


def add_file_to_graph(file: File, graph: Graph, doc_namespace: str, external_doc_ref_to_namespace: Dict[str, str]):
    file_resource = URIRef(add_namespace_to_spdx_id(file.spdx_id, doc_namespace, external_doc_ref_to_namespace))
    graph.add((file_resource, RDF.type, SPDX_NAMESPACE.File))
    graph.add((file_resource, SPDX_NAMESPACE.fileName, Literal(file.name)))
    for file_type in file.file_types:
        graph.add(
            (
                file_resource,
                SPDX_NAMESPACE.fileType,
                SPDX_NAMESPACE[f"fileType_{snake_case_to_camel_case(file_type.name)}"],
            )
        )

    for checksum in file.checksums:
        add_checksum_to_graph(checksum, graph, file_resource)

    add_license_expression_or_none_or_no_assertion(
        file.license_concluded, graph, file_resource, SPDX_NAMESPACE.licenseConcluded, doc_namespace
    )
    add_license_expression_or_none_or_no_assertion(
        file.license_info_in_file, graph, file_resource, SPDX_NAMESPACE.licenseInfoInFile, doc_namespace
    )

    add_optional_literal(file.license_comment, graph, file_resource, SPDX_NAMESPACE.licenseComments)
    add_optional_literal(file.copyright_text, graph, file_resource, SPDX_NAMESPACE.copyrightText)
    add_optional_literal(file.comment, graph, file_resource, RDFS.comment)
    add_optional_literal(file.notice, graph, file_resource, SPDX_NAMESPACE.noticeText)
    for contributor in file.contributors:
        graph.add((file_resource, SPDX_NAMESPACE.fileContributor, Literal(contributor)))
    for attribution_text in file.attribution_texts:
        graph.add((file_resource, SPDX_NAMESPACE.attributionText, Literal(attribution_text)))


# --- tests/spdx/fixtures.py -------------------------------------------------

def checksum_fixture(algorithm=ChecksumAlgorithm.SHA1, value="71c4025dd9897b364f3ebbb42c484ff43d00791c") -> Checksum:
    return Checksum(algorithm, value)


def file_fixture(
    name="./fileName.py",
    spdx_id="SPDXRef-File",
    checksums=None,
    file_types=None,
    license_concluded=AND(LicenseSymbol("MIT"), LicenseSymbol("GPL-2.0-only")),
    license_info_in_file=None,
    license_comment="licenseComment",
    copyright_text="copyrightText",
    comment="fileComment",
    notice="fileNotice",
    contributors=None,
    attribution_texts=None,
) -> File:
    checksums = [checksum_fixture()] if checksums is None else checksums
    file_types = [FileType.TEXT] if file_types is None else file_types
    license_info_in_file = (
        [LicenseSymbol("MIT"), LicenseSymbol("GPL-2.0-only"), SpdxNoAssertion()]
        if license_info_in_file is None
        else license_info_in_file
    )
    contributors = ["fileContributor"] if contributors is None else contributors
    attribution_texts = ["fileAttributionText"] if attribution_texts is None else attribution_texts
    return File(
        name=name,
        spdx_id=spdx_id,
        checksums=checksums,
        file_types=file_types,
        license_concluded=license_concluded,
        license_info_in_file=license_info_in_file,
        license_comment=license_comment,
        copyright_text=copyright_text,
        comment=comment,
        notice=notice,
        contributors=contributors,
        attribution_texts=attribution_texts,
    )
