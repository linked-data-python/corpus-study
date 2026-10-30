"""Validation driver for kumagallium__asterism__ingest_src_asterism_rml_validate.py___fn_source_columns.

Establishes semantic equivalence of original.py and translated.ldpy.

The region returns a set of column names read from a function execution;
each call compares that set (and the input graph, which must stay intact).

- `fixture.ttl`, fe1: IRIs throughout, one direct reference, one nested
  function under the w3id predicate, legacy fnml input/inputValueMap and
  legacy rml:reference, an inputValueMap with an unrelated predicate.
- `fixture.ttl`, fe3: no input at all, the zero-solution case.
- `fixture_cases.ttl`, the shape the repository really parses (the caller,
  rml_validate.py:1034, passes an `fe` read with graph.objects off a
  blank-node object map); the driver picks each case's blank-node fe off
  its IRI root, the same way for both sides:
  case1  reference AND nested function on one inputValueMap: the
         `if found: continue` branch (an `if False:` mutant adds colHidden);
  case2  nested function under the LEGACY fnml:functionExecution, the second
         item of _FUNCTION_EXECUTION_PREDS;
  case3  both reference predicates on one map, two columns under one
         predicate (a `break` after the first is visible), a column twice;
  case4  a FALSY reference "" still counts as found and skips the function;
  case5  zero solutions with neighbours sharing two of three terms of each
         pattern (ex:reference, ex:inputValueMap, ex:input);
  case6  an input that is a literal.
- a Literal passed as `fe` (graph.objects can hand one over): no column.
"""
from pathlib import Path
from rdflib import Literal, URIRef
from rdfeval.harness import run_pair, fixture_graph

_HERE = Path(__file__).resolve().parent
_FE1 = URIRef("http://example.org/fe1")
_FE3 = URIRef("http://example.org/fe3")
_FE_PRED = URIRef("http://w3id.org/rml/functionExecution")


def _case(n):
    def call():
        g = fixture_graph(_HERE / "fixture_cases.ttl")
        fe = g.value(URIRef(f"http://example.org/case#case{n}"), _FE_PRED)
        return (g, fe), {}
    return call


VERDICT = run_pair(
    __file__,
    entry='_fn_source_columns',
    calls=[
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _FE1), {}),
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _FE3), {}),
        *[_case(n) for n in range(1, 7)],
        lambda: ((fixture_graph(_HERE / "fixture_cases.ttl"),
                  Literal("notAnFE")), {}),
    ],
)
