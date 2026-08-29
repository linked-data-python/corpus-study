# Context shim (see meta.json): subset of
# libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py (_short,
# _label, _own_namespaces, _named_classes, _named_object_properties) from
# jupyter-naas/abi@3fb7f5304d, so the region executes without the module's
# other ~1800 lines (argparse CLI, BFO bucket tables, the rest of the
# checks). Identical bindings for both representations.
from typing import Any

from rdflib import BNode, Graph, OWL, RDF, RDFS, URIRef


def _short(iri: Any, g: Graph) -> str:
    if isinstance(iri, BNode):
        return "_:bnode"
    try:
        return g.namespace_manager.qname(iri)
    except Exception:  # noqa: BLE001
        s = str(iri)
        return s.split("/")[-1].split("#")[-1]


def _label(iri: Any, g: Graph) -> str:
    if not isinstance(iri, (URIRef, BNode)):
        return str(iri) if iri is not None else "?"
    lbl = g.value(iri, RDFS.label) if isinstance(iri, URIRef) else None
    if lbl:
        return str(lbl)
    return _short(iri, g)


def _named_classes(g: Graph) -> list[URIRef]:
    return [s for s in g.subjects(RDF.type, OWL.Class) if isinstance(s, URIRef)]


def _named_object_properties(g: Graph) -> list[URIRef]:
    return [
        s for s in g.subjects(RDF.type, OWL.ObjectProperty) if isinstance(s, URIRef)
    ]


def _own_namespaces(g: Graph) -> set[str]:
    """Namespaces of the owl:Ontology subjects declared in this file."""
    namespaces = set()
    for subject in g.subjects(RDF.type, OWL.Ontology):
        if not isinstance(subject, URIRef):
            continue
        text = str(subject)
        cut = max(text.rfind("/"), text.rfind("#"))
        if cut > 0:
            namespaces.add(text[: cut + 1])
    return namespaces
