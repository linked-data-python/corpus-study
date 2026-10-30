"""Validation driver for binary-array-ld__bald__nc2rdf_nc2rdf.py__baldgraph2schemaorg.

Establishes semantic equivalence of original.py and translated.ldpy.

Hand-written (not `run_pair`): the region returns a graph, and the
repository does not stop at the triples.  `nc2schemaorg` (nc2rdf.py:96-104)
calls `schema_g.serialize(format=outformat)` on the returned graph, which
reads the graph's namespace bindings: a prefix bound on the returned graph
shows up as `so:Dataset` where the original prints `<http://schema.org/Dataset>`
(turtle, n3) or an `ns1:` prefix (xml).  So each call compares, for the
original and the translation, either the exception (type and message) or
three observations of the returned graph: isomorphism, its namespace
bindings (`list(g.namespaces())`), and its serialisation in turtle, n3 and
xml, with the identifiers of anonymous nodes normalised.

Calls (all in a directory holding `bald2schemaorg_mappings.json`):

  0. `path=None, baseuri=None`: a blank-node container, no url, with the
     input graph of `_input_graph()` (a plain field, a `keywords` field with
     blank entries, an unmapped predicate that must not appear, a padded
     predicate name, a non-string object, an empty literal, a typed literal, and a second container).
  1. an http `path` and a `baseuri`: the `isUrl(path)` guard is true, the
     `schema:url` triple holds `URIRef(path)` (an IRI, not a literal) and
     the container is the IRI `URIRef(baseuri)`.
  2. a `baseuri` and a path that is not a URL (`"data/f.nc"`): `isUrl` false,
     the container is an IRI, no url triple.
  3. an http `path` and no `baseuri`: the url triple hangs on a blank node.
  4. `baseuri=""` (not None, so `URIRef("")`) and `path=""` (falsy, not a URL).
  5. `path=5`: `isUrl` swallows the error and the url triple is skipped.
  6. a graph with no container: only the type triple (zero solutions).
  7. `graph=None`: the exception raised by `graph.query` (type and message).
"""
import json
import re
import sys
import traceback
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

from rdfeval import harness

BALD = Namespace("http://binary-array-ld.net/latest/")
NC = Namespace("http://example.org/nc/")


def _input_graph():
    """A fresh graph with bald:Container subjects and the values the mapping
    table (bald2schemaorg_mappings.json) distinguishes."""
    g = Graph()
    c = URIRef("http://example.org/dataset/1")
    g.add((c, RDF.type, BALD.Container))
    g.add((c, NC.summary, Literal("A test dataset")))
    g.add((c, NC.keywords, Literal("alpha, beta, , gamma")))
    # an empty literal and a typed one go through Literal(row[1]) unchanged
    g.add((c, NC.title, Literal("")))
    g.add((c, NC.id, Literal(7)))
    # a non-literal object (an IRI) is turned into a literal by Literal(row[1])
    g.add((c, NC.license, URIRef("http://example.org/licence/by")))
    # a predicate whose basename carries trailing white space: mapped only
    # because the region strips it
    g.add((c, URIRef(str(NC) + "summary "), Literal("padded field")))
    # Unmapped predicate: must not appear at all in the schema.org graph.
    g.add((c, NC.unmapped_field, Literal("ignored")))
    # a subject that is not a bald:Container: its triples must not be read
    other = URIRef("http://example.org/dataset/2")
    g.add((other, NC.summary, Literal("not a container")))
    return g


def _container_only_graph():
    g = Graph()
    g.add((BNode("c"), RDF.type, BALD.Container))
    return g


def _no_container_graph():
    g = Graph()
    g.add((URIRef("http://example.org/x"), NC.summary, Literal("orphan")))
    return g


CALLS = [
    lambda: ((_input_graph(),), {}),
    lambda: ((_input_graph(), "http://example.org/f.nc",
              "http://example.org/d"), {}),
    lambda: ((_input_graph(),), {"path": "data/f.nc",
                                 "baseuri": "http://example.org/d"}),
    lambda: ((_input_graph(), "https://example.org/f.nc"), {}),
    lambda: ((_input_graph(), "", ""), {}),
    lambda: ((_input_graph(), 5), {}),
    lambda: ((_no_container_graph(),), {}),
    lambda: ((_container_only_graph(), "http://example.org/f.nc"), {}),
    lambda: ((None,), {}),
]

_BNODE = re.compile(r"\b(N[0-9a-f]{32}|n[0-9a-f]{32}|ub\d+bL\d+C\d+)\b")


def _observe(g):
    """What the repository can read off the returned graph."""
    obs = {"namespaces": sorted((p, str(n)) for p, n in g.namespaces())}
    for fmt in ("turtle", "n3", "xml"):
        text = g.serialize(format=fmt)
        text = text.decode("utf-8") if isinstance(text, bytes) else text
        obs[fmt] = _BNODE.sub("BNODE", text)
    return obs


def _outcome(fn, args, kwargs):
    try:
        g = fn(*args, **kwargs)
    except Exception as e:                      # noqa: BLE001 - compared
        return ("raised", type(e).__name__, str(e)), None
    return ("returned",), g


ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:baldgraph2schemaorg (custom: isomorphism, "
                           "namespace bindings, turtle/n3/xml serialisation)",
                 "diffs": [], "error": None, "calls": len(CALLS)}
try:
    ns_o, _ = harness._exec_python(ex_dir / "original.py")
    ns_t, _ = harness._exec_ldpy(ex_dir / "translated.ldpy")
    fo, ft = ns_o["baldgraph2schemaorg"], ns_t["baldgraph2schemaorg"]
    diffs = []
    for i, case in enumerate(CALLS):
        args_o, kw_o = case()
        args_t, kw_t = case()
        out_o, go = _outcome(fo, args_o, kw_o)
        out_t, gt = _outcome(ft, args_t, kw_t)
        if out_o != out_t:
            diffs.append(f"call[{i}]: outcome differs ({out_o} vs {out_t})")
            continue
        if go is None:
            continue
        if not harness.graphs_isomorphic(go, gt):
            diffs.append(f"call[{i}]: graphs not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")
        obs_o, obs_t = _observe(go), _observe(gt)
        for key in obs_o:
            if obs_o[key] != obs_t[key]:
                diffs.append(f"call[{i}]: {key} differs "
                             f"({obs_o[key]!r} vs {obs_t[key]!r})"[:400])
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    verdict["observed"] = True
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
