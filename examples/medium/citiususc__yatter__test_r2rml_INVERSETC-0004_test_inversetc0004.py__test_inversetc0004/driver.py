"""Validation driver for yatter INVERSETC-0004.

The region is a pytest test taking no arguments: it parses mapping.ttl, runs
yatter.inverse_translation() to recover a YARRRML mapping, and asserts it
matches the recorded mapping.yml.  Both representations are run with the same
empty fixture; the assertions inside the function are the real check, so any
divergence in RDF behaviour would surface as an AssertionError.

Context shims (identical for both representations, which are executed in this
same process):
  * yatter is not installed in the evaluation environment; its source tree is
    put on sys.path from the corpus checkout (citiususc/yatter@0b40dff623);
  * coloredlogs.py is a no-op stand-in for the log colouriser imported by
    yatter.constants;
  * deepdiff.py is a minimal order-insensitive comparison stand-in for
    DeepDiff(..., ignore_order=True) -- see its header;
  * mapping.yml / mapping.ttl are copied verbatim from the test case directory
    (the region reads them next to __file__).
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)

YATTER_SRC = (HERE.parents[2] / "corpus" / "repos" / "citiususc__yatter" / "src")
if str(YATTER_SRC) not in sys.path:
    sys.path.insert(0, str(YATTER_SRC))

from rdfeval.harness import run_pair


def no_args():
    return ((), {})


VERDICT = run_pair(__file__, entry="test_inversetc0004", calls=[no_args])
