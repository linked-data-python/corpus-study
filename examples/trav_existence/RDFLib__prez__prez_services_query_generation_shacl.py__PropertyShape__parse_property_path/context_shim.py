# Context shim (see meta.json): the PropertyPath class hierarchy (from
# prez/services/query_generation/shacl.py) and the SHEXT namespace (from
# prez/reference_data/prez_ns.py), RDFLib/prez@421ee0a9fe, so the region
# executes outside its package. Identical bindings for both representations.
#
# The real PropertyPath and its subclasses are pydantic BaseModel; pydantic
# is not installed in this environment, so they are reproduced here as plain
# dataclasses with the same fields -- structurally equivalent for the
# purpose of this region (building the tree and comparing it), and ordinary
# dataclass equality is exactly the oracle a driver needs.
import sys
from dataclasses import dataclass, field
from typing import List, Optional

from rdflib import Namespace

SHEXT = Namespace("http://example.com/shacl-extension#")


@dataclass(eq=True)
class PropertyPath:
    uri: Optional[object] = None


@dataclass(eq=True)
class Path(PropertyPath):
    value: object = None


@dataclass(eq=True)
class SequencePath(PropertyPath):
    value: List[object] = field(default_factory=list)


@dataclass(eq=True)
class InversePath(PropertyPath):
    value: object = None


@dataclass(eq=True)
class ZeroOrMorePath(PropertyPath):
    value: object = None
    operand: str = "*"


@dataclass(eq=True)
class OneOrMorePath(PropertyPath):
    value: object = None
    operand: str = "+"


@dataclass(eq=True)
class ZeroOrOnePath(PropertyPath):
    value: object = None
    operand: str = "?"


@dataclass(eq=True)
class AlternativePath(PropertyPath):
    value: List[object] = field(default_factory=list)


@dataclass(eq=True)
class BNodeDepth(PropertyPath):
    value: object = None


class PropertyShapeStub:
    """Stand-in for the `PropertyShape` instance `_parse_property_path` runs
    as a method of. `graph` is the fixture graph; `union_paths` records what
    `_add_path_to_shape` collects for the sh:union branch (the real method
    attaches the path to the shape being built -- here it just records the
    call). `_parse_property_path` re-enters whichever module (original.py or
    translated.ldpy) is currently calling it, so the region's own recursive
    `self._parse_property_path(...)` stays inside the implementation under
    test rather than some third copy.
    """

    def __init__(self, graph):
        self.graph = graph
        self.union_paths = []

    def _add_path_to_shape(self, item, union=False):
        self.union_paths.append((item, union))

    def _parse_property_path(self, pp):
        caller_globals = sys._getframe(1).f_globals
        return caller_globals["_parse_property_path"](self, pp)
