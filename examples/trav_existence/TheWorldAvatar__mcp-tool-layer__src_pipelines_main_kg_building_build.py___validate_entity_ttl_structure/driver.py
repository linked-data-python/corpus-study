"""Validation driver for TheWorldAvatar__mcp-tool-layer__src_pipelines_main_kg_building_build.py___validate_entity_ttl_structure.

This region READS a graph, so the oracle is the equality of the values both
versions produce from the same input graph (design record corpus/405), not
isomorphism. It does not, however, take a `Graph` as its argument: the
region's own signature is `_validate_entity_ttl_structure(*, ttl_path,
entity_uri, entity_label, main_entity_policy)` -- it PARSES the graph itself
from a file path -- so the standard `fixture=` flow (which parses ONE
`fixture.ttl` and hands the entry point a `Graph` as its single positional
argument) does not fit either. Each call below instead writes its own
Turtle content to a fresh temp file and passes `ttl_path=` explicitly; the
entry point is the region itself (`_validate_entity_ttl_structure`, no
`demo()` needed -- its return value, `(bool, list[str])`, is already
directly comparable).

The region carries FOUR trav_existence-shaped reads (`rdf_ops` only tallies
two `graph_read` API calls plus two bare `in`/`not in` checks that are not
separately categorised -- same undercount as the sibling ScaDS/KGpipe
region in this batch; INSTRUCTIONS.md SS2's correspondence table is applied
to every site of the shape, not just the one the static count names):

  (1) `not any(g.triples((top_entity, None, None)))` -- does top_entity
      have ANY triple at all, gating "missing subject" (only reached when
      `require_entity_uri_subject` is set)
  (2) `(top_entity, RDF.type, URIRef(top_class_iri)) not in g` -- exact
      triple membership, gating "missing rdf:type" (elif of (1): only
      reached when (1) found the subject to exist)
  (3) `g.objects(top_entity, pred)` inside a list comprehension -- not
      itself existence-shaped (it is trav_one_step), but translated too per
      SS2's "always the most specific construction" rule, since it shares
      the region with (1), (2) and (4)
  (4) `(o, RDF.type, target_cls) in g` inside a second list comprehension --
      per-candidate existence test filtering the results of (3) to those of
      the required target class

Cases A-C isolate (1)/(2) (`required_links=[]`, varying whether `top_entity`
has any triple, and if so whether it has the required rdf:type). Cases D-F
isolate (3)/(4) (`require_entity_uri_subject=False`, so (1)/(2) never run)
and, within a single Turtle graph, give every combination (3)/(4) need to be
proven specific rather than merely present:

  p1  right predicate, right class            -> counted
  p2  right predicate, WRONG class             -> filtered out by (4):
      proves (4)'s pattern checks the CLASS, not just that p2 is typed
  "literalvalue"  right predicate, not a URIRef -> filtered by the
      surrounding (untranslated) `isinstance(o, URIRef)` check, proving the
      translation of (3) still yields it to that filter instead of
      swallowing it
  p3  WRONG predicate (`hasOtherPart`)          -> absent from (3)'s result
      entirely: proves (3)'s pattern checks the PREDICATE

Case F additionally uses a required-link spec with NO `target_class_iri`
(the `if target_class_iri:` branch guarding (4) is skipped), so `objs` stays
whatever (3) alone produced -- proving (3) is not accidentally coupled to
(4) running.
"""
import hashlib
import tempfile
from pathlib import Path

from rdfeval.harness import run_pair

EX = "http://example.org/"
TOP_CLASS = EX + "TopClass"
E1 = EX + "e1"


def _case(ttl_content, entity_uri, shell_validation):
    # `make()` runs once per side (original.py and translated.ldpy), and
    # `run_pair` compares kwargs across the two runs -- including
    # `ttl_path` itself. A fresh random name per call would make that
    # single kwarg differ for a reason that has nothing to do with the
    # translation, so the path is deterministic (content-hashed) and
    # shared: both sides read the SAME file, written once, never mutated.
    digest = hashlib.sha256(ttl_content.encode("utf-8")).hexdigest()[:16]
    path = Path(tempfile.gettempdir()) / f"ldpy-corpus-study-{digest}.ttl"

    def make():
        path.write_text(ttl_content, encoding="utf-8")
        return (), {
            "ttl_path": str(path),
            "entity_uri": entity_uri,
            "entity_label": "",
            "main_entity_policy": {"shell_validation": shell_validation},
        }
    return make


