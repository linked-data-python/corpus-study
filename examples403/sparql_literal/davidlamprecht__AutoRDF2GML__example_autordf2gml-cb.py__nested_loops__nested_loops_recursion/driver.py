"""Validation driver for davidlamprecht__AutoRDF2GML__example_autordf2gml-cb.py__nested_loops__nested_loops_recursion.

Establishes semantic equivalence of original.py and translated.ldpy — here,
an identity translation (see meta.json, "not-expressible").

_nested_loops_recursion(lists, current_combination) has no parameter for the
graph it queries, the result list it appends to, or the class IRIs it
queries for: in the real file it is nested inside
nested_loops(list_of_lists, result_list, class_a, class_x) and closes over
all of them. entry=/calls= only compares a call's return value, its
arguments and stdout — a mutated *global* (result_list) is invisible to it.
So this driver uses module-state comparison instead: both files populate
`graph`, `class_a`, `class_x`, `result_list` at module level, call
`_nested_loops_recursion` once at the bottom, and run_pair compares the
resulting `graph` (isomorphism) and `result_list` (values) from each side.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
