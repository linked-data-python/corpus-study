# Context shim (see meta.json): subset of yurtle_rdflib/core.py and
# yurtle_rdflib/namespaces.py from Congruentsys/yurtle-rdflib@8bbb378f5a18,
# so the region executes outside its package (`.core`/`.namespaces` relative
# imports do not resolve for a single extracted file). Identical bindings
# for both representations; original.py and translated.ldpy both import
# from this module instead of `.core`/`.namespaces`.
#
# YURTLE/PM/BEING/PROVENANCE: real Namespace objects, transcribed verbatim
# (core.py lines 50-53, namespaces.py PROVENANCE).
#
# YurtleDocument: dataclass fields transcribed verbatim from core.py
# (lines 58-77); methods this region never calls (get_property,
# get_properties) are omitted.
#
# YurtleParser: this region's body never calls it -- YurtleWriter.__init__
# only instantiates one (self.parser = YurtleParser()) and neither `write`
# nor `write_file` ever reads `self.parser`. Left as an empty stand-in
# rather than transcribing the real regex-driven parser (core.py lines
# 109+), which this region does not exercise.
#
# YurtleWriter: `write`, `_serialize_turtle` and `write_file` transcribed
# verbatim from core.py (lines 620-648) -- this region calls write_file
# directly, so its real behaviour (not a stub) is what makes the driver's
# "read back what got written" check meaningful.
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Namespace, URIRef

YURTLE = Namespace("https://yurtle.dev/schema/")
PM = Namespace("https://yurtle.dev/pm/")
BEING = Namespace("https://yurtle.dev/being/")
PROVENANCE = Namespace("https://yurtle.dev/provenance/")

__namespaces__ = {"yurtle": YURTLE, "pm": PM, "being": BEING, "provenance": PROVENANCE}


@dataclass
class YurtleDocument:
    """A parsed Yurtle document with both graph and content."""

    graph: Graph
    content: str
    frontmatter_raw: str
    frontmatter_type: str  # "turtle" | "yaml" | "none"
    source_path: Path | None = None
    subject_uri: URIRef | None = None


class YurtleParser:
    """Not exercised by this region; see module docstring above."""


class YurtleWriter:
    """Write Yurtle documents with Turtle frontmatter."""

    def __init__(self):
        self.parser = YurtleParser()

    def write(self, doc: YurtleDocument) -> str:
        """Serialize a YurtleDocument back to text."""
        if doc.frontmatter_type == "turtle" or doc.graph:
            frontmatter = self._serialize_turtle(doc.graph)
        elif doc.frontmatter_raw:
            frontmatter = doc.frontmatter_raw
        else:
            return doc.content
        return f"---\n{frontmatter}\n---\n{doc.content}"

    def _serialize_turtle(self, graph: Graph) -> str:
        """Serialize graph to Turtle format."""
        result = graph.serialize(format="turtle")
        if isinstance(result, bytes):
            return result.decode("utf-8")
        return result

    def write_file(self, doc: YurtleDocument, path: str | Path):
        """Write a YurtleDocument to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = self.write(doc)
        path.write_text(text, encoding="utf-8")


@dataclass
class FileState:
    """Tracks the state of a single file in the store (store.py lines 64-73)."""

    path: Path
    hash: str
    last_modified: float
    triple_count: int
    subject_uri: URIRef | None = None
    is_dirty: bool = False
    markdown_content: str = ""  # Preserved for round-trip
