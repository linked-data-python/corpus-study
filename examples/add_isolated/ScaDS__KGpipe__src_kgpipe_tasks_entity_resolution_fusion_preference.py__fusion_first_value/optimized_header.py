# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe_tasks/entity_resolution/fusion/preference.py
# region: fusion_first_value (lines 180-212, stratum add_isolated)
# licence of the source repository: see meta.json
from logging import getLogger
from rdflib import URIRef, RDF
from kgpipe_context import (
    TARGET_ONTOLOGY_NAMESPACE, TrackRecord,
    canonicalize_entity_term, canonicalize_property_term,
    allowed_predicates, is_fusable, build_fixture_graphs,
)
logger = getLogger(__name__)

source_graph, seed_graph = build_fixture_graphs()
current_subjects = set([str(s) for s in seed_graph.subjects(unique=True)])
selected = []
discarded = []

for s, p, o in source_graph:
    # Canonicalize
    logger.debug(f"Canonicalizing {s}, {p}, {o}")
    s_can = canonicalize_entity_term(s)
    p_can = canonicalize_property_term(p)
    o_can = canonicalize_entity_term(o) if isinstance(o, URIRef) else o  # keep literals/bnodes as-is

    # Only work with properties that are in our ontology (after canonicalization)
    if not isinstance(p_can, URIRef) or str(p_can) not in allowed_predicates:
        logger.debug(f"Skipping {s}, {p}, {o} because it is not in the allowed predicates")
        continue

    if p_can == RDF.type and not o_can.startswith(TARGET_ONTOLOGY_NAMESPACE):
        continue

    if is_fusable(p_can):
        # Add exactly one value if none exists yet
        record = TrackRecord(subject=s_can,predicate=p_can,object=o,original_subject=s,original_predicate=p,original_object=o)
        if any(seed_graph.objects(s_can, p_can)):
            discarded.append(record)
            continue
        selected.append(record)
    # Non-fusable: copy if not already present (avoid dupes)
    elif (s_can, p_can, o_can) in seed_graph:
        continue
    seed_graph.add((s_can, p_can, o_can))
    # keep subjects set fresh for subsequent matches
    if isinstance(s_can, URIRef):
        current_subjects.add(str(s_can))
