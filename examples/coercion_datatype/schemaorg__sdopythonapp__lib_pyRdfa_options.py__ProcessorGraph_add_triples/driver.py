"""Validation driver for schemaorg__sdopythonapp__lib_pyRdfa_options.py__ProcessorGraph_add_triples.

add_triples(self, ...) writes an error structure into `self.graph` and returns
its blank node. What shows the region is the graph it leaves (triples, by
isomorphism; the typed `dcterms:date` literal included), the blank node it
returns, and the prefixes it binds ("lazy binding" at every call).

Time. The region stamps `datetime.datetime.utcnow().isoformat()`; two runs
never agree. The driver freezes `utcnow()` for BOTH sides by replacing the
`datetime` module in sys.modules before they are executed (each side is a
fork of this process): the clock is the only thing replaced, the stamp stays a
computed value, and a translation that drops the date, types it `xsd:string`,
or writes the lexical form differently is a difference.

Calls (a fresh `self` per call, as every side gets its own):
  * the bare case: no info class, no context, no node (full_msg = msg);
  * info class + string context + a node with `nodeName`;
  * URIRef context + a node WITHOUT `nodeName` (the `except` branch);
  * a context that is neither str nor URIRef (42) and a falsy one (""): no
    rdfa:context structure;
  * msg None (rdflib's Literal(None) is 'None': hence `{Literal(full_msg)}`);
  * a graph that already holds a neighbouring error structure, which must
    stay untouched.

Prefixes. The six `bind` calls became `@graph self.graph` with the prefixes of
the block, which does not overwrite a binding the graph already has. Whether
that matches the original's rebinding is not obvious, so a second phase
compares, in both directions, the namespace table and the triples left on
graphs prepared to disturb it: no default bindings, `ht`/`rdfa` already bound
to another namespace, a namespace already bound under another prefix, and two
calls in a row on one graph.
"""
import contextlib
import datetime as _real_datetime
import io
import sys
import types
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
RDFA = Namespace("http://www.w3.org/ns/rdfa#")


# -- a frozen clock, for both sides ---------------------------------------
class _FrozenDatetime(_real_datetime.datetime):
    @classmethod
    def utcnow(cls):
        return _real_datetime.datetime(2020, 2, 29, 12, 30, 45, 123456)


_fake = types.ModuleType("datetime")
_fake.__dict__.update({k: v for k, v in vars(_real_datetime).items()
                       if not k.startswith("__")})
_fake.datetime = _FrozenDatetime
sys.modules["datetime"] = _fake


# -- stand-ins -------------------------------------------------------------
class _Proc:
    """The ProcessorGraph instance: add_triples only reads `self.graph`."""

    def __init__(self, graph=None):
        self.graph = Graph() if graph is None else graph


class _Node:
    def __init__(self, name):
        self.nodeName = name


def _neighbour_graph():
    g = Graph()
    other = BNode("other")
    g.add((other, URIRef("http://purl.org/dc/terms/description"),
           Literal("an earlier error")))
    g.add((other, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
           RDFA["Warning"]))
    return g


ERROR, WARNING = RDFA["Error"], RDFA["Warning"]

CALLS = [
    lambda: ((_Proc(), "bad", ERROR, None, None, None), {}),
    lambda: ((_Proc(), "bad", ERROR, RDFA["DocumentError"],
              "http://example.org/page", _Node("div")), {}),
    lambda: ((_Proc(), "worse", WARNING, None,
              URIRef("http://example.org/u"), "span"), {}),
    lambda: ((_Proc(), "ctx int", ERROR, None, 42, None), {}),
    lambda: ((_Proc(), "ctx empty", ERROR, None, "", _Node("p")), {}),
    lambda: ((_Proc(), None, ERROR, None, None, None), {}),
    lambda: ((_Proc(), None, WARNING, RDFA["PGLinkedPageMissing"],
              "http://example.org/x y", _Node("a")), {}),
    lambda: ((_Proc(_neighbour_graph()), "bad", ERROR, None,
              "http://example.org/page", None), {}),
]

with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry='add_triples', calls=CALLS)


# -- phase 2: prefix tables on graphs prepared to disturb the rebinding -----
def _graphs():
    def none():
        return Graph(bind_namespaces="none")

    def ht_elsewhere():
        g = Graph()
        g.bind("ht", Namespace("http://example.org/not-http#"))
        g.bind("rdfa", Namespace("http://example.org/not-rdfa#"))
        return g

    def already_other_prefix():
        g = Graph(bind_namespaces="none")
        g.bind("dct", Namespace("http://purl.org/dc/terms/"))
        g.bind("xs", Namespace("http://www.w3.org/2001/XMLSchema#"))
        g.bind("pyrdfa", Namespace("http://example.org/mine#"))
        return g

    return {"none": none, "ht_elsewhere": ht_elsewhere,
            "already_other_prefix": already_other_prefix,
            "default": Graph}


def _table(g):
    return sorted((p, str(n)) for p, n in g.namespaces())


if VERDICT.get("error") is None:
    try:
        sys.modules.pop("context_shim", None)
        ns_o, _ = harness._exec_python(HERE / "original.py")
        sys.modules.pop("context_shim", None)
        ns_t, _ = harness._exec_ldpy(HERE / "translated.ldpy")
        for label, make in _graphs().items():
            res = {}
            for side, ns in (("original", ns_o), ("translation", ns_t)):
                proc = _Proc(make())
                ns["add_triples"](proc, "m", ERROR, WARNING, "http://e/c", _Node("n"))
                ns["add_triples"](proc, "m2", WARNING, None, None, None)
                res[side] = proc.graph
            o, t = res["original"], res["translation"]
            if not isomorphic(o, t):
                VERDICT["diffs"].append(f"{label}: triples differ after two calls")
            if _table(o) != _table(t):
                to, tt = set(_table(o)), set(_table(t))
                VERDICT["diffs"].append(
                    f"{label}: namespace tables differ: only original "
                    f"{sorted(to - tt)}, only translation {sorted(tt - to)}")
        VERDICT["tables_compared"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"prefix phase: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)
