"""Validation driver for synaptixs__ontomesh__src_alignment_generator.py___declared_local_names.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).

`_declared_local_names` takes an (output_dir, filename) pair and reads the
Turtle file itself -- there is no graph argument to hand a fixture= to, so
the fixture is a real file next to the pair, `fixture_ok.ttl`, and a second
call names a file that does not exist (the `os.path.isfile` guard's
zero-solution branch).

Two calls were added by the mutation audit (2026-10-31):
  - `fixture_shapes.ttl`, shaped like the files the repository really
    reads (output/ontology/tmf-sid-hierarchy.ttl): a URI subject with no
    rdf:type, so that narrowing `m{ ?s ?p ?o }` to `?s a ?o` no longer
    stays green, and an ontology IRI ending in "/";
  - `fixture_malformed.ttl`, which rdflib refuses (undeclared `owl:`), so
    the `except Exception` line scan is exercised too.
Equivalent mutant, not counted: forcing the `os.path.isfile` guard to
False gives the same `set()` on a missing file (parse raises, then open
raises OSError).
"""
from pathlib import Path
from rdfeval.harness import run_pair

_HERE = str(Path(__file__).resolve().parent)

VERDICT = run_pair(
    __file__,
    entry='_declared_local_names',
    calls=[
        ((_HERE, "fixture_ok.ttl"), {}),
        ((_HERE, "does-not-exist.ttl"), {}),
        ((_HERE, "fixture_shapes.ttl"), {}),
        ((_HERE, "fixture_malformed.ttl"), {}),
    ],
)
