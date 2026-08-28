"""Validation driver for landrs-toolkit__PySOSA__PySOSA_FeatureOfInterest.py__FeatureOfInterest___init__.

The region is a constructor extracted as a module-level function: it writes
three RDF terms onto ``self`` and returns nothing.  The driver passes a bare
stand-in object whose equality is the harness's own normalisation of its
attribute dict -- so the two Literals must match exactly and the two BNodes
must both be blank nodes (their identifiers necessarily differ between runs).
"""
from rdfeval.harness import normalise, run_pair


class Foi:
    """Bare stand-in for the FeatureOfInterest instance under construction."""

    def __eq__(self, other):
        return normalise(vars(self)) == normalise(vars(other))

    def __repr__(self):
        return "Foi(%r)" % (vars(self),)


def plain():
    return ((Foi(), "Air temperature sensor site", "A field station in Grenoble"), {})


def numeric_label():
    return ((Foi(), 42, None), {})


VERDICT = run_pair(__file__, entry="__init__", calls=[plain, numeric_label])
