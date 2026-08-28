# Extracted from davidlamprecht/AutoRDF2GML@729b5c5387 : example/autordf2gml-cb.py
# region: nested_loops._nested_loops_recursion (lines 577-587, stratum sparql_literal)
# licence of the source repository: see meta.json
graph = rdflib.Graph()

def _nested_loops_recursion(lists, current_combination):
    if not lists:
        query_a = create_sparql_query(current_combination, class_a, class_x)

        for row in graph.query(query_a):
            result_list.append(row)

        return

    for item in lists[0]:
        _nested_loops_recursion(lists[1:], current_combination + [item])
