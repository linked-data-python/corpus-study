"""Validation driver for Nanopublication__nanopub-py__tests_test_nanopub.py__TestIllTypedLiterals_test_sign_rejects_ill_typed_literal.

The region is a pytest test; both files end with an identical demo harness
that runs it and republishes the resulting assertion graph as
``demo_assertion``, so module-state comparison checks the actual RDF (the
test's own ``pytest.raises`` and ``source_uri is None`` assertions run on both
sides too).  ``tests.conftest`` is replaced by the local ``conftest_shim``
(see meta.json); the corpus checkout of commit 05022dc4bc is put on sys.path
here so the region's ``nanopub`` imports stay as upstream.
"""
import sys

sys.dont_write_bytecode = True

CORPUS = ("/home/lefrancois/Documents/recherche/semantic_web_micropython/github"
          "/corpus/repos/Nanopublication__nanopub-py")
if CORPUS not in sys.path:
    sys.path.insert(0, CORPUS)

from rdfeval.harness import run_pair  # noqa: E402

VERDICT = run_pair(__file__)
