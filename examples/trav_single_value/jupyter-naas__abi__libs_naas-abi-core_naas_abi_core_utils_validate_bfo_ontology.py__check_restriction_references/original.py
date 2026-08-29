# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py
# region: check_restriction_references (lines 653-716, stratum trav_single_value)
# licence of the source repository: see meta.json
#
# The extracted region had no imports at all: Graph, OWL, RDF, RDFS, URIRef
# and the five helpers (_short, _label, _own_namespaces, _named_classes,
# _named_object_properties) are module-level names of
# validate_bfo_ontology.py that the region's own lines never declare.
# Restored here -- OWL/RDF/RDFS/URIRef/Graph from rdflib itself, the five
# helpers from the context shim (see meta.json).
from rdflib import Graph, OWL, RDF, RDFS, URIRef
from naas_context import _short, _label, _own_namespaces, _named_classes, _named_object_properties

_VOCAB_PREFIXES_FOR_RESTRICTIONS = (
    "http://purl.obolibrary.org/obo/",
    "http://www.w3.org/2001/XMLSchema#",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "http://www.w3.org/2000/01/rdf-schema#",
    "http://www.w3.org/2002/07/owl#",
    "http://www.w3.org/2004/02/skos/core#",
    "https://www.commoncoreontologies.org/",
)

def check_restriction_references(g: Graph) -> list[dict]:
    issues = []
    own_namespaces = _own_namespaces(g)
    declared_classes = set(_named_classes(g))
    declared_properties = set(_named_object_properties(g))
    declared_data_properties = {
        s for s in g.subjects(RDF.type, OWL.DatatypeProperty) if isinstance(s, URIRef)
    }

    def _severity(iri: URIRef) -> str:
        """ERROR for a dangling reference, WARNING for a sibling-file one."""
        text = str(iri)
        if any(text.startswith(ns) for ns in own_namespaces):
            return "WARNING"
        return "ERROR"

    def _is_known(iri: URIRef) -> bool:
        s = str(iri)
        if any(s.startswith(p) for p in _VOCAB_PREFIXES_FOR_RESTRICTIONS):
            return True
        return (
            iri in declared_classes
            or iri in declared_properties
            or iri in declared_data_properties
            or (iri, RDF.type, None) in g
        )

    for bnode in g.subjects(RDF.type, OWL.Restriction):
        on_prop = g.value(bnode, OWL.onProperty)
        if isinstance(on_prop, URIRef) and not _is_known(on_prop):
            owner = g.value(None, RDFS.subClassOf, bnode)
            if owner is None:
                continue
            issues.append(
                {
                    "severity": _severity(on_prop),
                    "category": "RESTRICTION_REF",
                    "subject": _short(owner, g) if owner else "unknown",
                    "message": (
                        f"Restriction on class '{_label(URIRef(str(owner)), g) if owner else '?'}' "
                        f"references undeclared property '{_short(on_prop, g)}'."
                    ),
                }
            )

        for filler_pred in (OWL.allValuesFrom, OWL.someValuesFrom):
            filler = g.value(bnode, filler_pred)
            if isinstance(filler, URIRef) and not _is_known(filler):
                owner = g.value(None, RDFS.subClassOf, bnode)
                if owner is None:
                    continue
                issues.append(
                    {
                        "severity": _severity(filler),
                        "category": "RESTRICTION_REF",
                    "subject": _short(owner, g) if owner else "unknown",
                    "message": (
                        f"Restriction on class '{_label(URIRef(str(owner)), g) if owner else '?'}' "
                        f"references undeclared class '{_short(filler, g)}' "
                            f"in {_short(filler_pred, g)}."
                        ),
                    }
                )
    return issues
