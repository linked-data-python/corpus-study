# Extracted from RDFLib/timefuncs@dd3bde8727 : tests/functions/test_is_after.py
# region: test_is_after (lines 15-59, stratum sparql_literal)
# licence of the source repository: see meta.json
#
# Context restored (see meta.json): `from pathlib import Path` was above the
# extracted line range in the real file (it is used by `tests_dir =
# Path(__file__).parent`, which the context lines DID capture) -- restored
# here verbatim, it is not new logic. `from timefuncs import is_after`,
# which registers `tfun:isAfter` as a custom SPARQL function as an import
# side effect, is replaced by the equivalent import from `_context` (see
# that file for why `timefuncs` itself is not installable here).
from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import TIME
from _context import is_after
TFUN = Namespace("https://w3id.org/timefuncs/")
AFTER = Namespace("https://w3id.org/timefuncs/testdata/after/")
tests_dir = Path(__file__).parent

def test_is_after():
    g = Graph().parse(str(tests_dir / "data" / "after.ttl"))
    expected = [(str(AFTER[f"a{a:02}"]), str(AFTER[f"b{b:02}"]))
                for a in range(1, 11) for b in range(1, 11) if a == b or min(a, b) >= 7]

    actual = sorted((str(a), str(b)) for a, b in g.query("""
        SELECT ?a ?b
        WHERE {
            ?a a time:TemporalEntity .
            ?b a time:TemporalEntity .

            FILTER tfun:isAfter(?a, ?b)
        }
        """, initNs={"time": TIME, "tfun": TFUN}))

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
    return run(test_is_after)
