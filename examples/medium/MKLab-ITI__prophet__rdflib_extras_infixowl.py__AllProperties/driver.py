"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__AllProperties.

AllProperties is a *generator* yielding infixowl Property objects, so an
entry= comparison would compare two generator objects.  Both files therefore
carry an identical demo harness that consumes it over a small OWL vocabulary;
the driver compares the resulting module-level graph (which Property.__init__
mutates by asserting each property's base type) and the printed listing.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
