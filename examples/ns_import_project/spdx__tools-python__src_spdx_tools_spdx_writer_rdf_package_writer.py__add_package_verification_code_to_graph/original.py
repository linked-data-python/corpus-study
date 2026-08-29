# Extracted from spdx/tools-python@cef432adee : src/spdx_tools/spdx/writer/rdf/package_writer.py
# region: add_package_verification_code_to_graph (lines 74-97, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import DOAP, RDF, RDFS, XSD, BNode, Graph, Literal, URIRef
from spdx_tools.spdx.model import ExternalPackageRef, Package, PackageVerificationCode
from spdx_tools.spdx.rdfschema.namespace import REFERENCE_NAMESPACE, SPDX_NAMESPACE

def add_package_verification_code_to_graph(
    package_verification_code: PackageVerificationCode, graph: Graph, package_node: URIRef
):
    if not package_verification_code:
        return
    package_verification_code_node = BNode()
    graph.add((package_verification_code_node, RDF.type, SPDX_NAMESPACE.PackageVerificationCode))
    graph.add(
        (
            package_verification_code_node,
            SPDX_NAMESPACE.packageVerificationCodeValue,
            Literal(package_verification_code.value),
        )
    )
    for excluded_file in package_verification_code.excluded_files:
        graph.add(
            (
                package_verification_code_node,
                SPDX_NAMESPACE.packageVerificationCodeExcludedFile,
                Literal(excluded_file),
            )
        )

    graph.add((package_node, SPDX_NAMESPACE.packageVerificationCode, package_verification_code_node))
