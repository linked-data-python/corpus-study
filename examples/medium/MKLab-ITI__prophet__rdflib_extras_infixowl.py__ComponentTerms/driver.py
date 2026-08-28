"""Validation driver: ComponentTerms is a generator, so module state is compared.

Both files end with an identical demo harness (see meta.json) that consumes the
generator over a small OWL graph covering its three branches -- a named
superclass plus an anonymous someValuesFrom restriction (recursive), an
owl:unionOf BooleanClass, and a leaf class -- and prints the identifiers found.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
