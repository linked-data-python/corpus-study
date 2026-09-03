# Extracted from RDFLib/timefuncs@dd3bde8727 : tests/functions/test_starts.py
# region: test_starts (lines 15-49, stratum bind_initbindings)
# licence of the source repository: see meta.json
# (added to make the region executable: the real file imports Path and
# `starts` at the top -- `from pathlib import Path` and
# `from timefuncs import starts`, the latter's side effect being to
# register `tfun:starts`; see context_shim.py and meta.json)
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import TIME
from context_shim import starts
TFUN = Namespace("https://w3id.org/timefuncs/")
STARTS = Namespace("https://w3id.org/timefuncs/testdata/starts/")
tests_dir = Path(__file__).parent

def test_starts():
    g = Graph().parse(str(tests_dir / "data" / "starts.ttl"))

    q = """
        SELECT ?a ?b
        WHERE {
            VALUES ?a_type { time:Interval time:ProperInterval }
            VALUES ?b_type { time:Interval time:ProperInterval }

            ?a a ?a_type .
            ?b a ?b_type .

            FILTER tfun:starts(?a, ?b)
        }
        """
    expected = [
        (str(STARTS.a01), str(STARTS.b01)),
        # (str(STARTS.a02), str(STARTS.b02)), false
        (str(STARTS.a03), str(STARTS.b03)),
        (str(STARTS.a04), str(STARTS.b04)),
        (str(STARTS.a05), str(STARTS.b05)),
        (str(STARTS.a06), str(STARTS.b06)),
        # (str(STARTS.a07), str(STARTS.b07)), still working on this
        (str(STARTS.a08), str(STARTS.b08)),
    ]

    actual = sorted([
        (str(r[0]), str(r[1]))
        for r in g.query(
            q,
            initNs={"time": TIME, "tfun": TFUN}
        )
    ])

    assert actual == expected


# Demo harness (identical on both sides, see meta.json): `test_starts`
# asserts internally and returns nothing, printing nothing and mutating no
# argument -- entry=/calls= would have nothing to compare on its own (the
# "nothing observable" guard in rdfeval.harness). `demo` runs it -- an
# AssertionError on either side already fails the whole check, which is the
# region's own pass/fail criterion -- and returns a sentinel.
def demo():
    test_starts()
    return "ok"
