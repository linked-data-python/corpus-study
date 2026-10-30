# Context shim (see meta.json): subset of seocho.ontology.core (PropertyType,
# a minimal Property/NodeDef/RelDef/Ontology) and of the module-private
# _safe_local() from seocho/ontology/serialization.py, from tteon/seocho@09f72a4569,
# so the region executes outside the package. Identical bindings for both
# representations.
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PropertyType(Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"
    DATE = "DATE"
    POINT = "POINT"
    LIST = "LIST"


@dataclass
class Property:
    property_type: PropertyType = PropertyType.STRING
    description: str = ""


@dataclass
class NodeDef:
    description: str = ""
    properties: Dict[str, Property] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    broader: List[str] = field(default_factory=list)
    same_as: Optional[str] = None


@dataclass
class RelDef:
    source: str = "Any"
    target: str = "Any"
    description: str = ""
    properties: Dict[str, Property] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    same_as: Optional[str] = None


class Ontology:
    def __init__(self, name, *, namespace="", description="",
                 nodes=None, relationships=None):
        self.name = name
        self.namespace = namespace
        self.description = description
        self.nodes: Dict[str, NodeDef] = dict(nodes or {})
        self.relationships: Dict[str, RelDef] = dict(relationships or {})


_TTL_LOCAL_RE = re.compile(r"[^A-Za-z0-9_]")


def _safe_local(uri, *, fallback: str = "Entity") -> str:
    """Take the last fragment / path segment of a URI as a Python-friendly name."""
    text = str(uri)
    if "#" in text:
        local = text.rsplit("#", 1)[-1]
    elif "/" in text:
        local = text.rstrip("/").rsplit("/", 1)[-1]
    else:
        local = text
    cleaned = _TTL_LOCAL_RE.sub("_", local).strip("_")
    if not cleaned:
        return fallback
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned
