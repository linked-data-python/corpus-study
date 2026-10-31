"""Validation driver for dtai-kg__SCOOP__SCOOP_shape_integration_priority.py__ShapeIntegrationPriority___init__.

`__init__` is an unbound method extracted as a plain function: `self` must
be supplied explicitly.  A minimal stand-in with value-based equality lets
the harness compare the attributes the constructor sets, the same way it
would compare a dataclass instance.

Two runs:

  as-written -- run_pair, two calls (two shapes and an output path; no shape
    and an empty path).  `self.random_number` is excluded from `_Self`'s
    equality there: the shared `random` module is in a different state for
    each side's call.

  extended -- each side called directly, and compared on everything the
    constructor decides.  Value equality alone is blind to the type of what
    is stored: `Namespace('…#') == '…#'` and `URIRef('…#') == Namespace('…#')`
    are both true, so a `self.shaclNS` stored as a `str` or a `URIRef` passed
    the as-written run.  The rest of the class needs the Namespace OBJECT
    (`self.shaclNS.targetClass`, `self.rdfSyntax.first`, …), so:
      * the same attribute names on both sides;
      * the same type for every attribute, and for every element of the two
        term lists (Namespace, URIRef);
      * the same values; `self.SHACL` by isomorphism, and its prefix
        bindings: the class serialises it (shape_integration_priority.py:433),
        so every binding of the original's must be on the translation's;
      * `self.random_number`, with `random.seed(1234)` before each side's
        call, so both draw the same 1000 numbers;
      * `self.shapes` and `self.output` are the very objects passed in.
    Cases:
      A the repository's real input shape: main.py:84-99 passes a list of
        `(Graph, path)` pairs, parsed from Turtle files, and an output path;
      B the as-written inputs again (two strings, no shape at all).
"""
import contextlib
import io
import json
import random
import sys
from pathlib import Path

from rdflib import Graph

from rdfeval import harness
from rdfeval.harness import run_pair, graphs_isomorphic

ex_dir = Path(__file__).resolve().parent


class _Self:
    """Stand-in for the real object `__init__` is called on."""

    def __eq__(self, other):
        if not isinstance(other, _Self):
            return NotImplemented
        keys = (set(vars(self)) | set(vars(other))) - {"random_number"}
        for k in keys:
            a, b = getattr(self, k, None), getattr(other, k, None)
            if isinstance(a, Graph) and isinstance(b, Graph):
                if not graphs_isomorphic(a, b):
                    return False
            elif a != b:
                return False
        return True

    def __repr__(self):
        return f"_Self({ {k: v for k, v in vars(self).items() if k != 'random_number'} !r})"


def _shape_graph(n):
    g = Graph()
    g.parse(data=f"""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix ex: <http://example.org/> .
        ex:Shape{n} a sh:NodeShape ; sh:targetClass ex:C{n} ;
            sh:property [ sh:path ex:p{n} ; sh:minCount 1 ] .
        """, format="turtle")
    return g


CASES = [
    ("A real shapes", lambda: ([(_shape_graph(1), "shapes/one.ttl"),
                                (_shape_graph(2), "shapes/two.ttl")],
                               "integrated.ttl")),
    ("B as-written", lambda: (["shape1", "shape2"], "output.ttl")),
]


def _types(value):
    if isinstance(value, (list, tuple)):
        return (type(value).__name__, tuple(_types(v) for v in value))
    return type(value).__name__


def _bound(g):
    return {(p, str(n)) for p, n in g.namespaces()}


def _call(ns, shapes, output):
    self = _Self()
    random.seed(1234)
    ns["__init__"](self, shapes, output)
    return self, shapes, output


def _extended():
    left, right = harness.sides_from_env()
    ns_o, _ = harness._exec_artefact(ex_dir / left, "__original__")
    ns_t, _ = harness._exec_artefact(ex_dir / right, "__translated__")
    diffs = []
    for label, make in CASES:
        so, sh_o, out_o = _call(ns_o, *make())
        st, sh_t, out_t = _call(ns_t, *make())
        if set(vars(so)) != set(vars(st)):
            diffs.append(f"{label}: attributes differ "
                         f"{sorted(vars(so))} vs {sorted(vars(st))}")
            continue
        for k in sorted(vars(so)):
            a, b = vars(so)[k], vars(st)[k]
            if _types(a) != _types(b):
                diffs.append(f"{label}: self.{k} type {_types(a)} vs {_types(b)}")
            if isinstance(a, Graph) and isinstance(b, Graph):
                if not graphs_isomorphic(a, b):
                    diffs.append(f"{label}: self.{k} not isomorphic")
                missing = _bound(a) - _bound(b)
                if missing:
                    diffs.append(f"{label}: self.{k} prefix bindings lost "
                                 f"{sorted(missing)}")
            elif k not in ("shapes", "output") and a != b:
                diffs.append(f"{label}: self.{k} values differ")
        if (so.shapes is sh_o) != (st.shapes is sh_t):
            diffs.append(f"{label}: self.shapes is / is not the list passed in")
        if (so.output is out_o) != (st.output is out_t):
            diffs.append(f"{label}: self.output is / is not the path passed in")
    return diffs


def _quiet(**kwargs) -> dict:
    """run_pair's verdict without its stderr line: this driver emits one."""
    with contextlib.redirect_stderr(io.StringIO()):
        return run_pair(**kwargs)


as_written = _quiet(
    driver_file=__file__,
    entry='__init__',
    calls=[
        lambda: ((_Self(), ["shape1", "shape2"], "output.ttl"), {}),
        lambda: ((_Self(), [], ""), {}),
    ],
)
try:
    extended, extended_error = _extended(), None
except Exception:
    import traceback
    extended, extended_error = [], traceback.format_exc(limit=8)

verdict = dict(as_written)
verdict["method"] = (f"{as_written.get('method')} (as-written + extended: "
                     "attribute types, seeded random, bindings, real inputs)")
verdict["diffs"] = ([f"as-written: {d}" for d in as_written.get("diffs", [])]
                    + [f"extended: {d}" for d in extended])
errors = [e for e in (as_written.get("error"), extended_error) if e]
verdict["error"] = "\n".join(errors) or None
verdict["calls"] = 2 + len(CASES)
verdict["equivalent"] = (bool(as_written.get("equivalent"))
                         and not extended and not extended_error)
print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
