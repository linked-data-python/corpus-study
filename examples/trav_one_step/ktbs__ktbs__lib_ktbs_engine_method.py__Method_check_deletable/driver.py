"""Driver for Method.check_deletable (kTBS).

`self` is the shim's Method (uri + state graph); the base implementation of
check_deletable (LocalCore's, which always accepts) comes from the shim too
and is called through super(Method, self).  The result is the Diagnosis; its
list of messages is compared as a multiset (no store promises an order).
Method m1 is used both ways, m2 by a trace only, m3 as a parent only, m4 by
nothing (its own outgoing links must not count), and an unknown method.
"""
from pathlib import Path

from rdflib import Namespace

from ktbs_context import Method
from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
B = Namespace("http://localhost:8001/b1/")


def call(uri, parameters=None):
    def make():
        return (Method(uri, fixture_graph(FIXTURE)), parameters), {}
    return make


CALLS = [call(B.m1), call(B.m2, {}), call(B.m3), call(B.m4), call(B.unknown)]

VERDICT = run_pair(__file__, entry="check_deletable", fixture="fixture.ttl", calls=CALLS)
