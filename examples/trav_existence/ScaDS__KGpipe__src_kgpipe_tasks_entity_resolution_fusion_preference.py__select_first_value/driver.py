"""Validation driver for ScaDS__KGpipe__src_kgpipe_tasks_entity_resolution_fusion_preference.py__select_first_value.

`select_first_value` reads two graphs from N-Triples FILES and writes its
result to another file, so the oracle here is not `fixture=` (which passes
ONE parsed Graph as the entry point's single argument): the region's own
signature is `select_first_value(inputs, outputs)`, both dicts of `Data`
objects wrapping file paths. `entry` is instead the `demo` harness both
files carry identically (see meta.json and the note in `original.py`): it
writes `source_nt`/`target_nt` to a fresh temp dir, points a minimal
`OntologyUtil` shim (context_shim.py) at `ontology_props`, runs the region,
and returns the graph parsed back from `outputs["output"].path` -- design
record corpus/405's "equality of the values produced from the same input
graph", just with the graph delivered and collected through files because
the region itself does.

This region carries TWO trav_existence reads:

  (1) `not any(seed_graph.objects(s_can, p_can))`, in the FUSABLE branch --
      gates whether a value is adopted for a (subject, cardinality-1
      predicate) pair AT ALL. Both directions are observable in the final
      graph: guard wrongly True adds a second value where only one should
      survive (extra triple); guard wrongly False drops the sole value
      (missing triple).
  (2) `(s_can, p_can, o_can) not in seed_graph`, in the NON-FUSABLE branch --
      guards a `.add()` of the SAME triple regardless of the guard's
      result, and `Graph.add` is idempotent (a set): when the triple is
      ALREADY present, whether the guard fires or not, the resulting graph
      is identical either way. So only ONE direction of this specific guard
      is observable through the region's own output -- "wrongly thinks an
      ABSENT triple is present" (skips an add that should happen, so the
      triple goes missing) -- never the other ("wrongly thinks a PRESENT
      triple is absent", since re-adding it changes nothing). The fixture
      below still includes an already-present case (s4) for realism, but it
      cannot discriminate a correct translation from an incorrect one on
      its own; that is a property of the region's OWN idempotent-add
      design, not a gap in this driver -- see the note in meta.json.

One call exercises every subject the region would ever see together, since
`select_first_value` processes the whole `source_graph` in one pass and
nothing here makes different subjects interact:

  s1  fusable (rdfs:label), seed ALREADY has "existing" -> "new" from
      source must NOT be added (check 1, guard-False direction)
  s2  fusable (rdfs:label), absent from seed entirely -> "firstval" MUST be
      added (check 1, guard-True direction)
  s3  non-fusable (skos:altLabel); seed has "seedAlt" for s3, source offers
      a DIFFERENT object "sourceAlt" -> "sourceAlt" MUST be added (check 2,
      the one discriminating direction; also proves the pattern matches on
      the object, not just subject+predicate: a translation that dropped
      the object would see s3+skos:altLabel already present and skip it)
  s4  non-fusable, EXACT triple already in both graphs -> no change either
      way (non-discriminating, see above)
  s5  predicate NOT in allowed_predicates at all -> skipped entirely by
      surrounding (untranslated) Python logic, never reaches either check;
      included so a translation that accidentally widened a pattern and
      started matching/copying everything would be caught too
  s6  fusable (rdfs:label), seed has s6 already but only for an UNRELATED
      predicate (skos:altLabel, not rdfs:label) -> "onlyLabel" MUST still
      be added (check 1, predicate specificity: a translation that
      matched on subject alone -- "does s6 have ANY triple at all" --
      would wrongly see s6 as already covered and discard it; s1/s2 alone
      cannot catch this since s1's only seed triple already IS the
      predicate under test and s2 has no seed triple at all, so a
      subject-only match happens to coincide with the correct answer for
      both -- confirmed by deliberately loosening the pattern to `{s_can}
      ?anyp ?o` below and seeing s1/s2 alone stay green while adding s6
      turns it red, see meta.json)

A second, empty call is the trivial zero-solution baseline: nothing in,
nothing out.

Repair of 2026-10-30 -- what the two calls above could not see:

  * TRUTHINESS of the fusable guard. `not any(seed_graph.objects(s, p))`
    tests the truth of each object, and rdflib makes `Literal("")`,
    `"0"^^xsd:integer` and `"false"^^xsd:boolean` false: a target that
    holds only such a value counts as having NONE, so the source value is
    adopted (and the target ends with two values). Case `falsy` puts one of
    each in the target -- for rdfs:label and for two ontology properties of
    max_cardinality 1 (ex:count, ex:flag), next to a truthy control
    (ex:count "3"). `not bool(m{ ... })` counted solutions instead and
    failed this case; the translation now writes `not any(m{ ... ?o })`.
  * the ONTOLOGY: `ontology_props` was always empty, so no property other
    than rdfs:label/rdf:type was fusable, and no ontology property was
    allowed at all. Case `ontology` declares one property of
    max_cardinality 1 (fusable) and one of max_cardinality 2 (allowed, not
    fusable), plus rdf:type objects in and out of TARGET_ONTOLOGY_NAMESPACE.
  * NEIGHBOURS of the non-fusable guard sharing two of its three terms:
    same subject and object under another predicate (s7), same predicate
    and object on another subject (s8/s9) -- a predicate or subject widened
    to a variable would see them and skip an add that must happen.
  * a value added BY THE LOOP blocking a later one: s2 gets two source
    labels; the first adopted (through `+{ }` on the translated side) must
    make the guard discard the second.
  * the FILES the region writes besides the graph: `<stem>.selected.json`
    and `<stem>.discarded.json`, which the guard decides as much as the
    graph (a value discarded instead of selected). `demo` deletes its temp
    directory, so for every case the driver also calls
    `select_first_value` itself in a directory of its own per side, and
    compares the output graph (isomorphism) and both JSON files (equal
    lists, in order: both sides iterate the same parsed source graph).
  * the ValueError raised when ONTOLOGY_PATH is not set (same type and
    message on both sides).

The driver therefore runs both sides by hand (run_pair compares only what
`demo` returns); every earlier call is kept, as a `demo` call compared by
isomorphism.
"""
from __future__ import annotations

