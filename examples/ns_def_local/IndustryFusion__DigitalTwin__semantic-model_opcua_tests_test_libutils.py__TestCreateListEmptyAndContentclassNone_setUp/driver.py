"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_tests_test_libutils.py__TestCreateListEmptyAndContentclassNone_setUp.

setUp(self) assigns one rdflib Namespace to `self.basens`; the TestCase's
other methods then USE it (semantic-model/opcua/tests/test_libutils.py; the
uses probed below are those of the sibling region TestUtilityFunctions.setUp
of the same file, whose methods read `self.basens` the same way).
Comparing `self.basens` with `==` is not enough: a Namespace is a `str`
subclass, so a bare string, or a URIRef, with the same text is `==` to it.
What the other methods do with `self.basens` is therefore what the stand-in
`self` compares (see `_Probe`), one line per use found in the clone:

  * `self.basens['hasDatatype']`, `self.basens['numericID']` ...  (item access
    mints a URIRef: a bare str raises TypeError, a URIRef gives a different
    IRI), compared as value AND as type;
  * `self.basens.term('x')` (Namespace API);
  * `str(self.basens)` (`"@id": str(self.basens)` in the JSON-LD test);
  * `graph.bind("base", self.basens)` then serialisation: the namespace
    table of the graph and a triple minted through the namespace;
  * the type of `self.basens` itself (Namespace, not str/URIRef);
  * the attributes setUp leaves on `self` (only `basens`).

An exception raised by one of these uses is part of the probe, so a stand-in
that cannot do one of them differs from the original instead of aborting.
"""
from rdflib import Graph, Literal
from rdfeval.harness import run_pair


def _probe(ns):
    """Everything the other test methods do with `self.basens`."""
    out = {}
    uses = {
        "type": lambda: type(ns).__module__ + "." + type(ns).__qualname__,
        "str": lambda: str(ns),
        "item": lambda: (str(ns["hasDatatype"]), type(ns["hasDatatype"]).__name__),
        "item2": lambda: (str(ns["numericID"]), type(ns["numericID"]).__name__),
        "term": lambda: (str(ns.term("x")), type(ns.term("x")).__name__),
        "bind": lambda: _bound(ns),
    }
    for name, use in uses.items():
        try:
            out[name] = use()
        except Exception as e:  # a use the stand-in cannot support
            out[name] = ("raised", type(e).__name__)
    return out


def _bound(ns):
    graph = Graph()
    graph.bind("base", ns)
    graph.add((ns["node"], ns["hasEnumValue"], Literal("test")))
    return (sorted((p, str(u)) for p, u in graph.namespaces() if p == "base"),
            sorted(graph.serialize(format="nt").splitlines()))


class _Self:
    """Stands in for the TestCase instance `setUp(self)` mutates."""

    def __eq__(self, other):
        return (isinstance(other, _Self)
                and sorted(vars(self)) == sorted(vars(other))
                and _probe(self.basens) == _probe(other.basens))

    __hash__ = None


VERDICT = run_pair(
    __file__,
    entry='setUp',
    calls=[lambda: ((_Self(),), {})],
)
