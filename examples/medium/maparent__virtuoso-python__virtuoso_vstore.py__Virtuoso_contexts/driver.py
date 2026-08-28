"""Validation driver for maparent__virtuoso-python__virtuoso_vstore.py__Virtuoso_contexts.

The region is a generator method of the Virtuoso store; it is exercised
against the off-line stand-in store of vstore_ctx.py by an identical demo
harness at the end of both sides, and compared on stdout (the graph
identifiers it yields and the query text it sent to the cursor).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # vstore_ctx shim

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
