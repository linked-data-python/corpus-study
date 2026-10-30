"""Validation driver for ScaDS__KGpipe__src_kgpipe_tasks_entity_resolution_fusion_preference.py__fusion_first_value.

Module-level region (kind: statement) with no entry point: `original.py`
and `translated.ldpy` are both executed top to bottom and their module
globals compared (entry=None). Two rdflib Graphs are in scope --
`source_graph` (read-only input, identical on both sides, compared only for
completeness) and `seed_graph` (what the region mutates) -- so the oracle is
RDF isomorphism on `seed_graph` (meta.oracle == "isomorphism"). The
`current_subjects` set (plain strings) is also compared via
rdfeval.harness's module-level value comparison, as an extra check that both
sides walk source_graph identically; `selected`/`discarded` (lists of
TrackRecord, a pydantic model) fall outside what the harness can compare
(only RDF terms/primitives/their containers) so they are not part of the
verdict, but keeping them mirrors the source faithfully.

Context shim kgpipe_context.py restores TrackRecord (verbatim), the real
TARGET_ONTOLOGY_NAMESPACE value from the sibling kgpipe/common/config.py at
the same commit, identity stand-ins for canonicalize_entity_term/
canonicalize_property_term (their real bodies need an external match file
this pair has no reason to fabricate -- entity matching is not what this
region does), concrete allowed_predicates/fusable_properties sets standing
in for ones the real code builds from an external ontology file, and
build_fixture_graphs() -- a factory (not a shared Graph import: see the
shim's own header) returning a fresh (source_graph, seed_graph) pair built
to exercise every branch: a fusable predicate with no existing seed value
(added), a fusable predicate whose subject already has a seed value
(discarded), an rdf:type triple whose object sits outside
TARGET_ONTOLOGY_NAMESPACE (skipped before the fusable check even runs), a
predicate absent from allowed_predicates entirely (skipped), a non-fusable
but allowed predicate not yet in the seed graph (copied), and the same
non-fusable predicate where the EXACT triple already sits in the seed graph
(skipped -- the dedupe check, zero triples added for that one).

Added by the repair of 2026-10-30 -- with identity canonicalisation,
s_can/p_can/o_can always equalled s/p/o, so `+{ {s} {p} {o} }` passed. The
driver now replaces, identically for both sides (one shared module, patched
before either side runs), the shim's stand-ins by:

  * canonicalize_entity_term / canonicalize_property_term with the REAL
    bodies of preference.py:147-175 (SINGLE_CANDIDATE_CHECK False), over a
    small MatchCluster (`_Matches`: get_cluster / has_match_to_namespace as
    in kgpipe/evaluation/cluster.py:95-117);
  * build_fixture_graphs wrapped to add, after the shim's nine triples,
    the cases where canonicalisation decides something:
      - a source subject remapped (src:A1 -> res:Frank: type and label
        added on the canonical subject), and one remapped onto a subject
        that already has a label in the seed (src:H2 -> res:Hugo): the
        fusable value is discarded on the CANONICAL subject;
      - a property remapped into the target namespace (other:score ->
        ex:hasScore) and one remapped into RDFS only (other:name ->
        rdfs:label, the workaround branch);
      - an rdf:type object remapped INTO the target namespace
        (other:Human -> ex:Human): kept only because o_can is used;
      - a non-fusable skos:altLabel with a URIRef object remapped
        (src:J -> res:JackAlias), and a remapped duplicate of a seed triple
        (src:Lea2 -> res:Lea, skos:altLabel "Dup2"@en) that the dedupe check
        must skip on the canonical triple;
      - the shim's nine triples keep their meaning: none of their terms is
        in a match cluster (clusters are symmetric in the real code, so a
        res:Dave pair would also remap the shim's res:Dave triples);
      - the non-fusable branch on canonical terms: a remapped subject
        (src:M1 -> res:Mia, skos:altLabel), and a remapped predicate and
        object together (other:knows -> ex:knows, an ontology property
        that is allowed but not fusable, added to allowed_predicates as
        the real set holds every ontology property; src:A1 -> res:Frank);
      - a blank-node subject (N-Triples sources have them), kept as is and
        not added to current_subjects;
      - falsy objects (0, "") on fusable predicates, which must be written.
  * selected / discarded (TrackRecord lists the harness cannot compare)
    are compared after run_pair by executing both sides again: their
    model_dump() rows, blank-node labels replaced by `_:b`, as multisets.
    run_pair's verdict line is silenced and re-emitted once (rdfeval.check
    reads the first one).
"""
import contextlib
import io
import json
import sys
from pathlib import Path

from rdflib import BNode, Literal, RDF, RDFS, SKOS, URIRef, XSD

from rdfeval.harness import _exec_ldpy, _exec_python, run_pair

import kgpipe_context

EX = "http://kg.org/ontology/"
RES = "http://kg.org/resource/"
SRC = "http://source.org/resource/"
OTHER = "http://other.org/"


class _Matches:
    """MatchCluster reduced to what the two canonicalisers call."""

    def __init__(self, pairs):
        self.uri_to_cluster = {}
        for a, b in pairs:
            cluster = {a, b}
            self.uri_to_cluster[a] = self.uri_to_cluster[b] = cluster

    def get_cluster(self, uri):
        return self.uri_to_cluster.get(uri)

    def has_match_to_namespace(self, uri, target_ns):
        cluster = self.get_cluster(uri)
        if cluster is None:
            return None
        for cluster_uri in cluster:
            if cluster_uri.startswith(target_ns):
                return cluster_uri
        return None


