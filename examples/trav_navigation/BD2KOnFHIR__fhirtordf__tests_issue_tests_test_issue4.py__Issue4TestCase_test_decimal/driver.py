"""Validation driver for BD2KOnFHIR__fhirtordf__tests_issue_tests_test_issue4.py__Issue4TestCase_test_decimal.

The region is a test method decorated `@unittest.expectedFailure`: called
directly it runs its body, and the whole effect is assertions about the graph
the loader built from a FHIR JSON. The call returns None when they hold and
raises AssertionError when one fails -- and the message of a failed
`assertEqual` carries both values, so the raises are told apart.

The loader (fhirtordf) is replaced by the stand-in of fhirtordf_shim.py,
which hands the region a graph frozen in a Turtle file; each case rebinds
`fhirtordf_shim.LOADER_OUTPUT` before the call (same for both
representations). `self` is a plain `unittest.TestCase()`.

What each case exercises, on the three chained reads
`g.value(g.value(g.value(<resource>, dispense), dispense.add), fhir:value)`:

  loader        the loader's output (fixture.ttl): "2.0"^^xsd:decimal at the
                end of the chain, so the last assertEqual fails (the issue the
                test pins, an expected failure).
  exact         "2.00"^^xsd:decimal at the end: the assertion holds.
  two_dispenses two dispense entries; the first one has no dispense.add and
                g.value follows the first -> None. The second one holds the
                "2.00" that a single join over the chain would find.
  no_value      the add node has no fhir:value (last link missing) while other
                "2.00" decimals sit under neighbouring predicates.
  no_add        no dispense.add on the entry (middle link missing): the chain
                is None before its last read.
  no_dispense   the resource has no dispense at all (first link missing);
                another resource, 33124, is complete.
"""
import unittest

from rdfeval.harness import run_pair
import fhirtordf_shim


def _case(loader_output):
    def make():
        fhirtordf_shim.LOADER_OUTPUT = loader_output
        return (unittest.TestCase(),), {}
    return make


CALLS = [
    _case("fixture.ttl"),                  # loader
    _case("fixture_exact.ttl"),            # exact
    _case("fixture_two_dispenses.ttl"),    # two_dispenses
    _case("fixture_no_value.ttl"),         # no_value
    _case("fixture_no_add.ttl"),           # no_add
    _case("fixture_other_resource.ttl"),   # no_dispense
]

VERDICT = run_pair(
    __file__,
    entry='test_decimal',
    calls=CALLS,
)
