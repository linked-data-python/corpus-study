"""Validation driver for aigora-de__rdf-construct__src_rdf_construct_lint_rules.py__check_property_no_type.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each fixture is parsed fresh for each side.

Three calls:

- ``fixture.ttl``: domain-only, range-only and domain-and-range subjects
  with no rdf:type (issues), a typed property, a builtin subject and a
  blank node (excluded);
- ``fixture_cases.ttl`` (repair 2026-10-30): each of the four members of
  ``property_types`` in EACH loop (a typo on any prefixed name, or the
  second ``m{ {subj} a ?t }`` given another predicate, changes the
  issues); a subject typed by a non-property class in each loop (types not
  empty, still an issue); a mixed type set; subjects with two domains, two
  ranges, two of each (graph.subjects yields one row per triple: the
  domain loop repeats the issue, the range loop dedups it); and neighbours
  a widened pattern would catch (a property type behind rdfs:seeAlso, a
  subject with neither domain nor range, a builtin and a blank node in the
  range loop, a property type as a domain VALUE);
- an empty graph: both loops have zero solutions, the result is [].
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent

VERDICT = run_pair(
    __file__,
    entry='check_property_no_type',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(HERE / "fixture.ttl"),), {}),
        lambda: ((fixture_graph(HERE / "fixture_cases.ttl"),), {}),
        lambda: ((Graph(),), {}),
    ],
    # results compared as multisets: no store promises an order.
)
