"""Validation driver for tableau__altimeter__altimeter_core_graph_links.py__SimpleLink_to_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

``to_rdf`` mutates the ``graph`` argument it is given (no return value), so
each call must hand it a fresh ``Graph`` and the harness compares that
argument afterwards.

The first four cases are the translator's: small int, int over the
threshold, str, negative int.

Added by the mutation audit of 2026-10-30. `SimpleLink.obj` is validated
against SCALAR_TYPES = (bool, int, float, str, datetime.datetime)
(altimeter/core/graph/__init__.py:3), so every one of those types is
exercised, plus the edges of the `> 2147483647` threshold:

  * bool (an int subclass, never over the threshold), int 0, the threshold
    itself (2147483647, no datatype) and one past it (2147483648, forced
    xsd:nonNegativeInteger);
  * float 1.5 and float 5e9 -- a float over the threshold keeps datatype
    None, which `isinstance(self.obj, (int, float))` would change;
  * str "" and a naive and an aware datetime (xsd:dateTime).

Every case after the first four builds the graph as the repository does
(ValidatedGraphSet.to_rdf, graph_set.py:92-111: a default `Graph()`, a
`Namespace(f"{name}:")`, a `NodeCache()`), and its subject BNode already
carries a triple, as a resource node does when its links are graphed: a
translation that wrote on a fresh blank node instead of `subj` is then not
isomorphic.

After run_pair, a second phase runs every case again and compares the
prefix bindings of `graph`: the repository serialises it
(altimeter/core/artifact_io/writer.py:133, `graph.serialize(fp,
format="xml")`), so `@graph graph` must not replace a binding the
original's graph has (it may add the block's own, record ldpy/027).
"""
import contextlib
import datetime
import io
from pathlib import Path

from rdflib import RDF, BNode, Graph, Namespace

from node_cache import NodeCache
from rdfeval.harness import _emit, _exec_ldpy, _exec_python, run_pair

HERE = Path(__file__).resolve().parent


class Link:
    def __init__(self, pred, obj):
        self.pred = pred
        self.obj = obj

    def __eq__(self, other):
        # the harness also compares call arguments (to catch a region that
        # mutates them differently); Link has no natural equality otherwise.
        return isinstance(other, Link) and vars(self) == vars(other)

    def __repr__(self):
        return f"Link({self.pred!r}, {self.obj!r})"


NS = Namespace("http://example.org/link#")


def case_small_int():
    # datatype stays None: plain integer coercion.
    return ((Link("hasCount", 3), BNode(), NS, Graph(), None), {})


def case_large_int():
    # obj.obj > 2147483647: datatype forced to xsd:nonNegativeInteger.
    return ((Link("hasBigCount", 5000000000), BNode(), NS, Graph(), None), {})


def case_string():
    # not an int at all: datatype stays None, plain string literal.
    return ((Link("hasName", "widget-1"), BNode(), NS, Graph(), None), {})


def case_negative_int():
    # int but not over the threshold, and negative: datatype stays None.
    return ((Link("hasDelta", -42), BNode(), NS, Graph(), None), {})


def repo_case(pred, obj):
    """A call shaped like ValidatedGraphSet.to_rdf's: default Graph(), the
    `<name>:` namespace, a NodeCache, a subject already in the graph."""
    def make():
        namespace = Namespace("alti:")
        graph = Graph()
        subj = BNode()
        graph.add((subj, RDF.type, getattr(namespace, "aws:ec2:instance")))
        return ((Link(pred, obj), subj, namespace, graph, NodeCache()), {})
    return make


CALLS = [
    case_small_int, case_large_int, case_string, case_negative_int,
    repo_case("is_default", True),
    repo_case("is_default", False),
    repo_case("instance_count", 0),
    repo_case("size", 2147483647),
    repo_case("size", 2147483648),
    repo_case("ratio", 1.5),
    repo_case("bytes", 5e9),
    repo_case("name", ""),
    repo_case("launch_time", datetime.datetime(2020, 1, 2, 3, 4, 5)),
    repo_case("launch_time",
              datetime.datetime(2020, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)),
]

# run_pair prints its own verdict line, and rdfeval check reads the FIRST
# one: silence it, so the line that counts is the one emitted below.
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry='to_rdf', calls=CALLS)

if not VERDICT.get("error"):
    extra = []
    fo = _exec_python(HERE / "original.py")[0]["to_rdf"]
    ft = _exec_ldpy(HERE / "translated.ldpy")[0]["to_rdf"]
    for i, make in enumerate(CALLS):
        args_o, _ = make()
        args_t, _ = make()
        for f, args in ((fo, args_o), (ft, args_t)):
            try:
                f(*args)
            except Exception:                     # noqa: BLE001 - compared above
                pass
        go, gt = args_o[3], args_t[3]
        lost = sorted({(p, str(u)) for p, u in go.namespaces()}
                      - {(p, str(u)) for p, u in gt.namespaces()})
        if lost:
            extra.append(f"call[{i}]: prefix bindings of the original lost "
                         f"in the translation: {lost}")
    VERDICT["method"] += " + graph bindings"
    VERDICT["diffs"] = VERDICT["diffs"] + extra
    VERDICT["equivalent"] = not VERDICT["diffs"]

_emit(VERDICT)
