# Context shim (see meta.json): subset of tests/ingest_tester.py from
# tetherless-world/materialsmine@0be55da099, so the region executes outside
# the nanomine test-suite (which needs a Whyis app, a Flask client and a
# running agent). Identical bindings for both representations.
#
# `disabled` and `disable_test` are the source's, line for line: applied as
# the source applies it, the decorator replaces the test by a function that
# only prints, so the SPARQL of the region is dead code. `EXERCISE_BODY` is
# the one addition: when a driver sets it, the decorator still registers and
# announces the test as the source does but hands back the test itself, so
# that the body of the region is what the driver observes.
import unittest

from rdflib import Graph

disabled = []
EXERCISE_BODY = False


def disable_test(func):
    disabled.append(func.__name__)
    print(func.__name__, "is disabled and will not run")
    if EXERCISE_BODY:
        return func

    def disable(*args, **kwargs):
        print(func.__name__, "has been disabled")
    return disable


class _App:
    """`runner.app.db` of the source is the Whyis application's graph."""

    def __init__(self, db):
        self.db = db


class Runner(unittest.TestCase):
    """What the region asks of `runner`: `app.db`, `expected_data` and the
    `unittest.TestCase` assertions (the source's runner is a TestCase)."""

    def __init__(self, db=None, expected_data=None):
        super().__init__("run")
        self.app = _App(db if db is not None else Graph())
        self.expected_data = expected_data if expected_data is not None else {}

    def run(self, result=None):             # not a runnable test itself
        return None
