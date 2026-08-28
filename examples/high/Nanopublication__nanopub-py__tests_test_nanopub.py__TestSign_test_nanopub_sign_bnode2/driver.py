"""Validation driver for TestSign.test_nanopub_sign_bnode2.

Context (identical for both representations):

* the ``nanopub`` package is not installed in the evaluation venv, so the
  corpus checkout Nanopublication/nanopub-py@05022dc4bc is put on sys.path
  before either module is executed;
* ``tests.conftest`` is replaced by the local ``conftest_context.py`` shim
  (see its header): the RSA key pair the profile needs was copied from
  Nanopublication/nanopub-testsuite@main instead of being downloaded.

The region takes only ``self``, which it never uses, and returns nothing:
what it checks is that signing the two-blank-node assertion yields the
trusty artifact code ``RA-1eE8scf…``.  That code is a hash of the signed
nanopub, so the in-test assertion is itself a strong graph-equality check
between the two representations — it fails as soon as the blank nodes or
the literals differ.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parents[2] / "corpus" / "repos" / "Nanopublication__nanopub-py"
if str(CORPUS) not in sys.path:
    sys.path.insert(0, str(CORPUS))

from rdfeval.harness import run_pair  # noqa: E402


def no_args():
    return ((None,), {})


VERDICT = run_pair(__file__, entry="test_nanopub_sign_bnode2", calls=[no_args])
