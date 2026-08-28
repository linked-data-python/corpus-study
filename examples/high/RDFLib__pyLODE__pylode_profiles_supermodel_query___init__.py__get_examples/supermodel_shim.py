"""Context shim for this example, imported identically by both sides.

`pylode.profiles.supermodel.query` cannot be imported here: `pylode/__init__.py`
pulls in `dominate` (HTML rendering), which the region does not need.  This
module therefore carries the pieces the region calls, copied verbatim from
RDFLib/pyLODE@0d0471fb99:

  * `MediaObject`, `ImageObject`, `TextObject` and `DEFAULT_ORDER_VALUE`
        pylode/profiles/supermodel/model.py, lines 9-42
  * `get_value`, `get_text_object`, `get_image_object`
        pylode/profiles/supermodel/query/__init__.py, lines 68-135
        (module-level siblings of the region, which references them by name)
"""
from abc import ABC
from dataclasses import dataclass
from textwrap import dedent

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, SDO, SH

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


@dataclass
class TextObject(MediaObject):
    text: str


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


def get_text_object(iri: URIRef, graph: Graph) -> TextObject:
    name = get_value(iri, SDO.name, graph)
    description = get_value(iri, SDO.description, graph)
    encoding_format = get_value(iri, SDO.encodingFormat, graph)
    source = get_value(iri, DCTERMS.source, graph)
    order = get_value(iri, SH.order, graph)
    text = get_value(iri, SDO.text, graph)

    if not text:
        raise ValueError("Text examples must have a value encoded using sdo:text.")

    return TextObject(
        name, description, encoding_format, source, order, dedent(text).strip()
    )


def get_image_object(iri: URIRef, graph: Graph) -> ImageObject:
    name = get_value(iri, SDO.name, graph)
    description = get_value(iri, SDO.description, graph)
    encoding_format = get_value(iri, SDO.encodingFormat, graph)
    source = get_value(iri, DCTERMS.source, graph)
    order = get_value(iri, SH.order, graph)
    url = get_value(iri, SDO.contentUrl, graph)
    caption = get_value(iri, SDO.caption, graph)

    return ImageObject(
        name,
        description,
        encoding_format,
        source,
        order,
        url,
        caption,
    )
