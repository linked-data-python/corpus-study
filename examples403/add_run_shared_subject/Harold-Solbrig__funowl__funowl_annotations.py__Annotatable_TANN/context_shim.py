# Context shim (see meta.json): minimal stand-ins for the funowl class
# hierarchy the region depends on (funowl/annotations.py,
# funowl/base/clone_subgraph.py), from
# Harold-Solbrig/funowl@69e1cbe2f615b4d64712ad9d5ab8f4d24988c006.
#
# clone_subgraph / USE_BNODE_COPIES are copied VERBATIM: self-contained,
# no further dependencies, and the region calls them for real.
#
# Annotatable / Annotation are reduced to the shape TANN reads
# (.annotations, .annotation_type, .property, .value): the real classes are
# dataclasses wired into funowl's functional-syntax writer (to_functional,
# annots, _add_annotations...), none of which TANN touches.
# AnnotationTerm is a minimal stand-in for the real AnnotationProperty /
# AnnotationValue / IRI / Literal wrappers behind .property and .value:
# TANN only ever calls their .to_rdf(g), so that is all this shim
# reproduces.
from typing import Dict

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import OWL
from rdflib.term import Node

USE_BNODE_COPIES = True


def clone_subgraph(g: Graph, subj: Node, seen: Dict[Node, Node] = None) -> Node:
    if not isinstance(subj, BNode):
        return subj
    if seen is None:
        seen = dict()
    elif subj in seen:
        return seen[subj]
    new_subj = BNode()
    seen[subj] = new_subj
    for p, o in g.predicate_objects(subj):
        g.add((new_subj, p, clone_subgraph(g, o, seen)))
    return new_subj


class AnnotationTerm:
    """Stand-in for AnnotationProperty / AnnotationValue: TANN only ever
    calls .to_rdf(g) on annotation.property and annotation.value."""

    def __init__(self, rdf_term):
        self._rdf_term = rdf_term

    def to_rdf(self, g: Graph):
        return self._rdf_term


class Annotatable:
    """Minimal stand-in for funowl's Annotatable (funowl/annotations.py):
    TANN only ever reads .annotations and .annotation_type off `self`.
    Real default: annotation_type = OWL.Axiom (class attribute)."""

    def __init__(self, annotations=None, annotation_type: URIRef = OWL.Axiom):
        self.annotations = annotations or []
        self.annotation_type = annotation_type


class Annotation(Annotatable):
    """Minimal stand-in for funowl's Annotation(Annotatable): real default
    annotation_type = OWL.Annotation (funowl/annotations.py:127)."""

    def __init__(self, property_rdf, value_rdf, annotations=None):
        super().__init__(annotations, annotation_type=OWL.Annotation)
        self.property = AnnotationTerm(property_rdf)
        self.value = AnnotationTerm(value_rdf)

    def TANN(self, g: Graph, subj):
        # Recursion guard, not a re-implementation: the real TANN recurses
        # into `annotation.TANN(g, t)` for annotations-on-annotations. The
        # driver (see driver.py) never nests annotations more than one
        # level deep, so every Annotation built as a *nested* annotation
        # has annotations=[] and this is never reached (TANN's own
        # `if self.annotations:` guard is false first). If it ever does
        # fire, that means a fixture nests annotations -- a fixture bug,
        # not something this shim should silently paper over by picking one
        # side's own TANN and running it for both (see meta.json for why
        # that would be unsound: original.py and translated.ldpy would
        # otherwise fight over which implementation is bound here).
        if self.annotations:
            raise NotImplementedError(
                "context_shim.Annotation.TANN: fixture nests annotations, "
                "which this shim does not support -- see meta.json"
            )
