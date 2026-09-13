# Context shim (see meta.json): minimal, faithful subset of
# statnett/KGraphPy@38859be62f : kgraphpy/namespaces.py, so the region
# executes outside the package. Identical bindings for both representations.
#
# Trimmed to what CIMMetadataHeader.from_manifest actually reaches: the MD
# namespace (used only by DEFAULT_PROFILE_PREDICATES elsewhere in header.py,
# not by the extracted lines themselves) and collect_specific_namespaces,
# which the region calls directly. The other namespace constants (CIM, EU,
# MODEL, ...), DCAT_EXT and the namespace-repair helpers are dropped: nothing
# in the extracted region reaches them.

from rdflib import Namespace, URIRef
from rdflib.namespace import DefinedNamespace, NamespaceManager
from typing import Iterable
from rdflib.term import Node


class _MDModelNamespace:
    def __init__(self, ns):
        self._ns = ns

    def __getattr__(self, name):
        return URIRef(self._ns[f"Model.{name}"])


class MD(DefinedNamespace):
    _NS = Namespace("http://iec.ch/TC57/61970-552/ModelDescription/1#")

    FullModel = _NS["FullModel"]
    Model = _MDModelNamespace(_NS)

    _extras = [
        "Model.profile",
        "Model.description",
        "Model.version",
        "Model.created",
        "Model.scenarioTime",
        "Model.modelingAuthoritySet",
        "Model.DependentOn",
        "Model.Supersedes",
    ]


def collect_specific_namespaces(triples: Iterable[tuple[Node, Node, Node]],
                                 namespace_manager: NamespaceManager) -> dict[str, URIRef]:
    """Collect namespaces used in a list of triples.

    Parameters:
        triples (Iterable[tuple[Node, Node, Node]]): The list of triples.
        namespace_manager (NamespaceManager): source of known namespaces.

    Returns:
        dict[str, URIRef]: the namespaces as prefix: namespace.
    """
    used_uris = set()
    for s, p, o in triples:
        for term in (s, p, o):
            if isinstance(term, URIRef):
                used_uris.add(str(term))

    known = sorted(namespace_manager.namespaces(), key=lambda item: len(str(item[1])), reverse=True)

    used = {}
    for uri in used_uris:
        for prefix, ns_uri in known:
            ns_str = str(ns_uri)
            if uri.startswith(ns_str):
                used[prefix] = ns_uri
                break

    return used
