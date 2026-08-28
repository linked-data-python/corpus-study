"""Validation driver: test_190_1 is a pySHACL regression test.

The region takes no arguments and returns None; the observable behaviour is
the assertion it makes on the validation report (exactly two
sh:ValidationResult subjects).  Running it on both sides therefore checks
that the translated SH/RDF term islands select the same triples: were
sh:ValidationResult or rdf:type to resolve differently, result_list would be
empty and the assert would raise, which run_pair reports as an error.
"""
from rdfeval.harness import run_pair


def run_test():
    return ((), {})


VERDICT = run_pair(__file__, entry="test_190_1", calls=[run_test])
