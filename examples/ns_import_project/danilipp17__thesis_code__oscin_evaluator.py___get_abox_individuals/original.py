# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/evaluator.py
# region: _get_abox_individuals (lines 159-170, stratum ns_import_project)
# licence of the source repository: see meta.json
from collections import defaultdict
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
from oscin.namespaces import AGENTOSCIN, is_ontology_uri
TBOX_TYPES = {
    OWL.Class,
    OWL.ObjectProperty,
    OWL.DatatypeProperty,
    OWL.Ontology,
    OWL.AllDisjointClasses,
}

def _get_abox_individuals(g: Graph) -> dict[str, set[str]]:
    """
    Get all ABox individuals grouped by class type.
    Returns {class_name: {individual_local_name, ...}}.
    """
    result: dict[str, set[str]] = defaultdict(set)
    for s, _, o in g.triples((None, RDF.type, None)):
        if o in TBOX_TYPES:
            continue
        if isinstance(s, URIRef) and not is_ontology_uri(s):
            result[_class_name(o)].add(_local_name(s))
    return dict(result)
