# Context shim (see meta.json): subset of kgraphpy/namespaces.py from
# statnett/KGraphPy@38859be62fdc2fd048e3ad1651bc16f0dcabaf75, so the region
# executes outside the package. Identical bindings for both representations.
# Only MD (the namespace the test parametrizes over) and the helper that
# from_graph() calls to bind namespaces on the extracted header graph are
# kept; the rest of the real file (CIM/EU/DCAT_EXT/... namespaces) is not
# reachable from this region.
from rdflib import Namespace, URIRef
from rdflib.namespace import NamespaceManager, DefinedNamespace
from typing import Iterable


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


def collect_specific_namespaces(triples, namespace_manager: NamespaceManager) -> dict:
    """Collect namespaces used in a list of triples."""
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
