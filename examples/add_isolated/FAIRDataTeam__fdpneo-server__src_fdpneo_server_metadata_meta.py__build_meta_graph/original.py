# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : src/fdpneo_server/metadata/meta.py
# region: build_meta_graph (lines 78-161, stratum add_isolated)
# licence of the source repository: see meta.json
from datetime import datetime
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF
# Context shim (see meta.json / context_shim.py): the real module paths are
# `fdpneo_server.metadata.graphs`, `fdpneo_server.metadata.states` and
# `fdpneo_server.shared.namespaces` -- not importable outside the package.
from context_shim import (
    DCT,
    DEFAULT_STATE,
    FDP_CREATE_OPERATION,
    FDP_MODIFY_OPERATION,
    FDP_METADATA_STATE,
    FDP_VALIDATED_AGAINST,
    MetaResult,
    MetadataState,
    Operation,
    OWL,
    PROV,
    _extract_creation,
    _extract_state,
    _extract_validated_against,
    _next_version,
    meta_graph_uri,
    record_graph_uri,
)

def build_meta_graph(
    *,
    record_iri: str | URIRef,
    prior: Graph,
    subject: str | None,
    now: datetime,
    initial_state: MetadataState = DEFAULT_STATE,
    validated_against: str | None = None,
    created: datetime | None = None,
    modified: datetime | None = None,
) -> MetaResult:
    """Build the next meta graph for ``record_iri``.

    Args:
        record_iri: The record being written. Used as the meta-graph subject.
        prior: The current meta graph for the record (empty graph on first write).
        subject: The current acting principal's URI; ``None`` if anonymous.
        now: The write timestamp; supplied by the caller for determinism.
        initial_state: Publication state for a *new* record (ADR-0010). LDP
            creates default to ``DRAFT``; the profile applier passes
            ``PUBLISHED`` for seeded records. On MODIFY the prior state is
            preserved and this argument is ignored — a content edit never
            changes publication state; only the transition API does.
        validated_against: The immutable profile *version* IRI the record was
            validated against at write time (ADR-0019 §3). Stamped as
            ``fdp-o:validatedAgainst`` when supplied; preserved from ``prior``
            when not (so a state transition or an unbound write keeps the
            provenance a content write recorded).
        created: **Privileged import only** (ADR-0016 §5) — an explicit
            ``dct:created`` from the source instead of ``now``/prior. Never set on
            the HTTP path; used by ``fdp backup import`` to carry source provenance.
        modified: **Privileged import only** — an explicit ``dct:modified`` from
            the source instead of ``now``.

    Returns:
        A :class:`MetaResult` whose ``graph`` is ready to replace whatever
        the triple store currently holds at ``<record>/meta``.
    """
    record_subject = record_graph_uri(record_iri)
    version = _next_version(prior, record_subject)
    created_at, prior_creator = _extract_creation(prior, record_subject)

    is_creation = created_at is None
    operation = Operation.CREATE if is_creation else Operation.MODIFY
    effective_created = created or created_at or now
    effective_creator = prior_creator if not is_creation else subject
    # State is server-managed lifecycle metadata: set it on create, preserve
    # it across content edits. Only the transition API (lifecycle.py) changes
    # an existing record's state.
    prior_state = _extract_state(prior, record_subject)
    effective_state = initial_state if is_creation else (prior_state or initial_state)

    graph = Graph()
    graph.add((record_subject, RDF.type, PROV.Entity))
    graph.add((record_subject, DCT.created, Literal(effective_created)))
    if effective_creator is not None:
        graph.add((record_subject, DCT.creator, URIRef(effective_creator)))
    graph.add((record_subject, DCT.modified, Literal(modified or now)))
    graph.add((record_subject, OWL.versionInfo, Literal(version)))
    graph.add((record_subject, FDP_METADATA_STATE, Literal(effective_state.value)))

    # ADR-0019 §3: the exact profile version validated at write time. A content
    # write supplies it; a bind-less write (or a state transition, which rebuilds
    # the meta graph without re-validating) preserves whatever the last content
    # write recorded, so the provenance never silently disappears.
    effective_binding = validated_against or _extract_validated_against(prior, record_subject)
    if effective_binding is not None:
        graph.add((record_subject, FDP_VALIDATED_AGAINST, URIRef(effective_binding)))

    activity = BNode()
    graph.add((record_subject, PROV.wasGeneratedBy, activity))
    graph.add((activity, RDF.type, PROV.Activity))
    graph.add(
        (
            activity,
            RDF.type,
            FDP_CREATE_OPERATION if is_creation else FDP_MODIFY_OPERATION,
        )
    )
    graph.add((activity, PROV.atTime, Literal(now)))
    if subject is not None:
        graph.add((activity, PROV.wasAssociatedWith, URIRef(subject)))

    return MetaResult(graph=graph, operation=operation, version=version, state=effective_state)
