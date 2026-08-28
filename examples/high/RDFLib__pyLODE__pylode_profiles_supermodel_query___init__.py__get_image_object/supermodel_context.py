# Context shim (see meta.json): the region calls ``get_value`` — a helper
# defined a few lines above it in the same file — and builds an
# ``ImageObject``.  The pylode package cannot be imported in the evaluation
# venv (``pylode/__init__.py`` pulls in dominate, httpx and kurra, none of
# which are installed), so the three definitions the region needs are copied
# verbatim from RDFLib/pyLODE@0d0471fb99:
#   * get_value  -- pylode/profiles/supermodel/query/__init__.py, lines 68-80
#   * MediaObject, ImageObject -- pylode/profiles/supermodel/model.py, lines 12-36
# Used identically by original.py and translated.ldpy.
from abc import ABC
from dataclasses import dataclass

from rdflib import Graph, Literal, URIRef

DEFAULT_ORDER_VALUE = 999999


@dataclass
class MediaObject(ABC):
    name: str
    description: str
    encoding_format: str
    source: str
    # TODO: had role
    order: int | float

    def __post_init__(self):
        if self.name is None:
            self.name = ""
        if self.description is None:
            self.description = ""
        if self.order is None:
            self.order = DEFAULT_ORDER_VALUE


@dataclass
class ImageObject(MediaObject):
    url: str
    caption: str

    def __hash__(self) -> int:
        return hash(self.url)


def get_value(
    iri: URIRef, predicate: URIRef, graph: Graph
) -> str | int | float | bool | None:
    """Get the value as a Python data type."""
    value = graph.value(iri, predicate)
    if value is None:
        return None
    if isinstance(value, Literal):
        return value.value
    elif isinstance(value, URIRef):
        return str(value)
    else:
        raise TypeError(f"Unhandled type {type(value)}. Expected URIRef or Literal.")
