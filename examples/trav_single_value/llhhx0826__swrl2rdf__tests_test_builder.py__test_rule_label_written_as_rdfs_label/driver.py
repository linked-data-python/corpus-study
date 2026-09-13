"""Validation driver for llhhx0826__swrl2rdf__tests_test_builder.py__test_rule_label_written_as_rdfs_label.

The region's whole effect is an internal ``assert``: it returns None, and
the only argument worth observing is ``prefix_map`` itself. A single
``PrefixMap`` instance is shared between both calls (the tuple ``case`` is
not a callable factory, so both sides unpack the SAME object) rather than
built fresh per side, because ``PrefixMap`` has no ``__eq__``: two distinct
but equal-by-content instances would be reported as differing by identity.
Sharing is safe here since ``rules_to_graph`` only reads it.
"""
from rdfeval.harness import run_pair
from swrl2rdf_shim import PrefixMap

VERDICT = run_pair(
    __file__,
    entry='test_rule_label_written_as_rdfs_label',
    calls=[((PrefixMap(),), {})],
)