import json
import os
import tempfile
import traceback
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import _emit, _exec_ldpy, _exec_python, graphs_isomorphic

HERE = Path(__file__).resolve().parent

EX = "http://example.org/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
SKOS = "http://www.w3.org/2004/02/skos/core#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD = "http://www.w3.org/2001/XMLSchema#"
KG = "http://kg.org/ontology/"          # TARGET_ONTOLOGY_NAMESPACE

TARGET_NT = (
    f'<{EX}s1> <{RDFS}label> "existing" .\n'
    f'<{EX}s3> <{SKOS}altLabel> "seedAlt" .\n'
    f'<{EX}s4> <{SKOS}altLabel> "dup" .\n'
    f'<{EX}s6> <{SKOS}altLabel> "unrelated" .\n'
)

SOURCE_NT = (
    f'<{EX}s1> <{RDFS}label> "new" .\n'
    f'<{EX}s2> <{RDFS}label> "firstval" .\n'
    f'<{EX}s3> <{SKOS}altLabel> "sourceAlt" .\n'
    f'<{EX}s4> <{SKOS}altLabel> "dup" .\n'
    f'<{EX}s5> <{EX}customPred> "ignored" .\n'
    f'<{EX}s6> <{RDFS}label> "onlyLabel" .\n'
)

# Falsy literals already in the target, for fusable predicates.
FALSY_PROPS = [{"uri": f"{EX}count", "max_cardinality": 1},
               {"uri": f"{EX}flag", "max_cardinality": 1}]
FALSY_TARGET = (
    f'<{EX}f1> <{RDFS}label> "" .\n'
    f'<{EX}f2> <{EX}count> "0"^^<{XSD}integer> .\n'
    f'<{EX}f3> <{EX}flag> "false"^^<{XSD}boolean> .\n'
    f'<{EX}f4> <{EX}count> "3"^^<{XSD}integer> .\n'      # truthy control
    f'<{EX}f5> <{RDFS}label> ""@en .\n'
)
FALSY_SOURCE = (
    f'<{EX}f1> <{RDFS}label> "from source" .\n'
    f'<{EX}f2> <{EX}count> "7"^^<{XSD}integer> .\n'
    f'<{EX}f3> <{EX}flag> "true"^^<{XSD}boolean> .\n'
    f'<{EX}f4> <{EX}count> "8"^^<{XSD}integer> .\n'
    f'<{EX}f5> <{RDFS}label> "label"@en .\n'
)

# An ontology with one fusable and one non-fusable property, rdf:type in
# and out of the target namespace, the non-fusable guard's neighbours, and
# two source values for one fusable (subject, predicate).
ONTO_PROPS = [{"uri": f"{EX}single", "max_cardinality": 1},
              {"uri": f"{EX}multi", "max_cardinality": 2}]
