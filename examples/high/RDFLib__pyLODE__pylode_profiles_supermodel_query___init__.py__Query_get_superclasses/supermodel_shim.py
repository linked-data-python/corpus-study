"""Context shim for this example, imported identically by both sides.

`pylode.profiles.supermodel.model` cannot be imported here: `pylode/__init__.py`
pulls in `dominate` (HTML rendering), which the region does not need.  The
region only uses `Class` as the return annotation of `list[Class]` (evaluated
at def time) and sorts the objects it gets back by `.name`, so the dataclass is
reduced to the two fields it touches; the iri-based `__eq__` is copied verbatim
from RDFLib/pyLODE@0d0471fb99 pylode/profiles/supermodel/model.py lines 167-185.
The full dataclass drags in Property, Note, Ontology and MediaObject, none of
which this region reads.
"""
from dataclasses import dataclass

from rdflib import URIRef


@dataclass
class Class:
    iri: URIRef
    name: str

    def __eq__(self, other):
        if not isinstance(other, Class):
            return False

        return self.iri == other.iri
