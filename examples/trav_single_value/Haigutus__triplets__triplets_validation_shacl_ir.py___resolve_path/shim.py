# Context shim (see meta.json): the two helpers `_resolve_path` calls,
# copied verbatim from triplets/validation/shacl_ir.py in
# Haigutus/triplets@7cf62970e8, so the region executes outside its module.
# Identical bindings for both representations.
def _rdf_list(graph, head, transform):
    from rdflib.collection import Collection
    return [transform(item) for item in Collection(graph, head)]


def _local(term):
    """IRI -> local name (matches the short KEY/VALUE names in triplet data)."""
    return str(term).split("#")[-1].split("/")[-1]
