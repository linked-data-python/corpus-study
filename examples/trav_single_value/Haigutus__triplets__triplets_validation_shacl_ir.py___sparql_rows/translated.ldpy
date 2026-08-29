# Extracted from Haigutus/triplets@7cf62970e8 : triplets/validation/shacl_ir.py
# region: _sparql_rows (lines 357-385, stratum trav_single_value)
# licence of the source repository: see meta.json
def _sparql_rows(graph, SH, shape_uri, meta):
    """sh:sparql constraints. params carries everything an engine needs to run
    the query without rdflib:

        {"select":   SELECT text ($this / $PATH placeholders kept),
         "prefixes": resolved "PREFIX ..." header lines (sh:prefixes → sh:declare),
         "path":     full IRI of the owning shape's sh:path, or None}

    The sparql node's own sh:message overrides the shape's.
    """
    rows = []
    path = graph.value(shape_uri, SH.path)
    for sparql in graph.objects(shape_uri, SH.sparql):
        select = graph.value(sparql, SH.select)
        if select is None:
            continue
        prefixes = "".join(
            f"PREFIX {graph.value(declaration, SH.prefix)}: <{graph.value(declaration, SH.namespace)}>\n"
            for ontology in graph.objects(sparql, SH.prefixes)
            for declaration in graph.objects(ontology, SH.declare))
        message = graph.value(sparql, SH.message)
        row = {**meta, "component": "sh:sparql",
               "params": {"select": str(select), "prefixes": prefixes,
                          # $PATH substitution needs the full IRI; only direct paths qualify
                          "path": str(path) if type(path).__name__ == "URIRef" else None}}
        if message is not None:
            row["message"] = str(message)
        rows.append(row)
    return rows
