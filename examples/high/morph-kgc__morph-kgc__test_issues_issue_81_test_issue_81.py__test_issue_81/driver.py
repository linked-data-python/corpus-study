"""Validation driver for morph-kgc issue 81.

test_issue_81 takes no arguments: it materialises an R2RML/RML mapping with
morph_kgc and asserts the result is isomorphic to the recorded output.nq.
Both representations are exercised with the same (empty) fixture; the
assertions inside the function are the real check, and any divergence in RDF
behaviour would surface as an AssertionError reported by the harness.

Fixture data (mapping.ttl, output.nq, test/issues/issue_81/country_info.csv)
is copied verbatim from morph-kgc/morph-kgc@a2122e88bb; mapping.ttl names its
source relative to the repository root, hence the nested test/issues/issue_81
directory and the chdir below (identical for both representations, which are
executed in this same process).
"""
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

from rdfeval.harness import run_pair


def no_args():
    return ((), {})


VERDICT = run_pair(__file__, entry="test_issue_81", calls=[no_args])
