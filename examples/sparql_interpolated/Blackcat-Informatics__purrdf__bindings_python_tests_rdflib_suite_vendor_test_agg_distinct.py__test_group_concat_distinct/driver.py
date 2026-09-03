"""Validation driver for Blackcat-Informatics__purrdf__bindings_python_tests_rdflib_suite_vendor_test_agg_distinct.py__test_group_concat_distinct.

IDENTITY translation (see meta.json): `query_tpl % "GROUP_CONCAT"` splices
the aggregate function NAME into `(%s(DISTINCT ?z_) as ?z)` -- a syntax
position, not a term, so `s{ }`'s term-position interpolation cannot carry
it (see translation_notes for the argument, and the sibling region
`test_agg_undef.py::template_tst` in this same stratum for the same idiom
with a varying `agg_func` parameter -- here `query_tpl` is the very same
module-level template, reused with a different aggregate name by the
sibling test `test_sum_distinct` in the real file, not extracted here).

`test_group_concat_distinct` takes no argument (all its data comes from the
query's own inline VALUES clause -- there is no external graph, hence no
fixture.ttl content, see that file) and originally only asserts, returning
nothing. `return results` was appended identically to both original.py and
translated.ldpy purely so run_pair has a value to diff (same pattern as
sparql_literal's test_select_star_multiple_sub_select_star and this
stratum's template_tst).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_group_concat_distinct',
    calls=[((), {})],
)
