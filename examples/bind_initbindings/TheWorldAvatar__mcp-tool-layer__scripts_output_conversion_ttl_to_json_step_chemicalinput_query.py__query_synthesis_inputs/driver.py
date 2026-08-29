"""Validation driver for TheWorldAvatar__mcp-tool-layer__scripts_output_conversion_ttl_to_json_step_chemicalinput_query.py__query_synthesis_inputs.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`run_pair`'s own `fixture=` shortcut passes the parsed graph as the entry
point's *only* argument, but `query_synthesis_inputs(graph, synthesis_uri)`
takes two -- so `calls=` is built by hand here, using `fixture_graph()`
directly, once per synthesis URI under test:

  * Synthesis_1: several solutions, both UNION branches (a chemical reached
    directly via ontosyn:hasChemicalInput, and one reached through
    ontosyn:hasSynthesisStep / ontosyn:hasAddedChemicalInput), all three
    OPTIONAL clauses either bound or not, and one chemical with two
    alternative names (two solution rows folding into one grouped entry);
  * Synthesis_3: exists in the graph but links no chemical at all -- the
    zero-solution case;
  * Synthesis_2's own chemical, and the rdfs:label sitting directly on
    Synthesis_1, are the neighbourhood that must not leak into either call.

Each call re-parses the fixture into a fresh Graph, so the two sides never
share mutable state.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"
ONTOSYN = "https://www.theworldavatar.com/kg/OntoSyn/"


def _call(synthesis_uri: str):
    return lambda: ((fixture_graph(FIXTURE), synthesis_uri), {})


VERDICT = run_pair(
    __file__,
    entry="query_synthesis_inputs",
    calls=[
        _call(ONTOSYN + "Synthesis_1"),  # several solutions, both UNION arms
        _call(ONTOSYN + "Synthesis_3"),  # zero solutions
    ],
    # hand-built calls=, not the fixture= shortcut, so ordered does not
    # default to False on its own: no store promises a row order, and the
    # grouping dict's insertion order (and each chemical's alternative_names
    # list) both depend on it.
    ordered=False,
)
