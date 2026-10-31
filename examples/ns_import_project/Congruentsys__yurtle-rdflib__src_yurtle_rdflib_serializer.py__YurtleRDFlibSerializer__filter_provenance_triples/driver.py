"""Validation driver for Congruentsys__yurtle-rdflib__src_yurtle_rdflib_serializer.py__YurtleRDFlibSerializer__filter_provenance_triples.

`demo()` (identical on both sides, appended after the extracted region --
see meta.json) builds a minimal fake `self` (a `.store` graph) and calls
`_filter_provenance_triples(self)`, returning the filtered graph.

Two runs:

  as-written -- run_pair, one call to `demo()`: the filtered graph, compared
    by isomorphism.  Its store isolates the two filters (a provenance
    predicate with a non-file object, a file:// object under another
    predicate) beside two kept triples.

  extended -- `_filter_provenance_triples` called directly on each side,
    with stores of the repository's real shapes, and compared on everything
    the region decides:
      * the filtered graph, by isomorphism;
      * whether it is a new graph (never the store itself);
      * its prefix bindings.  The region copies the store's bindings into
        the new graph, and the caller serialises it to a Yurtle file
        (serializer.py:105-108), so every binding of the original's graph
        must be on the translation's (extras tolerated, record ldpy/027).
        The stores carry the bindings the repository puts on them: `prov`,
        `yurtle`, `pm`, `being` (store.py:133-136), or the header of a
        parsed Yurtle file.  An `@graph filtered` in place of the `(filtered)`
        call suffix would bind the imported prefixes, `provenance:` among
        them, and take the namespace away from the store's `prov`: it fails
        here, and in the as-written run it would not;
      * what it prints, and what it raises (type and message).
    Cases:
      A store.py's bindings; a BNode subject, language-tagged, typed and
        xsd:string literals, a Literal that merely starts with "file://"
        (kept: not a URIRef), a file:// URIRef in SUBJECT position (kept),
        definedIn with a file:// object, definedIn with a literal, a file://
        object under another predicate, a BNode object;
      B the same bindings, no triple at all: an empty graph, bindings still
        copied;
      C a store parsed from a Yurtle-style Turtle header that binds the
        provenance namespace as `prov` and a project prefix `ex`.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from rdfeval import harness
from rdfeval.harness import run_pair

ex_dir = Path(__file__).resolve().parent

# yurtle_rdflib/namespaces.py, verbatim IRIs
YURTLE = Namespace("https://yurtle.dev/schema/")
PM = Namespace("https://yurtle.dev/pm/")
BEING = Namespace("https://yurtle.dev/being/")
PROVENANCE = Namespace("https://yurtle.dev/provenance/")


def _store_bindings(g):
    """YurtleStore.__init__ (store.py:133-136)."""
    g.bind("prov", PROVENANCE)
    g.bind("yurtle", YURTLE)
    g.bind("pm", PM)
    g.bind("being", BEING)
    return g


def _case_a():
    g = _store_bindings(Graph())
    alice, b = BEING.alice, BNode("task")
    g.add((alice, PM.status, Literal("active")))
    g.add((b, PM.title, Literal("titre", lang="fr")))
    g.add((b, PM.priority, Literal(3)))
    g.add((b, PM.due, Literal("2026-10-30", datatype=XSD.date)))
    g.add((b, PM.note, Literal("x", datatype=XSD.string)))
    g.add((b, PM.link, Literal("file:///not-a-uri.md")))
    g.add((URIRef("file:///notes/alice.md"), PM.owner, alice))
    g.add((alice, PROVENANCE.definedIn, URIRef("file:///notes/alice.md")))
    g.add((b, PROVENANCE.definedIn, Literal("notes/task.md")))
    g.add((alice, YURTLE.source, URIRef("file:///notes/other.md")))
    g.add((alice, BEING.knows, BNode("bob")))
    return g


def _case_b():
    return _store_bindings(Graph())


def _case_c():
    g = Graph()
    g.parse(data="""
        @prefix prov: <https://yurtle.dev/provenance/> .
        @prefix pm: <https://yurtle.dev/pm/> .
        @prefix ex: <http://example.org/project/> .
        ex:task1 a pm:Task ; pm:status "open" ;
            prov:definedIn <file:///work/task1.md> .
        ex:task2 pm:dependsOn ex:task1 ; prov:definedIn "task2.md" .
        """, format="turtle")
    return g


CASES = [("A store.py", _case_a), ("B empty", _case_b), ("C parsed", _case_c)]


def _bound(g):
    return {(p, str(n)) for p, n in g.namespaces()}


def _call(ns, store):
    self = ns["FakeSerializer"](store)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            result, raised = ns["_filter_provenance_triples"](self), None
        except Exception as e:                    # noqa: BLE001 - compared
            result, raised = None, (type(e).__name__, str(e))
    return {"result": result, "raised": raised, "stdout": out.getvalue(),
            "store": store}


def _extended():
    left, right = harness.sides_from_env()
    ns_o, _ = harness._exec_artefact(ex_dir / left, "__original__")
    ns_t, _ = harness._exec_artefact(ex_dir / right, "__translated__")
    diffs = []
    for label, make in CASES:
        o, t = _call(ns_o, make()), _call(ns_t, make())
        if o["raised"] != t["raised"]:
            diffs.append(f"{label}: outcome differs ({o['raised']} vs {t['raised']})")
        if o["stdout"] != t["stdout"]:
            diffs.append(f"{label}: stdout differs")
        ro, rt = o["result"], t["result"]
        if ro is None or rt is None:
            if (ro is None) != (rt is None):
                diffs.append(f"{label}: one side returned no graph")
            continue
        if not harness.graphs_isomorphic(ro, rt):
            diffs.append(f"{label}: filtered graphs not isomorphic "
                         f"({len(ro)} vs {len(rt)} triples)")
        if (ro is o["store"]) != (rt is t["store"]):
            diffs.append(f"{label}: result is / is not the store itself")
        missing = _bound(ro) - _bound(rt)
        if missing:
            diffs.append(f"{label}: prefix bindings lost {sorted(missing)}")
        if not harness.graphs_isomorphic(o["store"], t["store"]):
            diffs.append(f"{label}: store modified differently")
    return diffs


def _quiet(**kwargs) -> dict:
    """run_pair's verdict without its stderr line: this driver emits one."""
    with contextlib.redirect_stderr(io.StringIO()):
        return run_pair(**kwargs)


as_written = _quiet(driver_file=__file__, entry='demo', calls=[((), {})])
try:
    extended, extended_error = _extended(), None
except Exception:
    import traceback
    extended, extended_error = [], traceback.format_exc(limit=8)

verdict = dict(as_written)
verdict["method"] = (f"{as_written.get('method')} (as-written + extended: "
                     "bindings, real store shapes, stdout, raises)")
verdict["diffs"] = ([f"as-written: {d}" for d in as_written.get("diffs", [])]
                    + [f"extended: {d}" for d in extended])
errors = [e for e in (as_written.get("error"), extended_error) if e]
verdict["error"] = "\n".join(errors) or None
verdict["calls"] = 1 + len(CASES)
verdict["equivalent"] = (bool(as_written.get("equivalent"))
                         and not extended and not extended_error)
print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
