# Extracted from RDFLib/timefuncs@dd3bde8727 : tests/functions/test_is_during.py
# region: test_is_during (lines 15-46, stratum sparql_literal)
# licence of the source repository: see meta.json
#
# Context restored (see meta.json): `from pathlib import Path` was above the
# extracted line range in the real file (it is used by `tests_dir =
# Path(__file__).parent`, which the context lines DID capture) -- restored
# here verbatim, it is not new logic. `from timefuncs import is_during`,
# which registers `tfun:isDuring` as a custom SPARQL function as an import
# side effect, is replaced by the equivalent import from `_context` (see
# that file for why `timefuncs` itself is not installable here).
from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import TIME
from _context import is_during
TFUN = Namespace("https://w3id.org/timefuncs/")
ID = Namespace("https://w3id.org/timefuncs/testdata/isduring/")
tests_dir = Path(__file__).parent

def test_is_during():
    g = Graph().parse(str(tests_dir / "data" / "is_during.ttl"))
    q = """SELECT ?a ?b WHERE {
        ?a a time:Interval .
        ?b a time:Interval .

        FILTER tfun:isDuring(?a, ?b)
    }"""
    expected = [(str(ID[f"a0{i}"]), str(ID[f"b0{i}"])) for i in range(1, 10)]

    actual = sorted((str(a), str(b)) for a, b in g.query(q, initNs={"time": TIME, "tfun": TFUN}))

    assert actual == expected
    # Appended (see meta.json): the original test asserts and returns
    # nothing, so the driver would have nothing beyond "did not raise" to
    # compare (rdfeval.harness: a call that returns None, mutates nothing
    # and prints nothing is "nothing observable to compare"). Identical on
    # both sides; changes nothing about the RDF behaviour under test.
    return actual


# Demo seam (identical on both sides, see meta.json): `run` lets driver.py
# observe the query's candidate rows (see there); by default it is the call.
def demo(run=lambda test: test()):
    return run(test_is_during)
