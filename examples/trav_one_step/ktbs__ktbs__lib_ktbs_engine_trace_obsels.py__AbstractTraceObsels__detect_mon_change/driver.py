"""Validation driver for ktbs__ktbs__lib_ktbs_engine_trace_obsels.py__AbstractTraceObsels__detect_mon_change.

The region is a method: `self` carries `trace_uri`, `trace.pseudomon_range`
and `state` (a Graph that is a superset of the `graph` argument, per the
region's own docstring). `prepared` is mutated in place and compared after
the call, like `self` and `graph`.
"""
from rdflib import Graph, URIRef, Literal
from rdfeval.harness import run_pair

TRACE = "http://example.org/trace1/"


class _Trace:
    def __init__(self, pseudomon_range):
        self.pseudomon_range = pseudomon_range


class _Fake:
    """Minimal stand-in for AbstractTraceObsels: only the attributes the
    region reads (trace_uri, trace.pseudomon_range, state)."""

    def __init__(self, pseudomon_range, state_triples):
        self.trace_uri = URIRef(TRACE)
        self.trace = _Trace(pseudomon_range)
        self.state = Graph()
        for t in state_triples:
            self.state.add(t)

    def __eq__(self, other):
        return (isinstance(other, _Fake)
                and self.trace_uri == other.trace_uri
                and self.trace.pseudomon_range == other.trace.pseudomon_range
                and set(self.state) == set(other.state))


class _Prepared:
    def __init__(self, last_obsel=None, last_begin=None, last_end=None,
                 str_mon=True, pse_mon=True):
        self.last_obsel = last_obsel
        self.last_begin = last_begin
        self.last_end = last_end
        self.str_mon = str_mon
        self.pse_mon = pse_mon

    def __eq__(self, other):
        return (isinstance(other, _Prepared)
                and self.last_obsel == other.last_obsel
                and self.last_begin == other.last_begin
                and self.last_end == other.last_end
                and self.str_mon == other.str_mon
                and self.pse_mon == other.pse_mon)


HAS_TRACE = URIRef("http://liris.cnrs.fr/silex/2009/ktbs#hasTrace")
HAS_BEGIN = URIRef("http://liris.cnrs.fr/silex/2009/ktbs#hasBegin")
HAS_END = URIRef("http://liris.cnrs.fr/silex/2009/ktbs#hasEnd")
RELATES_TO = URIRef("http://liris.cnrs.fr/silex/2009/ktbs#relatesTo")


def _case_first_obsel():
    # prepared.last_obsel is None: the early-return branch.
    new_obs = URIRef(TRACE + "o1")
    triples = [
        (new_obs, HAS_TRACE, URIRef(TRACE)),
        (new_obs, HAS_BEGIN, Literal(5)),
        (new_obs, HAS_END, Literal(10)),
    ]
    graph = Graph()
    for t in triples:
        graph.add(t)
    self_ = _Fake(pseudomon_range=2, state_triples=triples)
    prepared = _Prepared()
    return (self_, graph, prepared), {}


def _case_monotonic_no_relation():
    # A later obsel, unrelated to any other: monotonicity holds.
    old_obs = URIRef(TRACE + "o1")
    new_obs = URIRef(TRACE + "o2")
    new_triples = [
        (new_obs, HAS_TRACE, URIRef(TRACE)),
        (new_obs, HAS_BEGIN, Literal(6)),
        (new_obs, HAS_END, Literal(10)),
    ]
    state_triples = new_triples + [
        (old_obs, HAS_BEGIN, Literal(1)),
        (old_obs, HAS_END, Literal(5)),
    ]
    graph = Graph()
    for t in new_triples:
        graph.add(t)
    self_ = _Fake(pseudomon_range=2, state_triples=state_triples)
    prepared = _Prepared(last_obsel=old_obs, last_begin=1, last_end=5)
    return (self_, graph, prepared), {}


def _case_regression_with_related_obsel():
    # A new obsel that regresses both begin/end, plus a related obsel
    # (reached through graph.objects()/graph.subjects() with a wildcard
    # predicate) that must be walked too but does not itself regress.
    old_obs = URIRef(TRACE + "o_old")
    new_obs = URIRef(TRACE + "o3")
    related = URIRef(TRACE + "o_related")
    new_triples = [
        (new_obs, HAS_TRACE, URIRef(TRACE)),
        (new_obs, HAS_BEGIN, Literal(8)),
        (new_obs, HAS_END, Literal(15)),
        (new_obs, RELATES_TO, related),
        (related, HAS_BEGIN, Literal(22)),
        (related, HAS_END, Literal(25)),
    ]
    state_triples = new_triples + [
        (old_obs, HAS_BEGIN, Literal(10)),
        (old_obs, HAS_END, Literal(20)),
    ]
    graph = Graph()
    for t in new_triples:
        graph.add(t)
    self_ = _Fake(pseudomon_range=3, state_triples=state_triples)
    prepared = _Prepared(last_obsel=old_obs, last_begin=10, last_end=20)
    return (self_, graph, prepared), {}


VERDICT = run_pair(
    __file__,
    entry='_detect_mon_change',
    calls=[_case_first_obsel, _case_monotonic_no_relation,
           _case_regression_with_related_obsel],
)
