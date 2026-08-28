# Extracted from JonasHeinickeBio/biomedical-knowledge-lookup@00477184b3 : src/knowledge_lookup/umls/rdf.py
# region: concept_to_graph (lines 56-137, stratum add_in_loop)
# licence of the source repository: see meta.json
import json
from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import XSD
from ..models import ConceptType, UnifiedConcept
from ..services.rdf_converter import RDFNamespaces
UMLS = Namespace("https://uts.nlm.nih.gov/uts/umls/concept/")

def concept_to_graph(concept: UnifiedConcept, graph: Graph | None = None) -> Graph:
    """Convert a *concept* to an RDF :class:`Graph` and return it.

    Parameters
    ----------
    concept :
        The concept to serialise.
    graph :
        An optional existing graph to add triples to (creates a new one if
        ``None``).

    Returns
    -------
    The populated RDF graph.
    """
    g = graph if graph is not None else Graph()
    ns = RDFNamespaces()
    uri = _concept_uri(concept)

    # Bind namespaces for pretty Turtle
    for prefix, namespace in ns.get_namespace_bindings().items():
        g.bind(prefix, namespace)
    g.bind("umls", UMLS)

    # ── Type assertion ──────────────────────────────────────────────
    type_uri = _concept_type_to_rdf_class(concept.concept_type or ConceptType.UNKNOWN)
    g.add((uri, RDF.type, type_uri))

    # ── Labels & descriptions ───────────────────────────────────────
    g.add((uri, RDFS.label, Literal(concept.primary_label, lang="en")))
    labels_dict: dict[str, str] = (
        json.loads(concept.labels) if isinstance(concept.labels, str) else {}
    )
    for lang, label in labels_dict.items():
        g.add((uri, RDFS.label, Literal(label, lang=lang)))
    if concept.synonyms:
        for synonym in concept.synonyms:
            g.add((uri, ns.VOCAB["synonym"], Literal(synonym, lang="en")))
    if concept.definitions:
        for definition in concept.definitions:
            g.add((uri, ns.VOCAB["definition"], Literal(definition, lang="en")))

    # ── Identifiers (cross-references) ──────────────────────────────
    if concept.identifiers:
        for cid in concept.identifiers:
            _add_identifier(g, uri, cid, ns)

    # ── Semantic types & categories ─────────────────────────────────
    if concept.semantic_types:
        for st in concept.semantic_types:
            g.add((uri, ns.VOCAB["semanticType"], Literal(st)))
    if concept.categories:
        for cat in concept.categories:
            g.add((uri, ns.VOCAB["category"], Literal(cat)))

    # ── Relationships ───────────────────────────────────────────────
    if concept.parents:
        for parent_id in concept.parents:
            parent_uri = URIRef(UMLS[parent_id])
            g.add((uri, RDFS.subClassOf, parent_uri))
    if concept.children:
        for child_id in concept.children:
            child_uri = URIRef(UMLS[child_id])
            g.add((child_uri, RDFS.subClassOf, uri))
    if concept.related:
        for related_id in concept.related:
            related_uri = URIRef(UMLS[related_id])
            g.add((uri, ns.VOCAB["related"], related_uri))

    # ── Confidence / provenance ─────────────────────────────────────
    g.add(
        (
            uri,
            ns.VOCAB["confidenceScore"],
            Literal(concept.confidence_score or 0.0, datatype=XSD.float),
        )
    )
    if concept.sources:
        for src in concept.sources:
            g.add((uri, ns.VOCAB["source"], Literal(str(src))))

    return g
