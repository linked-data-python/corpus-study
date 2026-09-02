"""Validation driver for INM-6__alpaca__alpaca_serialization_prov.py__AlpacaProvDocument__add_function_execution.

The region's single extracted operation (`rdf_ops: 1`) is the existence
read `PROV.wasAttributedTo not in self.graph.predicates(container_entity,
script_agent)` -- reached only through the `_is_membership` branch -- so the
oracle is the equality of the values both versions produce from the same
input graph (design record corpus/405), not isomorphism, even though
`meta.json` still says `"oracle": "isomorphism"` (the field predates this
region being routed through a `demo()` harness rather than a bare
call/fixture pair; see context_shim.py and the note in `original.py`).

`entry` is the `demo` harness both files carry identically (see meta.json):
it builds a fresh `AlpacaProvDocument(graph)`, runs the region on a
`subscript`-kind execution, and returns whether `_wasAttributedTo` was
called -- the one bit of information the read decides.

Four cases give the TRUE and FALSE branches of the read, plus neighbouring
data that must NOT match on either the object or the subject alone --
`self.graph.predicates(s, o)` filters by BOTH, so a fixture that only
varied the predicate's presence anywhere would pass a translation that
dropped the subject or the object from the pattern without catching it:

  1. exact triple present            -> not called (0): the TRUE branch
  2. absent entirely                 -> called (1): the FALSE branch
  3. same subject/predicate, WRONG object (agent)    -> called (1):
     proves the object is part of the match, not just the predicate
  4. same predicate/object, WRONG subject (container) -> called (1):
     proves the subject is part of the match too
"""
from rdflib import Namespace

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")
PROV_NS = "http://www.w3.org/ns/prov#"


def _case(graph_data, container, agent):
    def make():
        return (graph_data, container, agent), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        # 1. (c1, prov:wasAttributedTo, agent1) already present -> not called
        _case(
            f'@prefix prov: <{PROV_NS}> . @prefix ex: <http://example.org/> . '
            'ex:c1 prov:wasAttributedTo ex:agent1 .',
            EX.c1, EX.agent1,
        ),
        # 2. nothing at all for c2 -> called
        _case("", EX.c2, EX.agent1),
        # 3. c3 IS attributed, but to a DIFFERENT agent -> called
        #    (the object -- the agent -- is part of the pattern)
        _case(
            f'@prefix prov: <{PROV_NS}> . @prefix ex: <http://example.org/> . '
            'ex:c3 prov:wasAttributedTo ex:someone_else .',
            EX.c3, EX.agent1,
        ),
        # 4. agent1 IS the object of that predicate, but from a DIFFERENT
        #    subject -> called (the subject is part of the pattern too)
        _case(
            f'@prefix prov: <{PROV_NS}> . @prefix ex: <http://example.org/> . '
            'ex:someone_else_container prov:wasAttributedTo ex:agent1 .',
            EX.c4, EX.agent1,
        ),
    ],
)
