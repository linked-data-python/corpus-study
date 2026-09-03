# Context shim (see meta.json): stand-in for semantic-model/shacl2flink/lib/utils.py
# from IndustryFusion/DigitalTwin@3b40088b880811f61df63ba926f78256098ce695, so
# `from lib.utils import get_full_path_of_shacl_property, NGSILD,
# UnsupportedShape` in original.py resolves outside the shacl2flink package.
# Identical bindings for both representations.
#
# NGSILD: real Namespace IRI, transcribed verbatim (utils.py line 30).
#
# UnsupportedShape: real exception class, transcribed verbatim (utils.py
# lines 42-49) -- cheap to reproduce exactly, and the region's own `try:
# ... except Exception:` around `Collection(g, path)` does not care which
# exception type it is.
#
# get_full_path_of_shacl_property: imported by the real
# shacl_properties_to_sql.py (context line, kept verbatim in
# original.py/translated.ldpy) but never called by THIS region's own body
# (inverse_relationship_predicate only reads `steps[0]`/`steps[1]` via
# Collection and g.value). Left as a placeholder that raises if ever
# invoked, rather than transcribing its real body (utils.py lines 194-203,
# which walks `shape_parent` -- a helper this region never reaches) -- not
# reached by this region.
from rdflib import Namespace

NGSILD = Namespace('https://uri.etsi.org/ngsi-ld/')


class UnsupportedShape(Exception):
    """
    A shape the compiler cannot translate.

    Raised at build time rather than skipped. A constraint that is silently not
    compiled is worse than a build failure: validation then reports conformant
    for something it never checked, and nothing anywhere says so.
    """


def get_full_path_of_shacl_property(*args, **kwargs):
    raise NotImplementedError("not reached by this region")
