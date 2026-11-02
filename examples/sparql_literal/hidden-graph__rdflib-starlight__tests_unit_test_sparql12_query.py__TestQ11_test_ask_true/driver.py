"""Validation driver for TestQ11.test_ask_true (rdflib-starlight).

The region is a test: an ASK query (`ASK { << :bob :knows :carol >> :verifiedBy
:ResearchTeam . }`, in a triple-quoted string) sent to `g.query`, followed by `assert r.askAnswer is True`.  The query is
SPARQL 1.2 (reification shorthand), which rdflib 7.2.1 cannot parse, and the
package that evaluates it (rdflib-starlight, `StarlightGraph`) is not
installable here.  The pair is therefore run against a STUB graph whose
`query` prints the text it receives (whitespace-normalised, so stdout shows
the exact query each side sent) and answers with `askAnswer` set by the case:

  * True: the assert passes (None);
  * False: AssertionError;
  * 1 and "true" (truthy but not `True`): AssertionError -- the `is True`
    in the assert is what is exercised;
  * the graph the stub wraps (a few triples from fixture.ttl) is an argument
    too and is compared after the call: nothing may be written to it.

What this does NOT prove: that the query means what the original means to a
SPARQL 1.2 engine.  The translation is the original text unchanged (`s{ }`
cannot hold it: see meta.json), so the text sent is what is compared.
"""
import re
from pathlib import Path
from types import SimpleNamespace

from rdflib import Graph

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


class _StubStarlightGraph(Graph):
    answer = True

    def query(self, q, *args, **kwargs):
        print("query:", re.sub(r"\s+", " ", str(q)).strip())
        return SimpleNamespace(askAnswer=self.answer)


def call(answer):
    def _make():
        g = _StubStarlightGraph()
        g.parse(FIXTURE, format="turtle")
        g.answer = answer
        return (None, g), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='test_ask_true',
    calls=[call(True), call(False), call(1), call("true")],
)
