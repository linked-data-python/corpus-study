"""Validation driver for alganet__apysource__tests_test_emit.py__test_provenance_records_every_fragment_it_examined.

The region is a test: it takes no argument and its whole effect is two
assertions about the provenance graph `_run_with_provenance()` returns, so a
green call proves nothing by itself (it returns None on both sides). What the
original SHOWS is whether it raises. The driver therefore runs it against
provenance graphs that differ, by changing the page the real apysource checks
two fixed fragments against (`provenance_shim.BODY`, set by each case before
the call; the rebinding is the same for both representations):

  charter        the page holds the first fragment's sentence and not the
                 second's: one "verified", one "failed" -> both assertions
                 hold, the test passes.
  both_verified  the page holds both sentences: two verdicts, but both
                 "verified" -> the second assertion fails (a read that took
                 the status of the wrong node, or dropped one, would pass).
  none_verified  an empty page: two verdicts, both "failed" -> second
                 assertion fails.
  swapped        only the SECOND sentence is on the page: the verdicts are
                 "failed" for the first fragment and "verified" for the second,
                 the test passes -- the dict keyed by the fragment each verdict
                 was derived from has the same two entries either way.
  short          a page too short to be evidence: both "failed", fails.

The asserts carry no message, so a failing call raises a bare AssertionError;
which of the two fired is not told apart, only whether the call passes.
"""
from rdfeval.harness import run_pair
import provenance_shim

CHARTER = provenance_shim.BODY
SECOND = "this sentence appears nowhere in the charter at all"


def _case(body):
    def make():
        provenance_shim.BODY = body
        return (), {}
    return make


CALLS = [
    _case(CHARTER),                                                  # charter
    _case(CHARTER.replace("</body>", f"<p>{SECOND}, as it happens.</p></body>")),  # both_verified
    _case(""),                                                       # none_verified
    _case(f"<html><body><p>{SECOND} and there it is in the text</p></body></html>"),  # swapped
    _case("<p>war</p>"),                                             # short
]

VERDICT = run_pair(
    __file__,
    entry='test_provenance_records_every_fragment_it_examined',
    calls=CALLS,
)
