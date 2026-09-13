# Context shim (see meta.json): subset of oscin/reader.py from
# danilipp17/thesis_code@c2772e3555, so the region executes outside the
# package. Identical bindings for both representations.
from typing import Optional

from rdflib import Graph, Literal, URIRef


class ReaderSelf:
    """Stand-in for the OntologyReader instance: only what the region calls."""

    def __init__(self, g: Graph):
        self.g = g

    def _int_value(self, subject: URIRef, predicate: URIRef) -> Optional[int]:
        for obj in self.g.objects(subject, predicate):
            if isinstance(obj, Literal):
                try:
                    return int(obj.toPython())
                except (ValueError, TypeError):
                    return None
        return None

    def _str_value(self, subject: URIRef, predicate: URIRef) -> Optional[str]:
        for obj in self.g.objects(subject, predicate):
            return str(obj)
        return None
