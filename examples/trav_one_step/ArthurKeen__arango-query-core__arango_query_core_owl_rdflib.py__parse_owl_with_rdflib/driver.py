"""Validation driver for ArthurKeen__arango-query-core__arango_query_core_owl_rdflib.py__parse_owl_with_rdflib.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). The region's own signature takes the *raw Turtle text* as a
string (`turtle_text: str`, which is what the repository passes) and parses
it itself -- so each fixture's content is read as TEXT and passed as that
argument, not parsed into a Graph object beforehand (the default `fixture=`
behaviour of `run_pair` hands the entry point a pre-parsed Graph, which does
not fit this signature; hence the explicit `calls=`).

The three calls, and what each exercises:
  * `call_default` -- fixture.ttl: the main reads, several solutions per
    subject read, a property whose domain is not a class, the AnnotationProperty
    neighbour (see its header);
  * `call_branches` -- fixture_branches.ttl (added at repair): every branch
    and default fixture.ttl leaves undecided -- missing typeField/typeValue,
    default styles, the fallback half of each `or` chain with a non-default
    value, falsy values ("" and 0) that the `if x:` guards and the `or`
    chains must skip, two values for one read, non-string ranges, and a
    neighbour reaching owl:Class / owl:DatatypeProperty / owl:ObjectProperty
    by another predicate than rdf:type (see its header);
  * `call_empty` -- an empty ontology: zero solutions for every read, the
    bundle holds empty lists and dicts.

The returned MappingBundle is compared with `ordered=False` (the default
for a fixture run): its `conceptual_schema`/`physical_mapping` dicts hold
lists (`entities`, `relationships`) built by iterating subject sets no
store promises an order for.
"""
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
BRANCHES = HERE / "fixture_branches.ttl"


def call_default():
    return ((FIXTURE.read_text(),), {})


def call_branches():
    return ((BRANCHES.read_text(),), {})


def call_empty():
    return (("",), {})


VERDICT = run_pair(
    __file__,
    entry='parse_owl_with_rdflib',
    fixture="fixture.ttl",
    calls=[call_default, call_branches, call_empty],
)
