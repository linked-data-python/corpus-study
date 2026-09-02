"""Validation driver for Blackcat-Informatics__purrdf__bindings_python_tests_rdflib_suite_vendor_test_subselect.py__test_select_star_multiple_sub_select_star.

This region reads a graph (design record corpus/405), but
`test_select_star_multiple_sub_select_star` takes no argument: it queries a
fixed module-level graph (`_graph_with_label`, populated by a `.add(...)`
call restored from the real file -- see original.py/translated.ldpy
headers), so run_pair's `fixture=` mechanism (which injects ONE parsed
graph as the entry point's sole argument) does not apply here -- the same
situation as lazlop/semantic_objects's `test_class_scope_or_roundtrip` and
RDFLib/timefuncs's `test_is_after` in this same stratum. `calls=[((), {})]`
calls the entry point with no arguments, once per side; there is no
fixture.ttl for this region.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_select_star_multiple_sub_select_star',
    calls=[((), {})],
)
