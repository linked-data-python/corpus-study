"""Validation driver for pySHACL's test_190_2.

The region takes no argument and returns nothing: it parses the two Turtle
constants defined above it, runs pyshacl's ``validate`` over them, walks the
validation report for ``sh:ValidationResult`` subjects and asserts that the
data conforms.  Running it on both sides therefore exercises the whole
pipeline; the ldpy side differs only in how ``RDF.type`` and
``SH.ValidationResult`` are written.
"""
from rdfeval.harness import run_pair


def no_args():
    return ((), {})


VERDICT = run_pair(__file__, entry="test_190_2", calls=[no_args])
