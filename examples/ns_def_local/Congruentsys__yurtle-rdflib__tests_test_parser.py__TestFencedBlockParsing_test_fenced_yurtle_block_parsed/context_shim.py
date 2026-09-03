# Context shim (see meta.json): the real test does `from yurtle_rdflib
# import PM, YURTLE, YurtleParser` -- a package that is not installed in
# the pinned study venv (not on PyPI there; only its own dev venv has it).
# This shim transcribes VERBATIM the subset of
# Congruentsys/yurtle-rdflib@8bbb378f5a : src/yurtle_rdflib/core.py the
# region actually exercises (YAML frontmatter -> ``` turtle/yurtle fenced
# blocks, no frontmatter-Turtle branch, no ```yurtle-table branch): the
# `YurtleDocument` dataclass (trimmed to the fields the region can reach --
# `get_property`/`get_properties`/`to_dict` are never called here), the
# `YURTLE`/`PM`/`BEING` namespaces, and `YurtleParser.parse` down through
# `_parse_yaml`/`_yaml_to_triples`/`_add_triple` and
# `_parse_blocks`/`_looks_like_yaml`/`_build_prefix_header`.
#
# Left out (not transcribed, and confirmed unreached by this region's
# fixture -- `sample_doc_with_fenced_blocks` has YAML frontmatter, one
# ```turtle block and one ```yurtle block, no ```yurtle-table block):
# `_is_turtle`/`_parse_turtle` (the Turtle-frontmatter branch --
# `_is_turtle` itself IS needed, since `parse()` calls it to choose a
# branch, but it always returns False here so `_parse_turtle` is never
# entered and is omitted), `_parse_single_table_block` /
# `_resolve_prefixed_name` / `_infer_literal` (yurtle-table row parsing --
# `_parse_table_blocks` itself is kept, since `_parse_blocks` calls it
# unconditionally, but its own FENCED_TABLE_PATTERN never matches this
# fixture so it returns without needing those three), the RDFlib Parser
# plugin wrapper (`YurtleRDFlibParser`, registered under format="yurtle")
# and `YurtleWriter` -- the region calls `YurtleParser().parse(text)`
# directly, never `Graph().parse(..., format="yurtle")`.
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Standard Yurtle namespaces (core.py module level)
YURTLE = Namespace("https://yurtle.dev/schema/")
PM = Namespace("https://yurtle.dev/pm/")
BEING = Namespace("https://yurtle.dev/being/")
VOYAGE = Namespace("https://yurtle.dev/voyage/")
KNOWLEDGE = Namespace("https://yurtle.dev/knowledge/")


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
    """Parser for Yurtle documents (Markdown with Turtle frontmatter)."""

    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

    FENCED_BLOCK_PATTERN = re.compile(
        r"```(?:turtle|yurtle)\s*\r?\n(.*?)^```", re.DOTALL | re.MULTILINE
    )
    FENCED_TABLE_PATTERN = re.compile(r"```yurtle-table\s*\r?\n(.*?)^```", re.DOTALL | re.MULTILINE)

    _YAML_FIRST_LINE = re.compile(r"^[a-zA-Z_][\w-]*:\s*$")
    _MERGE_CONFLICT = re.compile(r"^<{7}\s|^={7}\s*$|^>{7}\s", re.MULTILINE)

    STANDARD_PREFIXES = {
        "yurtle": YURTLE,
        "pm": PM,
        "being": BEING,
        "voyage": VOYAGE,
        "knowledge": KNOWLEDGE,
        "rdf": RDF,
        "rdfs": RDFS,
        "xsd": XSD,
    }

    def __init__(self):
        import logging

        self.logger = logging.getLogger("yurtle-parser")

    def parse(self, text: str, source_path: Path | None = None) -> YurtleDocument:
        match = self.FRONTMATTER_PATTERN.match(text)

        if not match:
            graph = Graph()
            for prefix, ns in self.STANDARD_PREFIXES.items():
                graph.bind(prefix, ns)
            self._parse_blocks(text, graph)
            return YurtleDocument(
                graph=graph,
                content=text,
                frontmatter_raw="",
                frontmatter_type="none",
                source_path=source_path,
            )

        frontmatter_raw = match.group(1)
        content = match.group(2)

        if self._is_turtle(frontmatter_raw):
            raise NotImplementedError(
                "Turtle-frontmatter branch not reached by this region's fixture; "
                "not transcribed into the shim -- see context_shim.py header."
            )
        else:
            graph, subject_uri = self._parse_yaml(frontmatter_raw, source_path)
            frontmatter_type = "yaml"

        self._parse_blocks(content, graph)

        return YurtleDocument(
            graph=graph,
            content=content,
            frontmatter_raw=frontmatter_raw,
            frontmatter_type=frontmatter_type,
            source_path=source_path,
            subject_uri=subject_uri,
        )

    def _is_turtle(self, frontmatter: str) -> bool:
        stripped = frontmatter.strip()
        return (
            stripped.startswith("@prefix")
            or stripped.startswith("@base")
            or stripped.startswith("<")
            or stripped.startswith("PREFIX")
            or stripped.startswith("BASE")
        )

    def _parse_yaml(self, frontmatter: str, source_path: Path | None):
        graph = Graph()

        for prefix, ns in self.STANDARD_PREFIXES.items():
            graph.bind(prefix, ns)

        try:
            data = yaml.safe_load(frontmatter)
            if not data:
                return graph, None

            if source_path:
                subject_uri = self._uri_from_path(source_path)
            elif "id" in data:
                subject_uri = URIRef(f"urn:{data['id']}")
            else:
                subject_uri = URIRef("urn:unknown")

            self._yaml_to_triples(graph, subject_uri, data)

            return graph, subject_uri

        except Exception as e:
            self.logger.error(f"Failed to parse YAML frontmatter: {e}")
            return Graph(), None

    def _yaml_to_triples(self, graph: Graph, subject: URIRef, data: dict[str, Any]):
        key_mappings = {
            "type": RDF.type,
            "title": YURTLE.title,
            "status": PM.status,
            "priority": PM.priority,
            "assignee": PM.assignedTo,
            "assigned_to": PM.assignedTo,
            "created": YURTLE.created,
            "updated": YURTLE.updated,
            "tags": YURTLE.tag,
            "labels": YURTLE.label,
            "methodology": PM.methodology,
            "domain": BEING.domain,
            "name": YURTLE.name,
            "description": YURTLE.description,
        }

        for key, value in data.items():
            predicate = key_mappings.get(key, YURTLE[key])

            if isinstance(value, list):
                for item in value:
                    self._add_triple(graph, subject, predicate, item)
            else:
                self._add_triple(graph, subject, predicate, value)

    def _add_triple(self, graph: Graph, subject: URIRef, predicate: URIRef, value: Any):
        obj: Literal | URIRef
        if isinstance(value, bool):
            obj = Literal(value, datatype=XSD.boolean)
        elif isinstance(value, int):
            obj = Literal(value, datatype=XSD.integer)
        elif isinstance(value, float):
            obj = Literal(value, datatype=XSD.decimal)
        elif isinstance(value, str) and value.startswith("urn:"):
            obj = URIRef(value)
        elif isinstance(value, str) and value.startswith("http"):
            obj = URIRef(value)
        else:
            obj = Literal(str(value))

        graph.add((subject, predicate, obj))

    def _uri_from_path(self, path: Path) -> URIRef:
        return URIRef(f"urn:doc:{path.stem}")

    def _parse_blocks(self, content: str, graph: Graph) -> None:
        prefix_header = self._build_prefix_header(graph)

        for match in self.FENCED_BLOCK_PATTERN.finditer(content):
            block_content = match.group(1).strip()
            if not block_content:
                continue

            if self._looks_like_yaml(block_content):
                continue

            if self._MERGE_CONFLICT.search(block_content):
                continue

            try:
                enriched = prefix_header + block_content
                graph.parse(data=enriched, format="turtle")
            except Exception as e:
                self.logger.debug(f"Failed to parse fenced block at offset {match.start()}: {e}")

        self._parse_table_blocks(content, graph)

    def _parse_table_blocks(self, content: str, graph: Graph) -> None:
        for match in self.FENCED_TABLE_PATTERN.finditer(content):
            block_content = match.group(1).strip()
            if not block_content:
                continue
            raise NotImplementedError(
                "yurtle-table branch not reached by this region's fixture; "
                "not transcribed into the shim -- see context_shim.py header."
            )

    @staticmethod
    def _build_prefix_header(graph: Graph) -> str:
        lines = []
        for prefix, ns in sorted(graph.namespace_manager.namespaces()):
            if prefix:
                lines.append(f"@prefix {prefix}: <{ns}> .")
        return "\n".join(lines) + "\n\n" if lines else ""

    @classmethod
    def _looks_like_yaml(cls, content: str) -> bool:
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line == "---":
                return True
            if cls._YAML_FIRST_LINE.match(line):
                return True
            return False
        return False
