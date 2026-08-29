# Extracted from davidlamprecht/AutoRDF2GML@729b5c5387 : example/autordf2gml-cb.py
# region: nested_loops._nested_loops_recursion (lines 577-587, stratum sparql_literal)
# licence of the source repository: see meta.json
# `create_sparql_query` (same file, lines 592-608) is restored context, see
# meta.json and _context.py. In the real file _nested_loops_recursion is
# nested inside nested_loops(list_of_lists, result_list, class_a, class_x)
# and closes over `result_list`, `class_a`, `class_x` as free variables, plus
# the module-level `graph`; extracted on its own it has no parameter for any
# of them, so they are restored here as module-level assignments — the same
# free-variable resolution, just not routed through an enclosing call.
# `graph` additionally needs real data for the region to do something beyond
# "did not crash" (see meta.json for why this region cannot use s{ } at all).
import rdflib
from _context import create_sparql_query

graph = rdflib.Graph()
graph.parse(data="""
    @prefix ex: <http://example.org/> .
    ex:a1 a ex:A ; ex:p1 ex:mid1 .
    ex:mid1 ex:p2 ex:x1 .
    ex:x1 a ex:X .
    ex:a2 a ex:A .
""", format="turtle")

class_a = "http://example.org/A"
class_x = "http://example.org/X"
result_list = []


def _nested_loops_recursion(lists, current_combination):
    if not lists:
        query_a = create_sparql_query(current_combination, class_a, class_x)

        for row in graph.query(query_a):
            result_list.append(row)

        return

    for item in lists[0]:
        _nested_loops_recursion(lists[1:], current_combination + [item])


_nested_loops_recursion([["http://example.org/p1"], ["http://example.org/p2"]], [])
