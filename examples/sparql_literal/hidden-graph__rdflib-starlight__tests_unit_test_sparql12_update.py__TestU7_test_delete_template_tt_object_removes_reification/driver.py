"""Validation driver for TestU7.test_delete_template_tt_object_removes_reification
(rdflib-starlight).

The region is a test: it sends a SPARQL 1.2 `DELETE { ?r rdf:reifies <<( ?s ?p
?o )>> } WHERE { ... }` update to `g`, then asserts that `g.triples((stmt1,
rdf:reifies, None))` is empty.  rdflib 7.2.1 cannot parse the update, and the
package that runs it (rdflib-starlight) is not installable here, so the pair
runs against a STUB graph.  Its `update` prints the text it receives
(whitespace-normalised: stdout shows the exact update each side sent) and then
applies the effect the case selects, written by the driver (not derived from
the SPARQL):

  * "delete": removes every `?r rdf:reifies ?x` whose subject has
    :confidence "0.9" -- stmt1 loses its reification, stmt2 (0.5) keeps its
    own, ex:other (no reification) is untouched -> the assert passes (None);
  * "nothing": the update has no effect -> stmt1 still reifies, AssertionError;
  * "delete all": removes every reification, including stmt2's -> the assert
    passes but the graph the call leaves differs from "delete" (the stub is an
    argument and is compared afterwards).

What this does NOT prove: that the update means what the original means to a
SPARQL 1.2 engine.  The translation is the original text unchanged (`s{ }`
cannot hold it: see meta.json), so the text sent is what is compared.
"""
import re
from pathlib import Path

from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
REIFIES = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#reifies")
CONF = URIRef("http://example.org/confidence")


class _StubStarlightGraph(Graph):
    effect = "delete"

    def update(self, update_object, *args, **kwargs):
        print("update:", re.sub(r"\s+", " ", str(update_object)).strip())
        if self.effect == "nothing":
            return
        for r, _, x in list(self.triples((None, REIFIES, None))):
            if self.effect == "delete all" or (r, CONF, Literal("0.9")) in self:
                self.remove((r, REIFIES, x))


def call(effect):
    def _make():
        g = _StubStarlightGraph()
        g.parse(FIXTURE, format="turtle")
        g.effect = effect
        return (None, g), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='test_delete_template_tt_object_removes_reification',
    calls=[call("delete"), call("nothing"), call("delete all")],
)
