"""Validation driver for TestIllTypedLiterals.test_ill_typed_literal_parsed_from_trig.

The region is a pytest method; its ``self`` is unused, so the single
fixture passes ``None``.  The assertion is inside the region itself: it
requires ``MalformedNanopubError`` to be raised with "not-a-number" in the
message, which only happens if the ill-typed literal really carries
``xsd:integer``.  A wrong datatype (or a well-typed value) makes
``pytest.raises`` fail, the harness catches it and the verdict is not
equivalent -- checked by a negative control.
"""
from rdfeval.harness import run_pair


def case_pytest_self():
    return ((None,), {})


VERDICT = run_pair(__file__, entry="test_ill_typed_literal_parsed_from_trig",
                   calls=[case_pytest_self])
