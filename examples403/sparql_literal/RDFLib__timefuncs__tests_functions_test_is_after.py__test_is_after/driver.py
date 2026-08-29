"""Validation driver for RDFLib__timefuncs__tests_functions_test_is_after.py__test_is_after.

This region reads a graph (design record corpus/405), but `test_is_after`
takes no argument: it builds its own graph from a fixed relative path
(`tests_dir / "data" / "after.ttl"`, restored verbatim at `data/after.ttl` --
see meta.json), so run_pair's `fixture=` mechanism (which injects ONE parsed
graph as the entry point's sole argument) does not apply here, the same
situation as lazlop/semantic_objects's `test_class_scope_or_roundtrip` in
this same stratum. `calls=[((), {})]` calls the entry point with no
arguments, once per side.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_is_after',
    calls=[((), {})],
)
