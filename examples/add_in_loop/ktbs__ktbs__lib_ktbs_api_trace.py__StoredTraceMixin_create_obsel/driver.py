"""Validation driver for ktbs__ktbs__lib_ktbs_api_trace.py__StoredTraceMixin_create_obsel.

Establishes semantic equivalence of original.py and translated.ldpy via the
demo(**kwargs) harness both files carry (see meta.json): create_obsel builds
its graph and hands it to self.post_graph(...), a side effect rather than a
return value, so demo() supplies a context_shim._TraceStub as `self` and
hands back the graph it captured.

Three calls, chosen to walk every branch that touches the graph (the ones
that raise -- "type is mandatory", unparsable begin/end -- are not
RDF-producing branches and are left untested here):

CALL_1 -- begin/end as plain ints (hasBegin/hasEnd, not the DT variants),
an explicit URIRef subject, and all four "in a loop" collections non-empty
and multi-item: attributes (one Node-valued, one plain-valued -- exercises
both sides of `val if isinstance(val, Node) else Literal(val)`), relations,
inverse_relations, source_obsels. This is the main add-in-loop exhibit.

CALL_2 -- begin as an ISO date string (the parse_date branch), end as a
naive datetime (the "tzinfo is None -> replace(tzinfo=UTC)" branch),
subject=None (self.get_default_subject()), id=None (BNode obs -- graph
isomorphism, not identity, so a fresh blank node each run is fine), and all
four loop collections absent (None) -- the loops must contribute nothing.

CALL_3 -- subject given as a plain string, not a URIRef (the
Literal(subject) branch), begin as a tz-aware datetime (Integral branch not
taken, tzinfo already set so no replace()), end as an int, a label, and all
four loop collections present but EMPTY -- zero iterations, not "loop
absent": a bindings-generator with nothing to yield must still add nothing
extra, not raise.

Added by the repair of 2026-10-30:

RECORDER -- context_shim._TraceStub (harness support, not project code)
ignored every post_graph argument but the graph, so `ktbs:Obsel` (passed
outside any island) could be wrong without a difference. The driver
replaces it, identically for both sides (one shared module), by a subclass
that PRINTS what post_graph, force_state_refresh and factory receive; the
harness compares each call's stdout. A blank-node obsel prints as `_:b`.

CALL_4 -- the shape of the real callers (utest/test_ktbs_api_trace.py:116,
utest/test_ktbs_engine_trace_stats.py:26): a relative id resolved against
the trace URI, a type and attribute keys that are resources carrying a
`.uri`, begin=0 (falsy Integral) and end=None (end = begin), attribute
values that are falsy or meaningless (0, "", False, None, NaN, a list,
a bool True), and label="" (falsy, not None: must still be written).

CALL_5 -- explicit URIRef subject (the branch CALL_1's docstring claimed
but which passed a str), a BNode id kept as is, begin/end as ISO strings
with an offset, relations / inverse_relations / source_obsels given as
resources with `.uri`, a duplicated relation, and label=0.

CALL_6 -- subject "" (Literal(""), falsy, still written), begin=True
(bool is Integral).

CALL_7 / CALL_8 -- the raising branches (type None; begin a float), whose
type and message must agree.

FACTORY BRANCH -- demo() always passes no_return=True, so
`self.factory(uris[0], [ktbs:Obsel])` was never reached. After run_pair,
the driver executes both sides again and calls create_obsel(stub,
no_return=False, **CALL_1/CALL_4 kwargs) directly with the recorder, whose
factory returns an ObselMixin instance (the region asserts it); what the
stub printed and the graph it captured are compared, and any difference
turns the verdict red. run_pair's own verdict line is silenced and
re-emitted once (rdfeval.check reads the first one).
"""
import contextlib
import io
import json
import math
import sys
from pathlib import Path

from rdfeval.harness import _exec_ldpy, _exec_python, graphs_isomorphic, run_pair
from datetime import datetime, timezone
from rdflib import BNode, URIRef

import context_shim

_ORIGINAL_STUB = context_shim._TraceStub


class _RecordingTraceStub(_ORIGINAL_STUB):
    """_TraceStub that prints every argument the region hands to `self`."""

    @staticmethod
    def _show(node):
        return "_:b" if isinstance(node, BNode) else repr(node)

    def post_graph(self, graph, parameters, trust, obs_uri, obsel_type):
        print("post_graph", repr(parameters), repr(trust),
              self._show(obs_uri), repr(obsel_type))
        return super().post_graph(graph, parameters, trust, obs_uri, obsel_type)

    def force_state_refresh(self):
        print("force_state_refresh")

    def factory(self, uri, types):
        print("factory", self._show(uri), repr(types))
        obsel = context_shim.ObselMixin()
        obsel.uri = uri
        return obsel


context_shim._TraceStub = _RecordingTraceStub


class _Res:
    """A kTBS resource as the real callers pass it: coerce_to_uri reads .uri."""

    def __init__(self, uri):
        self.uri = URIRef(uri)

    def __eq__(self, other):
        return isinstance(other, _Res) and other.uri == self.uri

    def __hash__(self):
        return hash(self.uri)

    def __repr__(self):
        return f"_Res({self.uri!r})"

