# Extracted from Haigutus/triplets@7cf62970e8 : triplets/validation/shacl_ir.py
# region: _node_rows (lines 249-271, stratum trav_single_value)
# licence of the source repository: see meta.json
def _node_rows(graph, SH, shape, target_class, target_kind="class"):
    """NodeShape-level constraints (closed, sparql) + its property shapes' rows."""
    meta = _shape_meta(graph, SH, shape, target_class, path=None, inverse=False,
                       target_kind=target_kind)
    rows = []

    closed = graph.value(shape, SH.closed)
    if closed is not None and closed.toPython() is True:
        # params = the complete allowed list, resolved at compile time:
        # sh:ignoredProperties + every (non-inverse) sh:property path of THIS shape
        ignored = graph.value(shape, SH.ignoredProperties)
        allowed = _rdf_list(graph, ignored, _local) if ignored is not None else []
        for property_shape in graph.objects(shape, SH.property):
            path, inverse, _ = _resolve_path(graph, SH, graph.value(property_shape, SH.path))
            if path is not None and not inverse:
                allowed.append(path)
        rows.append({**meta, "component": "sh:closed", "params": allowed})

    rows.extend(_sparql_rows(graph, SH, shape, meta))
    for property_shape in graph.objects(shape, SH.property):
        rows.extend(_shape_rows(graph, SH, property_shape, target_class, parent=meta,
                                target_kind=target_kind))
    return rows