VERDICT = run_pair(
    __file__,
    entry="_validate_entity_ttl_structure",
    calls=[
        # A. top_entity has NO triple at all -> (1) fires: "missing subject"
        _case(
            f'<{EX}other> a <{TOP_CLASS}> .',
            E1,
            {"top_entity_class_iri": TOP_CLASS,
             "require_entity_uri_subject": True, "required_links": []},
        ),
        # B. top_entity has SOME triple, but not the required rdf:type ->
        #    (1) does not fire, (2) does: "missing rdf:type"
        _case(
            f'<{E1}> <http://www.w3.org/2000/01/rdf-schema#label> "E1" .',
            E1,
            {"top_entity_class_iri": TOP_CLASS,
             "require_entity_uri_subject": True, "required_links": []},
        ),
        # C. top_entity has the required rdf:type -> neither (1) nor (2)
        #    fires, no required_links -> valid
        _case(
            f'<{E1}> a <{TOP_CLASS}> .',
            E1,
            {"top_entity_class_iri": TOP_CLASS,
             "require_entity_uri_subject": True, "required_links": []},
        ),
        # D. required_links, min_count=2 but only p1 survives both filters
        #    (p2 wrong class, literal not a URIRef, p3 wrong predicate) ->
        #    found=1 < 2 -> "missing required link"
        _case(
            f'<{E1}> a <{TOP_CLASS}> .\n'
            f'<{E1}> <{EX}hasPart> <{EX}p1> .\n'
            f'<{EX}p1> a <{EX}PartClass> .\n'
            f'<{E1}> <{EX}hasPart> <{EX}p2> .\n'
            f'<{EX}p2> a <{EX}OtherClass> .\n'
            f'<{E1}> <{EX}hasPart> "literalvalue" .\n'
            f'<{E1}> <{EX}hasOtherPart> <{EX}p3> .\n',
            E1,
            {"top_entity_class_iri": TOP_CLASS,
             "require_entity_uri_subject": False,
             "required_links": [{"predicate_iri": EX + "hasPart",
                                 "target_class_iri": EX + "PartClass",
                                 "min_count": 2}]},
        ),
        # E. same graph as D, min_count=1 -> found=1 >= 1 -> valid
        _case(
            f'<{E1}> a <{TOP_CLASS}> .\n'
            f'<{E1}> <{EX}hasPart> <{EX}p1> .\n'
            f'<{EX}p1> a <{EX}PartClass> .\n'
            f'<{E1}> <{EX}hasPart> <{EX}p2> .\n'
            f'<{EX}p2> a <{EX}OtherClass> .\n'
            f'<{E1}> <{EX}hasPart> "literalvalue" .\n'
            f'<{E1}> <{EX}hasOtherPart> <{EX}p3> .\n',
            E1,
            {"top_entity_class_iri": TOP_CLASS,
             "require_entity_uri_subject": False,
             "required_links": [{"predicate_iri": EX + "hasPart",
                                 "target_class_iri": EX + "PartClass",
                                 "min_count": 1}]},
        ),
        # F. no target_class_iri -> (4) never runs, objs is (3) alone
        _case(
            f'<{E1}> a <{TOP_CLASS}> .\n'
            f'<{E1}> <{EX}hasRef> <{EX}r1> .\n'
            f'<{E1}> <{EX}hasRef> <{EX}r2> .\n',
            E1,
            {"top_entity_class_iri": TOP_CLASS,
             "require_entity_uri_subject": False,
             "required_links": [{"predicate_iri": EX + "hasRef",
                                 "target_class_iri": "",
                                 "min_count": 2}]},
        ),
    ],
)
