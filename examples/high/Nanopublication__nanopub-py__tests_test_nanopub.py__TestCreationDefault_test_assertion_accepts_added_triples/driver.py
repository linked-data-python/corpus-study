"""Validation driver for Nanopublication__nanopub-py__tests_test_nanopub.py__TestCreationDefault_test_assertion_accepts_added_triples.

The region is a pytest test; both files end with an identical demo harness
that runs it and republishes the resulting assertion graph as
``demo_assertion``, so module-state comparison checks the actual RDF.
The region's ``nanopub`` imports are left as upstream: the corpus checkout of
commit 05022dc4bc is put on sys.path here instead.
"""
import sys

sys.dont_write_bytecode = True

CORPUS = ("/home/lefrancois/Documents/recherche/semantic_web_micropython/github"
          "/corpus/repos/Nanopublication__nanopub-py")
if CORPUS not in sys.path:
    sys.path.insert(0, CORPUS)

from rdfeval.harness import run_pair  # noqa: E402

VERDICT = run_pair(__file__)
