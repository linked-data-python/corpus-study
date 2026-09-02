"""Validation driver for FAIRDataTeam__fdpneo-server__src_fdpneo_server_metadata_meta.py__build_meta_graph.

build_meta_graph returns a ``MetaResult`` dataclass (see context_shim.py)
whose ``graph`` field is a fresh rdflib Graph containing a fresh BNode (the
``activity``). run_pair's built-in entry=/calls= comparison would compare
that return value with plain ``==``: MetaResult is a frozen dataclass, so
``==`` compares ``graph`` field-wise too -- and two independently-built
Graphs holding an equivalent but not IDENTICAL BNode label are never ``==``
(rdflib does not give Graph content equality; that is exactly what
``rdflib.compare``/isomorphism is for). Comparing the raw return value would
therefore report a difference on every run regardless of translation -- a
false FAIL, following the precedent of driving both sides by hand set by
add_isolated/BBDFrancois.../driver.py and add_isolated/TheWorldAvatar/.../
driver.py for a region whose real state does not travel through run_pair's
default comparison.

So this driver unpacks MetaResult itself: ``.graph`` is compared by
isomorphism (the add_isolated/add_run_shared_subject oracle, design record
corpus/403), the other three fields (``operation``, ``version``, ``state``)
by plain equality.

Five cases exercise every conditional branch in the region:

  * A -- CREATE, subject given, no prior: dct:creator (from subject) AND
    prov:wasAssociatedWith are both emitted; fdp-o:validatedAgainst is not
    (no binding anywhere).
  * B -- CREATE, subject=None (anonymous): the two subject-derived triples
    (dct:creator, prov:wasAssociatedWith) are BOTH omitted.
  * C -- MODIFY (prior carries created/creator/version/state/validatedAgainst),
    subject=None: is_creation=False so effective_creator comes from the
    PRIOR graph regardless of `subject`, and effective_binding is preserved
    from prior since `validated_against` is not supplied here.
  * D -- MODIFY, validated_against explicitly overrides what prior recorded.
  * E -- CREATE with the privileged `created=`/`modified=` import overrides,
    and a non-default `initial_state`.
"""
from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

import context_shim as ctx

HERE = Path(__file__).resolve().parent

NOW = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
PRIOR_CREATED = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
IMPORT_CREATED = datetime(2020, 3, 4, tzinfo=timezone.utc)
IMPORT_MODIFIED = datetime(2020, 3, 5, tzinfo=timezone.utc)


def _prior_graph():
    from rdflib import Graph, Literal, URIRef
    g = Graph()
    subj = URIRef("https://example.org/records/r1")
    g.add((subj, ctx.DCT["created"], Literal(PRIOR_CREATED)))
    g.add((subj, ctx.DCT["creator"], URIRef("https://example.org/agents/alice")))
    g.add((subj, ctx.OWL["versionInfo"], Literal(3)))
    g.add((subj, ctx.FDP_METADATA_STATE, Literal("PUBLISHED")))
    g.add((subj, ctx.FDP_VALIDATED_AGAINST, URIRef("https://example.org/profiles/p1/v1")))
    return g


def _empty_graph():
    from rdflib import Graph
    return Graph()


CASES = [
    # (kwargs, description) -- kwargs rebuilt fresh per side (`prior` is a
    # mutable Graph; build_meta_graph never mutates it, but a fresh object
    # per call keeps the two runs from ever sharing state).
    (lambda: dict(record_iri="https://example.org/records/r1", prior=_empty_graph(),
                  subject="https://example.org/agents/bob", now=NOW),
     "A create+subject"),
    (lambda: dict(record_iri="https://example.org/records/r1", prior=_empty_graph(),
                  subject=None, now=NOW),
     "B create+anonymous"),
    (lambda: dict(record_iri="https://example.org/records/r1", prior=_prior_graph(),
                  subject=None, now=NOW),
     "C modify+anonymous, preserved creator/binding"),
    (lambda: dict(record_iri="https://example.org/records/r1", prior=_prior_graph(),
                  subject="https://example.org/agents/carol", now=NOW,
                  validated_against="https://example.org/profiles/p1/v2"),
     "D modify+override validated_against"),
    (lambda: dict(record_iri="https://example.org/records/r1", prior=_empty_graph(),
                  subject="https://example.org/agents/dave", now=NOW,
                  initial_state=ctx.MetadataState.PUBLISHED,
                  created=IMPORT_CREATED, modified=IMPORT_MODIFIED),
     "E create+privileged import overrides"),
]

verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:build_meta_graph (hand-rolled: MetaResult.graph "
                     "compared by isomorphism, other fields by equality)",
           "diffs": [], "error": None}

try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo = ns_o.get("build_meta_graph")
    ft = ns_t.get("build_meta_graph")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")

    diffs: list[str] = []
    for kwargs_factory, label in CASES:
        ro = fo(**kwargs_factory())
        rt = ft(**kwargs_factory())
        if not graphs_isomorphic(ro.graph, rt.graph):
            diffs.append(f"case[{label}]: graphs not isomorphic "
                         f"({len(ro.graph)} vs {len(rt.graph)} triples)")
        for field in ("operation", "version", "state"):
            vo, vt = getattr(ro, field), getattr(rt, field)
            if vo != vt:
                diffs.append(f"case[{label}].{field}: {vo!r} vs {vt!r}")

    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    verdict["calls"] = len(CASES)
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict
