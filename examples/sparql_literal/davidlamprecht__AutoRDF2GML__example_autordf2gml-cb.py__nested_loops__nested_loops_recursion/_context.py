# Context shim (see meta.json): `create_sparql_query`, copied verbatim from
# the same source file (davidlamprecht/AutoRDF2GML@729b5c5387 :
# example/autordf2gml-cb.py, lines 592-608). It is the function that builds
# the SPARQL text `_nested_loops_recursion` hands to `graph.query()` — a
# plain string-building helper, not itself an RDF operation, and not part of
# the extracted region. Identical for both representations (imported as-is
# by original.py and translated.ldpy).
def create_sparql_query(current_combination, class_a, class_x):
    triples = ""
    prev_var = "?a"
    for i, prop in enumerate(current_combination):
        var = f"?c{i+1}" if i < len(current_combination) - 1 else "?x"
        triples += f"{prev_var} <{prop}> {var} .\n"
        prev_var = var

    query_a = f"""
        SELECT DISTINCT ?a ?x
        WHERE {{
            ?a rdf:type <{class_a}> .
            ?x rdf:type <{class_x}> .
            {triples}
        }}
    """
    return query_a
