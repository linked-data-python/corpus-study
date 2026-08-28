"""Validation driver — NOT RUNNABLE, the example is classified "excluded".

The region is an integration test of virtuoso-python's SQL-to-RDF mapping:
executing it needs (a) a live OpenLink Virtuoso server (the module opens a
SQLAlchemy engine on `sqla_connection` at import time and the test COMMITs
rows to it), (b) the patched pyodbc that virtuoso-python ships as a source
patch, and (c) nose, sqlalchemy and sqla_rdfbridge.  None of these can be
provided from inside the example directory, and no stub would preserve the
behaviour under test (the assertion is about what Virtuoso's RDF views
return).  Both modules therefore fail identically at load time, on the
undefined `Session` of the extracted module-level line.

The driver is kept in the shape it would have — entry + one fixture for the
test's `self` — so that it becomes runnable as soon as a Virtuoso instance
is available; the validate stage skips "excluded" examples.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_07_conditional_link",
                   calls=[lambda: ((None,), {})])
