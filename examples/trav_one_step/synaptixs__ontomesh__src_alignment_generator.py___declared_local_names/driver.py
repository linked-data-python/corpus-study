"""Validation driver for synaptixs__ontomesh__src_alignment_generator.py___declared_local_names.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).

`_declared_local_names` takes an (output_dir, filename) pair and reads the
Turtle file itself -- there is no graph argument to hand a fixture= to, so
the fixture is a real file next to the pair, `fixture_ok.ttl`, and a second
call names a file that does not exist (the `os.path.isfile` guard's
zero-solution branch).
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
    ],
)
