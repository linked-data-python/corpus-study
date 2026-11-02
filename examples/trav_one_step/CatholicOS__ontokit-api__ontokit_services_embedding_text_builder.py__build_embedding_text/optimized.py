# Extracted from CatholicOS/ontokit-api@23680a4d04 : ontokit/services/embedding_text_builder.py
# region: build_embedding_text (lines 8-53, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib import Literal as RDFLiteral
from rdflib.namespace import OWL, RDFS, SKOS
from embedding_text_context import _local_name

def build_embedding_text(graph: Graph, entity_uri: URIRef, entity_type: str) -> str:
    """Build a text representation of an entity for embedding.

    Format: "{type}: {label}. {comment}. Parents: {parents}. Also known as: {alt_labels}"
    """
    def literals(subject, predicate):
        return [str(o) for o in graph.objects(subject, predicate) if isinstance(o, RDFLiteral)]

    # Primary label
    labels = literals(entity_uri, RDFS.label)
    primary_label = labels[0] if labels else _local_name(str(entity_uri))
    parts = [f"{entity_type}: {primary_label}"]

    # Comments/definitions
    desc = literals(entity_uri, RDFS.comment) or literals(entity_uri, SKOS.definition)
    if desc:
        parts.append(desc[0])

    # Parents (use subPropertyOf for properties, subClassOf for classes)
    parent_pred = RDFS.subPropertyOf if entity_type == "property" else RDFS.subClassOf
    parent_labels = [
        next(iter(literals(p, RDFS.label)), _local_name(str(p)))
        for p in graph.objects(entity_uri, parent_pred)
        if isinstance(p, URIRef) and p != OWL.Thing
    ]
    if parent_labels:
        parts.append(f"Parents: {', '.join(parent_labels)}")

    # Alternative labels
    all_alt = literals(entity_uri, SKOS.altLabel) + [
        lbl for lbl in labels[1:] if lbl != primary_label
    ]
    if all_alt:
        parts.append(f"Also known as: {', '.join(all_alt)}")

    return ". ".join(parts)
