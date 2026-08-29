# Extracted from RDFLib/timefuncs@dd3bde8727 : tests/functions/test_finishes.py
# region: test_finishes (lines 15-49, stratum bind_initbindings)
# licence of the source repository: see meta.json
# (added to make the region executable: the real file imports Path and
# `finishes` at the top -- `from pathlib import Path` and
# `from timefuncs import finishes`, the latter's side effect being to
# register `tfun:finishes`; see context_shim.py and meta.json)
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import TIME
from context_shim import finishes
TFUN = Namespace("https://w3id.org/timefuncs/")
FINISHES = Namespace("https://w3id.org/timefuncs/testdata/finishes/")
tests_dir = Path(__file__).parent

def test_finishes():
    g = Graph().parse(str(tests_dir / "data" / "finishes.ttl"))

    q = """
        SELECT ?a ?b
        WHERE {
            VALUES ?a_type { time:Interval time:ProperInterval }
            VALUES ?b_type { time:Interval time:ProperInterval }

            ?a a ?a_type .
            ?b a ?b_type .

            FILTER tfun:finishes(?a, ?b)
        }
        """        
    expected = [
        (str(FINISHES.a01), str(FINISHES.b01)),
        # (str(FINISHES.a02), str(FINISHES.b02)), false
        (str(FINISHES.a03), str(FINISHES.b03)),
        (str(FINISHES.a04), str(FINISHES.b04)),
        (str(FINISHES.a05), str(FINISHES.b05)),
        (str(FINISHES.a06), str(FINISHES.b06)),
        # (str(FINISHES.a07), str(FINISHES.b07)), still working on this
        (str(FINISHES.a08), str(FINISHES.b08)),
    ]

    actual = sorted([
        (str(r[0]), str(r[1]))
        for r in g.query(
            q,
            initNs={"time": TIME, "tfun": TFUN}
        )
    ])

    assert actual == expected


# Demo harness (identical on both sides, see meta.json): `test_finishes`
# asserts internally and returns nothing, printing nothing and mutating no
# argument -- entry=/calls= would have nothing to compare on its own (the
# "nothing observable" guard in rdfeval.harness). `demo` runs it -- an
# AssertionError on either side already fails the whole check, which is the
# region's own pass/fail criterion -- and returns a sentinel.
def demo():
    test_finishes()
    return "ok"
