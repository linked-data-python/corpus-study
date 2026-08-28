# Context shim (see meta.json): hidden-graph/rdflib-starlight@b7973da2b5,
# tests/unit/test_result_patches.py -- the module-level helper the region
# calls but does not define, `_graph_with_one_fact`, together with the three
# constants it (and only it) needs, verbatim from the source module:
#
#   EX_A = "<http://example/a>"
#   EX_B = "<http://example/b>"
#   EX_C = "<http://example/c>"
#
#   def _graph_with_one_fact() -> Graph:
#       g = Graph()
#       g.parse(data=f"{EX_A} {EX_B} {EX_C} .", format="nt")
#       return g
#
# The region itself also defines EX_A/EX_B/EX_C at module scope (see
# meta.json's "context"); this shim keeps its own private copies so that the
# graph the fixture builds does not depend on how the region's own EX_A/EX_B
# /EX_C are spelled in translated.ldpy (there they become real URIRef terms,
# not pre-formatted N-Triples text -- see translation_notes).  `import
# starlight` (the module under test, which patches rdflib.query.Result at
# import time) is intentionally NOT reproduced: this region asserts
# `ask.askAnswer`, an attribute the patch does not touch -- only the sibling
# tests that iterate the Result exercise the bug being patched.
# Imported identically by original.py and translated.ldpy.
from rdflib import Graph

_EX_A = "<http://example/a>"
_EX_B = "<http://example/b>"
_EX_C = "<http://example/c>"


def _graph_with_one_fact() -> Graph:
    g = Graph()
    g.parse(data=f"{_EX_A} {_EX_B} {_EX_C} .", format="nt")
    return g
