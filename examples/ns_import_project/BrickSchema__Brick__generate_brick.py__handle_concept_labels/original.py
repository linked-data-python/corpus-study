# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: handle_concept_labels (lines 838-860, stratum ns_import_project)
# licence of the source repository: see meta.json
import logging
from itertools import chain
from rdflib import Graph, Literal, BNode, URIRef
from bricksrc.namespaces import (
    BRICK,
    BSH,
    REC,
    RDF,
    OWL,
    RDFS,
    TAG,
    SOSA,
    SKOS,
    QUDT,
    VCARD,
    SH,
    REF,
)
G = brickschema.Graph()
A = RDF.type

def handle_concept_labels(graph: Graph = G):
    """
    Adds labels to all concepts in the Brick namespace, unless they already have one.
    Brick concepts are all subclasses of Brick.Entity and subproperties of Brick.Relationship.
    If there are two or more labels for a concept, choose one and raise a Warning
    """
    concepts = chain(
        graph.transitive_subjects(RDFS.subClassOf, BRICK.Entity),
        graph.subjects(A, BRICK.Entity),
        graph.subjects(A, OWL.ObjectProperty),
        graph.subjects(A, OWL.DatatypeProperty),
    )
    for s in concepts:
        labels = list(graph.objects(s, RDFS.label))
        if len(labels) == 0:
            graph.add(
                (s, RDFS.label, Literal(s.split("#")[-1].replace("_", " "), lang="en"))
            )
        elif len(labels) > 1:
            logging.warning(f"Multiple labels for {s}: {labels}")
            # choose one and remove the others
            for to_remove in labels[1:]:
                graph.remove((s, RDFS.label, to_remove))