# Two-member clusters only, so each remapping is deterministic.
entity_matches = _Matches([
    (SRC + "A1", RES + "Frank"),
    (SRC + "H2", RES + "Hugo"),
    (OTHER + "Human", EX + "Human"),
    (SRC + "J", RES + "JackAlias"),
    (SRC + "Lea2", RES + "Lea"),
    (SRC + "M1", RES + "Mia"),
])
relation_matches = _Matches([
    (OTHER + "score", EX + "hasScore"),
    (OTHER + "name", str(RDFS.label)),
    (OTHER + "knows", EX + "knows"),
])
SINGLE_CANDIDATE_CHECK = False
TARGET_ONTOLOGY_NAMESPACE = kgpipe_context.TARGET_ONTOLOGY_NAMESPACE


def canonicalize_entity_term(term):
    """Map a URI from the target graph to the matching source URI, if any."""
    if isinstance(term, URIRef):
        t_str = str(term)
        cluster = entity_matches.get_cluster(t_str)
        if cluster:
            right_candidates = [c for c in cluster if not c == t_str]
            if len(right_candidates) > 2 and SINGLE_CANDIDATE_CHECK:
                raise ValueError(f"Multiple matches found for {t_str}")
            else:
                for m in right_candidates:
                    return URIRef(m)
                return term
        else:
            return term
    return term


def canonicalize_property_term(term):
    """Map a URI from the target graph to the matching source URI, if any."""
    if isinstance(term, URIRef):
        t_str = str(term)
        mapped = relation_matches.has_match_to_namespace(t_str, TARGET_ONTOLOGY_NAMESPACE)
        if mapped:
            return URIRef(mapped)
        else:
            mapped = relation_matches.has_match_to_namespace(t_str, str(RDFS))
            if mapped:
                return URIRef(mapped)
    return term


_shim_fixture = kgpipe_context.build_fixture_graphs


def build_fixture_graphs():
    source_graph, seed_graph = _shim_fixture()
    seed_graph.add((URIRef(RES + "Hugo"), RDFS.label, Literal("Existing Hugo", lang="en")))
    seed_graph.add((URIRef(RES + "Lea"), SKOS.altLabel, Literal("Dup2", lang="en")))
    add = source_graph.add
    add((URIRef(SRC + "A1"), RDF.type, URIRef(EX + "Person")))
    add((URIRef(SRC + "A1"), RDFS.label, Literal("Frank A1", lang="en")))
    add((URIRef(SRC + "H2"), RDFS.label, Literal("Hugo H2", lang="en")))
    add((URIRef(RES + "Gina"), URIRef(OTHER + "score"), Literal(0.5, datatype=XSD.double)))
    add((URIRef(RES + "Gina"), URIRef(OTHER + "name"), Literal("Gina", lang="en")))
    add((URIRef(RES + "Ivan"), RDF.type, URIRef(OTHER + "Human")))
    add((URIRef(RES + "Jack"), SKOS.altLabel, URIRef(SRC + "J")))
    add((URIRef(SRC + "Lea2"), SKOS.altLabel, Literal("Dup2", lang="en")))
    add((URIRef(SRC + "M1"), SKOS.altLabel, Literal("Mimi", lang="en")))
    add((URIRef(RES + "Nora"), URIRef(OTHER + "knows"), URIRef(SRC + "A1")))
    # a FIXED blank-node label: a fresh BNode() per side would hash
    # differently and change the order in which the store yields the
    # triples, hence the loop variables s/p/o the module leaves behind
    add((BNode("anon"), RDFS.label, Literal("anonymous", lang="en")))
    add((URIRef(RES + "Kim"), URIRef(EX + "hasScore"), Literal(0)))
    add((URIRef(RES + "Kim"), RDFS.label, Literal("")))
    return source_graph, seed_graph


# The real allowed set also holds every ontology property (preference.py:127);
# ex:knows stands for one without max_cardinality 1, i.e. not fusable.
kgpipe_context.allowed_predicates.add(EX + "knows")
kgpipe_context.canonicalize_entity_term = canonicalize_entity_term
kgpipe_context.canonicalize_property_term = canonicalize_property_term
kgpipe_context.build_fixture_graphs = build_fixture_graphs

_buf = io.StringIO()
with contextlib.redirect_stderr(_buf):
    VERDICT = run_pair(__file__, entry=None, calls=None)


def _records(ns):
    """selected / discarded as comparable rows, blank-node labels erased."""
    bnodes = {str(t) for triple in ns["source_graph"] for t in triple
              if isinstance(t, BNode)}

    def row(record):
        return tuple(sorted((k, "_:b" if v in bnodes else v)
                            for k, v in record.model_dump().items()))

    return {name: sorted(row(r) for r in ns[name])
            for name in ("selected", "discarded")}


if VERDICT.get("error") is None:
    here = Path(__file__).resolve().parent
    ns_o, _ = _exec_python(here / "original.py")
    ns_t, _ = _exec_ldpy(here / "translated.ldpy")
    ro, rt = _records(ns_o), _records(ns_t)
    extra = [f"{name} differs: {ro[name]!r} vs {rt[name]!r}"
             for name in ro if ro[name] != rt[name]]
    if extra:
        VERDICT["equivalent"] = False
        VERDICT["diffs"] = VERDICT.get("diffs", []) + extra

print("RDFEVAL-VERDICT " + json.dumps(VERDICT), file=sys.stderr)
