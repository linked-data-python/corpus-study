# Context shim (see meta.json): in RDFLib/pyLODE@0d0471fb99
# pylode/profiles/supermodel/query/__init__.py, `g` is the Query graph
# (Query.ontdoc_inference is a method of a Graph subclass; the extracted
# statement reads `g`).  Here `g` is a plain rdflib Graph loaded from
# fixture.ttl, so the region executes outside the pylode package.
# Identical bindings for both representations.
from pathlib import Path

from rdflib import Graph

g = Graph()
g.parse(Path(__file__).resolve().parent / "fixture.ttl", format="turtle")
