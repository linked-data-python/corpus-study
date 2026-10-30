"""Validation driver for BrickSchema__Brick__generate_brick.py__define_relationships.

The region BUILDS a graph (it mutates the `graph=` keyword argument in
place, and never returns it) so the oracle is RDF isomorphism (meta.oracle
== "isomorphism"), established here on the `graph` kwarg after the call
(run_pair compares kwargs post-call: "une region peut muter son graphe").

`definitions` must be constructed fresh for each of the two calls run_pair
makes (one per side): the region itself mutates it in place via
`propdefn.pop("range"/"datatype"/"domain")`, so a shared dict would answer
the second call with the keys the first call already consumed. Hence a
callable case, not a static (args, kwargs) tuple.

The fixture definitions dict exercises: a property already a URIRef key
(hasPoint) vs. a plain-string key (hasUnit, hasQuantity, hasCount) that
`prop = BRICK[prop]` must convert; recursion via "subproperties" (exercises
the `superprop is not None` -> rdfs:subPropertyOf branch, absent at the top
level); "range" as a list (BNode enumeration + rdf:Collection, via the SHACL
sh:or branch) and as a single value (the sh:class elif branch); "datatype"
equal to BSH.NumericValue (the sh:or branch) and different (the sh:datatype
branch); "domain" as a list; and extra keys of all three shapes
add_relationships itself branches on (a list, a scalar, and a dict which it
silently skips).

Cases added by the mutation audit of 2026-10-30, each killing mutants of
the Python guards around the islands that the first case left alive:

  * `_case_shapes`: a key that is a URIRef OUTSIDE the Brick namespace
    (rec:includes, typed, no range/datatype/domain) -- the only input on
    which `if prop.startswith(BRICK):` is false, so forcing either of the
    two guards to True adds triples; a "range" given as a TUPLE (the
    `(tuple, list)` test: as `list` only, it would take the sh:class
    branch); and "range": None (the `elif range_defn is not None:` guard:
    forced to True, the translation would write Literal("None")).
    relationships.py itself only has str keys, list or single ranges; these
    are inputs the function's own branches are written for.
  * `_case_empty`: definitions == {} -- the early return.
  * the repository's bindings (second phase, hand-rolled below): in
    generate_brick.py the graph is `G`, on which line 74 calls
    `bind_prefixes(G)` (bricksrc/namespaces.py:35-56, 21 prefixes) before
    serialising it at lines 1123, 1146, 1176.  `@graph graph` binds the 13
    prefixes this file declares on that same graph; the phase runs the
    first case on a graph carrying the repository's bindings and requires
    every binding of the original's graph to be in the translation's
    (`@graph` may add, record ldpy/027, not replace).

Mutants that survive and are equivalent on every input the repository can
give: `if superprop is not None:` -> `if superprop:` (superprop is the
parent property, a non-empty URIRef), `elif range_defn:` (ranges are
URIRefs, lists or None), `if len(definitions) == 0:` forced to False (an
empty dict runs no loop; the only trace is `@graph` binding prefixes, which
the repository's graph already has under the same names).
"""
import contextlib
import io
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.compare import to_isomorphic

from brick_context import BRICK, BSH, QUDT, RDF, RDFS, OWL, REC, TAG
from rdfeval.harness import _emit, _exec_ldpy, _exec_python, run_pair

HERE = Path(__file__).resolve().parent


def _definitions():
    return {
        BRICK["hasPoint"]: {
            RDF.type: [OWL.ObjectProperty],
            "subproperties": {
                "hasSensor": {
                    RDF.type: [OWL.ObjectProperty],
                },
            },
            "range": [BRICK.Point, BRICK.Sensor],
            "domain": [BRICK.Equipment, BRICK.System],
            BRICK.hasAssociatedTag: [TAG.Point],
            RDFS.label: Literal("has point", lang="en"),
            BRICK.hasQuantity: {"foo": "bar"},  # add_relationships must skip this (a dict)
        },
        "hasUnit": {
            "range": QUDT.Unit,               # single value, not a list
            "domain": BRICK.Quantifiable,
        },
        "hasQuantity": {
            "datatype": BSH.NumericValue,
        },
        "hasCount": {
            "datatype": URIRef("http://example.org/customtype"),
        },
    }


def _case():
    return (), {"definitions": _definitions(), "graph": Graph()}


def _case_shapes():
    return (), {"definitions": {
        REC["includes"]: {
            RDF.type: [OWL.ObjectProperty],
            RDFS.label: Literal("includes", lang="en"),
        },
        "isPointOf": {
            "range": (BRICK.Equipment, BRICK.Location),
        },
        "aliasOf": {
            "range": None,
            "domain": BRICK.Entity,
        },
    }, "graph": Graph()}


def _case_empty():
    return (), {"definitions": {}, "graph": Graph()}


with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(
        __file__,
        entry="define_relationships",
        calls=[_case, _case_shapes, _case_empty],
    )

# bricksrc/namespaces.py:3-29 and 35-56 of BrickSchema/Brick@c12949f236.
REPO_BINDINGS = [
    ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("owl", "http://www.w3.org/2002/07/owl#"),
    ("dcterms", "http://purl.org/dc/terms/"),
    ("sdo", "http://schema.org/"),
    ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
    ("skos", "http://www.w3.org/2004/02/skos/core#"),
    ("sosa", "http://www.w3.org/ns/sosa/"),
    ("sh", "http://www.w3.org/ns/shacl#"),
    ("brick", "https://brickschema.org/schema/Brick#"),
    ("ref", "https://brickschema.org/schema/Brick/ref#"),
    ("tag", "https://brickschema.org/schema/BrickTag#"),
    ("vcard", "http://www.w3.org/2006/vcard/ns#"),
    ("bsh", "https://brickschema.org/schema/BrickShape#"),
    ("qudtqk", "http://qudt.org/vocab/quantitykind/"),
    ("qudt", "http://qudt.org/schema/qudt/"),
    ("unit", "http://qudt.org/vocab/unit/"),
    ("xsd", "http://www.w3.org/2001/XMLSchema#"),
    ("bacnet", "http://data.ashrae.org/bacnet/"),
    ("ifc", "https://brickschema.org/extension/ifc#"),
    ("s223", "http://data.ashrae.org/standard223#"),
    ("rec", "https://w3id.org/rec#"),
]


def _repo_graph():
    g = Graph()
    for prefix, iri in REPO_BINDINGS:
        g.bind(prefix, iri)
    return g


if not VERDICT.get("error"):
    extra = []
    ns_o, _ = _exec_python(HERE / "original.py")
    ns_t, _ = _exec_ldpy(HERE / "translated.ldpy")
    go, gt = _repo_graph(), _repo_graph()
    ns_o["define_relationships"](_definitions(), graph=go)
    try:
        ns_t["define_relationships"](_definitions(), graph=gt)
    except Exception as e:                        # noqa: BLE001 - reported
        extra.append(f"repo bindings: translation raised {type(e).__name__}: {e}")
    if to_isomorphic(go) != to_isomorphic(gt):
        extra.append(f"repo bindings: graphs not isomorphic ({len(go)} vs {len(gt)} triples)")
    lost = sorted({(p, str(u)) for p, u in go.namespaces()}
                  - {(p, str(u)) for p, u in gt.namespaces()})
    if lost:
        extra.append(f"repo bindings: prefix bindings of the original lost in the translation: {lost}")
    VERDICT["method"] += " + repo bindings"
    VERDICT["diffs"] = VERDICT["diffs"] + extra
    VERDICT["equivalent"] = not VERDICT["diffs"]

_emit(VERDICT)
