# Context shim (see meta.json): subset of arango_query_core/mapping.py
# (MappingSource, MappingBundle) from ArthurKeen/arango-query-core
# @f75a6be90c856bc7d9ef447748f253c9ba61a475, plus the two module-level
# helpers (_local_name, _xsd_to_simple) that live in the same file as the
# extracted region (arango_query_core/owl_rdflib.py) but outside its own
# line range (15-127), so the region executes outside the package.
# Identical bindings for both representations.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

JsonObj = dict[str, Any]


# arango_query_core/mapping.py, unmodified for the two classes this region
# constructs and returns.
@dataclass(frozen=True)
class MappingSource:
    kind: Literal["explicit", "heuristic", "schema_analyzer_export", "owl_turtle"]
    fingerprint: str | None = None
    generated_at_iso: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class MappingBundle:
    conceptual_schema: JsonObj
    physical_mapping: JsonObj
    metadata: JsonObj
    owl_turtle: str | None = None
    source: MappingSource | None = None


# arango_query_core/owl_rdflib.py lines 130-153, unmodified: the two
# helpers parse_owl_with_rdflib calls but does not define itself.
def _local_name(uri: Any) -> str:
    """Extract the local (fragment / last-path-segment) name from a URI."""
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[1]
    if "/" in s:
        return s.rsplit("/", 1)[1]
    return s


def _xsd_to_simple(uri: str) -> str:
    """Map an XSD datatype URI to a simple type string."""
    mapping = {
        "http://www.w3.org/2001/XMLSchema#string": "string",
        "http://www.w3.org/2001/XMLSchema#integer": "integer",
        "http://www.w3.org/2001/XMLSchema#int": "integer",
        "http://www.w3.org/2001/XMLSchema#decimal": "number",
        "http://www.w3.org/2001/XMLSchema#double": "number",
        "http://www.w3.org/2001/XMLSchema#float": "number",
        "http://www.w3.org/2001/XMLSchema#boolean": "boolean",
        "http://www.w3.org/2001/XMLSchema#date": "date",
        "http://www.w3.org/2001/XMLSchema#dateTime": "datetime",
    }
    return mapping.get(uri, "string")
