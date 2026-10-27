"""Validation driver for ktbs__ktbs__lib_ktbs_engine_trace_obsels.py__AbstractTraceObsels__detect_mon_change.

The region is a method: `self` carries `trace_uri`, `trace.pseudomon_range`
and `state` (a Graph that is a superset of the `graph` argument, per the
region's own docstring). `prepared` is mutated in place and compared after
the call, like `self` and `graph`.

The first three calls (first obsel, monotonic append, regression with an
outgoing relation) are the original driver and are kept as they were.  The
calls after them were added by the repair pass, one per branch the first three
never reached (see the comment above each):

  * `end == old_last_end`, whose `begin` is read from `self.state` and then
    compared three ways (`<`, `==`, `>`), with `obs <= old_last_obsel` both
    ways, and the pseudo-monotonic limit on `begin`;
  * `end < old_last_end` with `end` above and below the pseudo-monotonic limit;
  * the INCOMING relation (`graph.subjects(None, new_obs)`), which no earlier
    call had: nothing was bound to `new_obs` in object position;
  * neighbourhood that must be skipped: an obsel of another trace, an obsel
    without `hasEnd` in `self.state`, a literal object that merely starts with
    the trace URI, a relation to a non-obsel resource, a self-relation, and a
    `hasTrace` triple of ANOTHER trace in `graph` (it must not match);
  * the exceptions: the harness does not compare two raised exceptions (it
    stops on the first one), so `_exec_artefact` is wrapped below to return
    the exception's type and message as the call's result.  Both sides then
    have to raise the same thing, including when `pseudomon_range` is not a
    number (the original subtracts it before the loop, so it raises even when
    the loop would never compare) and when a `hasBegin` is missing.
"""
from rdflib import Graph, URIRef, Literal
import rdfeval.harness as _harness
from rdfeval.harness import run_pair

_ENTRY = "_detect_mon_change"
_exec_artefact = _harness._exec_artefact


def _exec_returning_exceptions(path, name):
    """Run the artefact, but make the entry point RETURN what it raises."""
    ns, out = _exec_artefact(path, name)
    region = ns[_ENTRY]

    def _wrapped(*args, **kwargs):
        try:
            return region(*args, **kwargs)
        except Exception as e:
            return ("raised", type(e).__name__, str(e))

    ns[_ENTRY] = _wrapped
    return ns, out


_harness._exec_artefact = _exec_returning_exceptions

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


OLD = URIRef(TRACE + "o_m")        # prepared.last_obsel in the cases below
OTHER_TRACE = "http://example.org/trace2/"
DESCRIPTION = URIRef("http://purl.org/dc/terms/description")


def _obsel(uri, begin=None, end=None):
    """The triples of one obsel in the shape the region reads."""
    triples = []
    if begin is not None:
        triples.append((uri, HAS_BEGIN, Literal(begin)))
    if end is not None:
        triples.append((uri, HAS_END, Literal(end)))
    return triples


def _case(new_obs, begin, end, *, extra_graph=(), extra_state=(),
          pseudomon_range=3, last=(10, 20)):
    """A call whose `graph` describes `new_obs` (+ `extra_graph`), `state`
    being a superset of it (+ `extra_state`), after an obsel OLD that ended
    at `last`."""
    def build():
        new_triples = ([(new_obs, HAS_TRACE, URIRef(TRACE))]
                       + _obsel(new_obs, begin, end) + list(extra_graph))
        graph = Graph()
        for t in new_triples:
            graph.add(t)
        state_triples = (new_triples + _obsel(OLD, *last) + list(extra_state))
        self_ = _Fake(pseudomon_range=pseudomon_range,
                      state_triples=state_triples)
        prepared = _Prepared(last_obsel=OLD, last_begin=last[0],
                             last_end=last[1])
        return (self_, graph, prepared), {}
    return build


Z = URIRef(TRACE + "o_z")   # sorts after OLD
A = URIRef(TRACE + "o_a")   # sorts before OLD
REL = URIRef(TRACE + "o_rel")

# --- end == old_last_end: begin is read from self.state --------------------
# begin == last_begin and obs > OLD: stays strictly monotonic, prepared moves
_case_end_eq_begin_eq_after = _case(Z, 10, 20)
# begin == last_begin and obs <= OLD: str_mon False
_case_end_eq_begin_eq_before = _case(A, 10, 20)
# begin < last_begin but >= begin limit (10-3): str_mon False, pse_mon True
_case_end_eq_begin_lt_pse = _case(Z, 9, 20)
# begin < begin limit: pse_mon False as well
_case_end_eq_begin_lt_far = _case(Z, 5, 20)
# begin > last_begin: monotonic, prepared.last_begin comes from the state read
_case_end_eq_begin_gt = _case(Z, 12, 20)
# --- end < old_last_end ------------------------------------------------------
# end < last_end but >= end limit (20-3): str_mon False, pse_mon True
_case_end_lt_pse = _case(Z, 11, 18)
# end < end limit: pse_mon False
_case_end_lt_far = _case(Z, 11, 15)
# end > last_end: begin is read from graph for prepared.last_begin
_case_end_gt = _case(Z, 11, 25)
# pseudomon_range 0: the limits are the last values themselves
_case_range_zero = _case(Z, 9, 20, pseudomon_range=0)

# --- INCOMING relation: (other, relatesTo, new_obs) in graph -----------------
# new_obs advances (end 25) and is stored first; the related obsel REL, reached
# only through graph.subjects(None, new_obs), regresses (end 15, below the
# limit): str_mon and pse_mon both go False AFTER prepared moved.
_case_incoming_regresses = _case(
    Z, 11, 25,
    extra_graph=[(REL, RELATES_TO, Z)] + _obsel(REL, 12, 15))
