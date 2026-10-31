"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_query_property_shape.py__get_property_by_property_shape.

This region READS a graph: `name = ... or profile_graph.value(property_shape,
SH.name) or ...`, extracted as a bare STATEMENT (not a function) from inside
`get_property_by_property_shape`.  The missing bindings -- `kwargs`,
`profile_graph`, `property_shape`, `sh_path`, `db` -- are restored as
parameters of a wrapping function `compute_name` (see original.py /
translated.ldpy).  That wrapper is also what makes `name` observable at all:
`run_pair`'s module-state path (entry=None) only compares rdflib Graphs and
stdout, and `profile_graph` here is read-only, so comparing it would be
vacuous -- it is identical on both sides by construction, regardless of
whether `.value()` was translated correctly.  entry="compute_name" compares
the actual return value instead, which is the point of the region.

`fixture.ttl` is `profile_graph`.  Two calls exercise the two branches of the
`or` chain that this statement's stratum (trav_single_value) is about:
  * with_sh_name    -- `.value()`/`m{ }.first()` finds ex:hasName's sh:name
                       directly (one of several sh:name solutions in the
                       graph);
  * without_sh_name -- ex:noName has no sh:name, so `.value()`/`.first()`
                       both answer None (the zero-solution case) and the
                       statement falls through to get_name(sh_path, ...),
                       itself reading ex:pathNode's rdfs:label.
Neither call ever reads ex:unrelated's sh:name (the neighbourhood).

Calls added by the mutation audit of 2026-10-31.  In the repository
`profile_graph` is never a bare Graph: it is `db.graph(profile_iri)`, a named
graph of the ProfilesDataset `db` (property_shape.py:278), whose triples were
added with `+=` (loader.py:105-146, which carries no prefix binding), and
whose NamespaceManager is the dataset's own, shared by every graph of `db`.
Before any query, Supermodel.__init__ copies every prefix of the user's input
file onto it with override=True (query/__init__.py:428-429).  `_dataset_case`
rebuilds exactly that, for an input file that declares
`@prefix shacl: <http://www.w3.org/ns/shacl#>`:
  * dataset_qname    -- no sh:name, and sh_path a SHACL IRI with no label in
                        the graph nor in `db`: get_name falls back to
                        `graph.qname(iri)` (common.py:41-43), which reads the
                        bindings -- "shacl:targetClass" in the repository;
  * dataset_kwargs   -- kwargs["name"] given, so the region never reads the
                        graph: nothing may change in the dataset's bindings;
  * dataset_two      -- two sh:name values: value() takes the first, never
                        raises (kills `.one()`);
  * dataset_empty    -- sh:name "": present but falsy, falls through;
  * dataset_bnode    -- a blank-node property shape.
After every call the driver compares the returned name (or the raised
exception), `profile_graph` by isomorphism, and requires each prefix binding
the original's dataset holds to be in the translation's (record ldpy/027
tolerates extra ones): `profile_graph` and `db` share that manager, and
pyLODE renders every later name of the run through it.

These five calls are driven by hand, not through run_pair's `calls=`:
run_pair compares every argument, and a Graph argument by isomorphism,
which rdflib 7.2.1 cannot compute on a Dataset (`to_isomorphic` iterates it
as triples and meets quads).  Their diffs are merged into run_pair's single
verdict (its `_emit` is wrapped), since `rdfeval check` reads only the first
verdict line.  rdflib 7.2.1's `Dataset.add_graph` registers a graph without
copying its triples (pyLODE requires rdflib >= 7.6), so the triples are added
to the named graph itself, still with `+=`.
"""
from rdflib import SH, Dataset, URIRef

from rdfeval import harness
from rdfeval.harness import fixture_graph, run_pair, sides_from_env

from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = "fixture.ttl"
EX = "http://example.org/shapes/"
HAS_NAME = URIRef("http://example.org/shapes/hasName")
NO_NAME = URIRef("http://example.org/shapes/noName")
PATH_NODE = URIRef("http://example.org/shapes/pathNode")
PROFILE = URIRef("http://example.org/profiles/p1")
ROOT = URIRef("http://example.org/profiles/root")


def with_sh_name():
    return (({}, fixture_graph(FIXTURE), HAS_NAME, None, Dataset()), {})


def without_sh_name():
    return (({}, fixture_graph(FIXTURE), NO_NAME, PATH_NODE, Dataset()), {})


def _dataset_args(kwargs, shape, sh_path):
    db = Dataset(default_union=True)               # ProfilesDataset.__init__
    profile_graph = db.graph(PROFILE)              # property_shape.py:278
    profile_graph += fixture_graph(HERE / FIXTURE)  # loader.py: `__iadd__`
    # query/__init__.py:428-429, for an input file that binds SHACL as
    # `shacl:` -- every graph of `db` shares this manager.
    db.graph(ROOT).namespace_manager.bind("shacl", SH, override=True)
    if shape == "bnode":
        shape = profile_graph.value(URIRef(EX + "holder"), SH.property)
    return (dict(kwargs), profile_graph, shape, sh_path, db)


DATASET_CASES = [
    ("dataset_qname", {}, NO_NAME, SH.targetClass),
    ("dataset_kwargs", {"name": "Given"}, HAS_NAME, None),
    ("dataset_two", {}, URIRef(EX + "twoNames"), None),
    ("dataset_empty", {}, URIRef(EX + "emptyName"), PATH_NODE),
    ("dataset_bnode", {}, "bnode", None),
]


def _bindings(db):
    return {(p, str(n)) for p, n in db.namespaces()}


def _dataset_diffs():
    left, right = sides_from_env()
    ns_o, _ = harness._exec_artefact(HERE / left, "__original__")
    ns_t, _ = harness._exec_artefact(HERE / right, "__translated__")
    fo, ft = ns_o["compute_name"], ns_t["compute_name"]
    diffs = []
    for label, kwargs, shape, sh_path in DATASET_CASES:
        args_o = _dataset_args(kwargs, shape, sh_path)
        args_t = _dataset_args(kwargs, shape, sh_path)
        ro = harness._outcome(fo, args_o, {})
        rt = harness._outcome(ft, args_t, {})
        if isinstance(ro, harness.Raised) or isinstance(rt, harness.Raised):
            if ro != rt:
                diffs.append(f"{label}: outcome differs ({ro!r} vs {rt!r})")
        else:
            harness._compare_value(ro, rt, f"{label}.result", diffs)
        harness._compare_value(args_o[1], args_t[1], f"{label}.profile_graph",
                               diffs)
        lost = sorted(_bindings(args_o[4]) - _bindings(args_t[4]))
        if lost:
            diffs.append(f"{label}: prefix bindings of the original lost in "
                         f"the translation: {lost}")
    return diffs


_emit = harness._emit


def _emit_with_datasets(verdict):
    try:
        extra = _dataset_diffs()
    except Exception as e:                      # noqa: BLE001 - reported
        extra = [f"dataset cases: driver error {type(e).__name__}: {e}"]
    verdict["diffs"] = list(verdict.get("diffs") or []) + extra
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not extra
    verdict["calls"] = verdict.get("calls", 0) + len(DATASET_CASES)
    _emit(verdict)


harness._emit = _emit_with_datasets

VERDICT = run_pair(
    __file__,
    entry='compute_name',
    fixture=FIXTURE,
    calls=[with_sh_name, without_sh_name],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
