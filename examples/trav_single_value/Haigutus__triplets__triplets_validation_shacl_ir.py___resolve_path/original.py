# Extracted from Haigutus/triplets@7cf62970e8 : triplets/validation/shacl_ir.py
# region: _resolve_path (lines 412-440, stratum trav_single_value)
# licence of the source repository: see meta.json
from shim import _local, _rdf_list  # context shim -- see meta.json

def _resolve_path(graph, SH, path_node):
    """Resolve sh:path → (KEY name, inverse, via_type); handles sh:inversePath,
    sh:alternativePath with a nested inverse, and the two-step sequence
    ``( assoc rdf:type )`` (the profile "valueType" pattern — the constraint
    applies to the type of the referenced object, via_type=True). Any other
    blank-node path (longer sequences, zeroOrMorePath, ...) spans more than
    one KEY and cannot be expressed as an IR row → (None, False, False);
    callers skip the shape."""
    import rdflib

    if path_node is None:
        return None, False, False
    if isinstance(path_node, rdflib.URIRef):
        return _local(path_node), False, False
    inverse = graph.value(path_node, SH.inversePath)
    if inverse is not None:
        return _local(inverse), True, False
    alternative = graph.value(path_node, SH.alternativePath)
    if alternative is not None:
        for item in _rdf_list(graph, alternative, lambda node: node):
            nested_inverse = graph.value(item, SH.inversePath)
            if nested_inverse is not None:
                return _local(nested_inverse), True, False
    if graph.value(path_node, rdflib.RDF.first) is not None:   # sequence path
        steps = _rdf_list(graph, path_node, lambda node: node)
        if (len(steps) == 2 and isinstance(steps[0], rdflib.URIRef)
                and steps[1] == rdflib.RDF.type):
            return _local(steps[0]), False, True
    return None, False, False