# the incoming obsel only reaches `end == last_end`, so its begin is read from
# self.state (and compared to last_begin)
_case_incoming_end_eq = _case(
    Z, 11, 25,
    extra_graph=[(REL, RELATES_TO, Z)] + _obsel(REL, 4, 20))
# incoming relation AND outgoing relation together, both regressing
_case_in_and_out = _case(
    Z, 11, 25,
    extra_graph=([(REL, RELATES_TO, Z), (Z, RELATES_TO, URIRef(TRACE + "o_out"))]
                 + _obsel(REL, 12, 15) + _obsel(URIRef(TRACE + "o_out"), 3, 2)))
# self-relation: new_obs is also yielded by objects() and subjects()
_case_self_relation = _case(Z, 11, 25, extra_graph=[(Z, RELATES_TO, Z)])

# the related obsel is an OLDER one: its hasEnd/hasBegin are only in
# self.state (the graph carries just the relation), as in a real trace.
# Outgoing and incoming, regressing below the limit / reaching end == last_end.
OUT = URIRef(TRACE + "o_out")
_case_outgoing_regresses = _case(
    Z, 11, 25, extra_graph=[(Z, RELATES_TO, OUT)] + _obsel(OUT, 3, 2))
_case_outgoing_state_only_regresses = _case(
    Z, 11, 25, extra_graph=[(Z, RELATES_TO, OUT)],
    extra_state=_obsel(OUT, 3, 2))
_case_outgoing_state_only_end_eq = _case(
    Z, 11, 25, extra_graph=[(Z, RELATES_TO, OUT)],
    extra_state=_obsel(OUT, 4, 20))
_case_incoming_state_only_regresses = _case(
    Z, 11, 25, extra_graph=[(REL, RELATES_TO, Z)],
    extra_state=_obsel(REL, 12, 15))
_case_incoming_state_only_end_eq = _case(
    Z, 11, 25, extra_graph=[(REL, RELATES_TO, Z)],
    extra_state=_obsel(REL, 4, 20))
# new_obs IS the previous last obsel (same URI, same begin/end): `obs <=` holds
# by equality only
_case_same_obsel = _case(OLD, 10, 20)

# --- neighbourhood that must be skipped --------------------------------------
# incoming relation from an obsel of ANOTHER trace, even though it has an end
# that would regress: `startswith(trace_uri)` skips it
_case_incoming_other_trace = _case(
    Z, 11, 25,
    extra_graph=[(URIRef(OTHER_TRACE + "o_x"), RELATES_TO, Z)],
    extra_state=_obsel(URIRef(OTHER_TRACE + "o_x"), 1, 1))
# incoming relation from an obsel of this trace with no hasEnd in the state
_case_incoming_no_end = _case(
    Z, 11, 25, extra_graph=[(REL, RELATES_TO, Z)])
# outgoing relation to a non-obsel resource, and a literal object that starts
# with the trace URI (a Literal has startswith() too, and no hasEnd)
_case_non_obsel_neighbours = _case(
    Z, 11, 25,
    extra_graph=[(Z, RELATES_TO, URIRef("http://example.org/elsewhere")),
                 (Z, DESCRIPTION, Literal(TRACE + "o_lit"))],
    extra_state=_obsel(URIRef("http://example.org/elsewhere"), 1, 1))
# the graph also types an obsel of ANOTHER trace: the hasTrace lookup is keyed
# on this trace's URI, so only new_obs may be found
_case_foreign_has_trace = _case(
    Z, 11, 25,
    extra_graph=[(URIRef(OTHER_TRACE + "o_y"), HAS_TRACE, URIRef(OTHER_TRACE))]
                + _obsel(URIRef(OTHER_TRACE + "o_y"), 99, 99))

# --- exceptions (compared through _exec_returning_exceptions) ---------------
# pseudomon_range is not a number: the original raises TypeError from the two
# limits BEFORE the loop, whatever the obsels are (here nothing regresses)
_case_range_none = _case(Z, 11, 25, pseudomon_range=None)
# end == last_end but the state has no hasBegin for it: int(None)
_case_missing_begin = _case(
    Z, None, 20, extra_state=[])
# the new obsel has no hasEnd: skipped, prepared untouched
_case_new_without_end = _case(Z, 11, None)


VERDICT = run_pair(
    __file__,
    entry=_ENTRY,
    calls=[_case_first_obsel, _case_monotonic_no_relation,
           _case_regression_with_related_obsel,
           _case_end_eq_begin_eq_after, _case_end_eq_begin_eq_before,
           _case_end_eq_begin_lt_pse, _case_end_eq_begin_lt_far,
           _case_end_eq_begin_gt,
           _case_end_lt_pse, _case_end_lt_far, _case_end_gt, _case_range_zero,
           _case_incoming_regresses, _case_incoming_end_eq, _case_in_and_out,
           _case_self_relation, _case_outgoing_regresses,
           _case_outgoing_state_only_regresses,
           _case_outgoing_state_only_end_eq,
           _case_incoming_state_only_regresses,
           _case_incoming_state_only_end_eq, _case_same_obsel,
           _case_incoming_other_trace, _case_incoming_no_end,
           _case_non_obsel_neighbours, _case_foreign_has_trace,
           _case_range_none, _case_missing_begin, _case_new_without_end],
)
