"""Validation driver for test_inversetc0007.

The region takes no arguments and asserts internally (the YARRRML it gets
back from ``yatter.inverse_translation`` must match ``mapping.yml``), so
one empty fixture is enough; a divergence would surface as an
``AssertionError`` on one side only.

Note that ``translated.ldpy`` is byte-identical to ``original.py``: the
region contains no RDF term, literal or triple, only ``Graph()`` and
``Graph.parse``, so there is nothing for the notation to change.
"""
from rdfeval.harness import run_pair


def case_no_args():
    return ((), {})


VERDICT = run_pair(__file__, entry="test_inversetc0007", calls=[case_no_args])
