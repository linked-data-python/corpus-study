# Extracted from RDFLib/timefuncs@dd3bde8727 : tests/functions/test_is_inside.py
# region: test_is_inside (lines 15-43, stratum bind_initbindings)
# licence of the source repository: see meta.json
# (added to make the region executable: the real file imports Path and
# `is_inside` at the top -- `from pathlib import Path` and (via
# `sys.path.append`) `from timefuncs import is_inside`, the latter's side
# effect being to register `tfun:isInside`; see context_shim.py and
# meta.json)
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import TIME
from context_shim import is_inside
TFUN = Namespace("https://w3id.org/timefuncs/")
INSIDE = Namespace("https://w3id.org/timefuncs/testdata/inside/")
tests_dir = Path(__file__).parent

def test_is_inside():
    g = Graph().parse(str(tests_dir / "data" / "is_inside.ttl"))
    q = """
        SELECT ?a ?b
        WHERE {
            ?a a time:Instant .
            ?b a time:Interval .

            FILTER tfun:isInside(?a, ?b)
        }
        """
    expected = [
        (str(INSIDE.a02), str(INSIDE.b02)),
        (str(INSIDE.a07), str(INSIDE.b07)),
        (str(INSIDE.a08), str(INSIDE.b07)),
        (str(INSIDE.a09), str(INSIDE.b09)),
    ]
    # print()
    # for r in g.query(q, initNs={"time": TIME, "tfun": TFUN}):
    #     print(r)
    actual = sorted([
        (str(r[0]), str(r[1]))
        for r in g.query(
            q,
            initNs={"time": TIME, "tfun": TFUN}
        )
    ])

    assert actual == expected


# Demo harness (identical on both sides, see meta.json): `test_is_inside`
# asserts internally and returns nothing, printing nothing and mutating no
# argument -- entry=/calls= would have nothing to compare on its own (the
# "nothing observable" guard in rdfeval.harness). `demo` runs it -- an
# AssertionError on either side already fails the whole check, which is the
# region's own pass/fail criterion -- and returns a sentinel.
def demo():
    test_is_inside()
    return "ok"
