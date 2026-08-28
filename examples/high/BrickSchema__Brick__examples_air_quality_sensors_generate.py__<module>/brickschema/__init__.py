# Context shim (see meta.json): local stand-in for the `brickschema` package.
from . import namespaces
from .graph import Graph

__all__ = ["Graph", "namespaces"]
