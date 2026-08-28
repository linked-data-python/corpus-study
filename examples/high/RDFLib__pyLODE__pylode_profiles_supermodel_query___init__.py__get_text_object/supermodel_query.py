# Context shim (see meta.json): get_value, defined next to the region in
# pylode/profiles/supermodel/query/__init__.py at RDFLib/pyLODE@0d0471fb99
# (BSD 3-Clause, lines 67-79, verbatim).  The extraction kept only the
# region, so its module-local helper has to be re-supplied.
# Used IDENTICALLY by original.py and translated.ldpy.
from rdflib import Graph, Literal, URIRef


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
