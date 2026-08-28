"""Validation driver for TestIllTypedLiterals.test_well_typed_literals_are_accepted.

Context (identical for both representations):

* the ``nanopub`` package is not installed in the evaluation venv, so the
  corpus checkout Nanopublication/nanopub-py@05022dc4bc is put on sys.path
  before either module is executed;
* ``_minimal_valid_nanopub``, a helper of tests/test_nanopub.py that the
  extractor did not carry over, lives in the local ``region_context.py``
  shim.

The region is a pytest test taking an unused ``self`` and returning nothing,
so both files end with an identical demo harness that runs it once and binds
the assertion graph it filled to ``demo_assertion``; module-state comparison
then checks that graph — the seven literals — by isomorphism.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parents[2] / "corpus" / "repos" / "Nanopublication__nanopub-py"
if str(CORPUS) not in sys.path:
    sys.path.insert(0, str(CORPUS))

from rdfeval.harness import run_pair  # noqa: E402

VERDICT = run_pair(__file__)