CALL_1 = {}, {
    "id": "http://example.org/obs/o1",
    "type": "http://example.org/model#Event",
    "begin": 1000,
    "end": 2000,
    "subject": "http://example.org/subjects/s1",
    "attributes": {
        "http://example.org/attr#weight": 42,
        "http://example.org/attr#ref": URIRef("http://example.org/other"),
    },
    "relations": [
        ("http://example.org/rel#next", "http://example.org/obs/o2"),
    ],
    "inverse_relations": [
        ("http://example.org/obs/o0", "http://example.org/rel#prev"),
    ],
    "source_obsels": [
        "http://example.org/obs/src1",
        "http://example.org/obs/src2",
    ],
    "label": "First obsel",
}

CALL_2 = {}, {
    "id": None,
    "type": "http://example.org/model#Sample",
    "begin": "2020-01-01T10:00:00Z",
    "end": datetime(2020, 1, 1, 10, 5, 0),
    "subject": None,
    "attributes": None,
    "relations": None,
    "inverse_relations": None,
    "source_obsels": None,
    "label": None,
}

CALL_3 = {}, {
    "id": "http://example.org/obs/o3",
    "type": "http://example.org/model#Event",
    "begin": datetime(2020, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
    "end": 3000,
    "subject": "plain-string-subject",
    "attributes": {},
    "relations": [],
    "inverse_relations": [],
    "source_obsels": [],
    "label": "Third obsel",
}

CALL_4 = {}, {
    "id": "o0",
    "type": _Res("http://example.org/base/m#OT2"),
    "begin": 0,
    "end": None,
    "attributes": {
        _Res("http://example.org/base/m#OT1-at1"): 0,
        _Res("http://example.org/base/m#OT1-at2"): "",
        _Res("http://example.org/base/m#OT1-at3"): False,
        _Res("http://example.org/base/m#OT1-at4"): None,
        _Res("http://example.org/base/m#OT1-at5"): math.nan,
        _Res("http://example.org/base/m#OT1-at6"): [1, 2],
        _Res("http://example.org/base/m#OT1-at7"): True,
    },
    "label": "",
}

CALL_5 = {}, {
    "id": BNode("given"),
    "type": "#OT1",
    "begin": "2020-01-01T10:00:00+02:00",
    "end": "2020-01-01T11:30:00+02:00",
    "subject": URIRef("http://example.org/people/alice"),
    "relations": [
        (_Res("http://example.org/base/m#rel"), _Res("http://example.org/base/t1/o2")),
        (_Res("http://example.org/base/m#rel"), _Res("http://example.org/base/t1/o2")),
        ("http://example.org/base/m#rel", "http://example.org/base/t1/o3"),
    ],
    "inverse_relations": [
        (_Res("http://example.org/base/t1/o9"), _Res("http://example.org/base/m#rel")),
    ],
    "source_obsels": [_Res("http://example.org/base/src/s1")],
    "label": 0,
}

CALL_6 = {}, {
    "id": "o6",
    "type": "#OT1",
    "begin": True,
    "end": 5,
    "subject": "",
}

CALL_7 = {}, {"id": "o7", "type": None, "begin": 1}

CALL_8 = {}, {"id": "o8", "type": "#OT1", "begin": 1.5}

_buf = io.StringIO()
with contextlib.redirect_stderr(_buf):
    VERDICT = run_pair(
        __file__,
        entry='demo',
        calls=[CALL_1, CALL_2, CALL_3, CALL_4, CALL_5, CALL_6, CALL_7, CALL_8],
    )


def _factory_branch(ns, kwargs):
    """create_obsel(..., no_return=False): what the recorder printed, the
    graph it captured, and the type of what came back."""
    stub = _RecordingTraceStub()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            ret = ns["create_obsel"](stub, no_return=False, **kwargs)
            outcome = (type(ret).__name__, repr(getattr(ret, "uri", None)))
        except Exception as e:  # noqa: BLE001 - compared
            outcome = ("raised", type(e).__name__, str(e))
    return out.getvalue(), outcome, stub.captured_graph


if VERDICT.get("error") is None:
    here = Path(__file__).resolve().parent
    ns_o, _ = _exec_python(here / "original.py")
    ns_t, _ = _exec_ldpy(here / "translated.ldpy")
    extra = []
    for name, (_, kwargs) in (("CALL_1", CALL_1), ("CALL_4", CALL_4)):
        po, oo, go = _factory_branch(ns_o, kwargs)
        pt, ot, gt = _factory_branch(ns_t, kwargs)
        if (po, oo) != (pt, ot):
            extra.append(f"factory branch {name}: {(po, oo)!r} vs {(pt, ot)!r}")
        if go is None or gt is None or not graphs_isomorphic(go, gt):
            extra.append(f"factory branch {name}: posted graphs differ")
    if extra:
        VERDICT["equivalent"] = False
        VERDICT["diffs"] = VERDICT.get("diffs", []) + extra

print("RDFEVAL-VERDICT " + json.dumps(VERDICT), file=sys.stderr)