ONTO_TARGET = (
    f'<{EX}o1> <{EX}single> <{EX}v1> .\n'
    f'<{EX}o2> <{EX}multi> <{EX}v1> .\n'
    f'<{EX}o3> <{RDF}type> <{KG}Person> .\n'
    f'<{EX}s7> <{RDFS}label> "alt7" .\n'              # same s, o; other p
    f'<{EX}s8> <{SKOS}altLabel> "shared" .\n'         # same p, o; other s
)
ONTO_SOURCE = (
    f'<{EX}o1> <{EX}single> <{EX}v2> .\n'             # fusable, blocked
    f'<{EX}o4> <{EX}single> <{EX}v3> .\n'             # fusable, adopted
    f'<{EX}o2> <{EX}multi> <{EX}v2> .\n'              # non-fusable, added
    f'<{EX}o2> <{EX}multi> <{EX}v1> .\n'              # non-fusable, present
    f'<{EX}o3> <{RDF}type> <{KG}Agent> .\n'           # fusable type, blocked
    f'<{EX}o5> <{RDF}type> <{KG}Agent> .\n'           # fusable type, adopted
    f'<{EX}o6> <{RDF}type> <http://xmlns.com/foaf/0.1/Person> .\n'  # skipped
    f'<{EX}s7> <{SKOS}altLabel> "alt7" .\n'
    f'<{EX}s9> <{SKOS}altLabel> "shared" .\n'
    f'<{EX}s2> <{RDFS}label> "first" .\n'             # two values, one
    f'<{EX}s2> <{RDFS}label> "second" .\n'            # (s, p): one survives
)

CASES = [
    ("baseline", SOURCE_NT, TARGET_NT, ()),
    ("empty", "", "", ()),                  # zero-solution baseline
    ("falsy", FALSY_SOURCE, FALSY_TARGET, FALSY_PROPS),
    ("ontology", ONTO_SOURCE, ONTO_TARGET, ONTO_PROPS),
]


def _direct(ns: dict, source_nt: str, target_nt: str, ontology_props):
    """Run the region itself; return (graph, selected, discarded)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "source.nt").write_text(source_nt)
        (tmp / "target.nt").write_text(target_nt)
        (tmp / "ontology.json").write_text(json.dumps(list(ontology_props)))
        os.environ["ONTOLOGY_PATH"] = str(tmp / "ontology.json")
        Data = ns["Data"]
        out = tmp / "output.nt"
        ns["select_first_value"]({"source": Data(path=tmp / "source.nt"),
                                  "target": Data(path=tmp / "target.nt")},
                                 {"output": Data(path=out)})
        graph = Graph().parse(out, format="nt")
        selected = json.loads((tmp / "output.selected.json").read_text())
        discarded = json.loads((tmp / "output.discarded.json").read_text())
        return graph, selected, discarded


def _unset_env(ns: dict):
    """The region's first guard: no ONTOLOGY_PATH -> ValueError."""
    saved = os.environ.pop("ONTOLOGY_PATH", None)
    try:
        ns["select_first_value"]({}, {})
        return "no exception"
    except Exception as e:                      # noqa: BLE001 - compared
        return (type(e).__name__, str(e))
    finally:
        if saved is not None:
            os.environ["ONTOLOGY_PATH"] = saved


verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:demo + direct call (graph, selected/discarded json)",
           "diffs": [], "error": None}

try:
    ns_o, _ = _exec_python(HERE / "original.py")
    ns_t, _ = _exec_ldpy(HERE / "translated.ldpy")
    for ns in (ns_o, ns_t):
        if not callable(ns.get("demo")) or not callable(ns.get("select_first_value")):
            raise RuntimeError("entry points not found in both modules")

    diffs: list[str] = []
    for name, src, tgt, props in CASES:
        go, gt = ns_o["demo"](src, tgt, props), ns_t["demo"](src, tgt, props)
        if not graphs_isomorphic(go, gt):
            diffs.append(f"{name}: demo graphs not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")
        (go, so, do), (gt, st, dt) = (_direct(ns_o, src, tgt, props),
                                      _direct(ns_t, src, tgt, props))
        if not graphs_isomorphic(go, gt):
            diffs.append(f"{name}: output graphs not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")
        if so != st:
            diffs.append(f"{name}: selected.json differs ({so!r} vs {st!r})")
        if do != dt:
            diffs.append(f"{name}: discarded.json differs ({do!r} vs {dt!r})")
    eo, et = _unset_env(ns_o), _unset_env(ns_t)
    if eo != et:
        diffs.append(f"unset ONTOLOGY_PATH: {eo!r} vs {et!r}")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
