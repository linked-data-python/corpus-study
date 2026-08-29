# Context shim (see meta.json): stand-in for semantic-model/opcua/lib/utils.py
# from IndustryFusion/DigitalTwin@3b40088b8808, so the region executes
# outside its package (`lib.utils` is a real dotted project path that does
# not resolve for a single extracted file). Identical bindings for both
# representations.
#
# NGSILD: real Namespace IRI, transcribed verbatim (utils.py line 85).
#
# collection_to_list / calculate_array_dimensions: imported by the real
# entity.py (context line, kept verbatim in original.py/translated.ldpy)
# but never called by THIS region's own body (Entity.__init__ only stores
# NGSILD on self). Left as placeholders that raise if ever invoked, rather
# than transcribing their real bodies (utils.py lines 118-150+, which read
# a datagraph this region never builds) -- not reached by this region.
from rdflib import Namespace

NGSILD = Namespace('https://uri.etsi.org/ngsi-ld/')


def collection_to_list(*args, **kwargs):
    raise NotImplementedError("not reached by this region")


def calculate_array_dimensions(*args, **kwargs):
    raise NotImplementedError("not reached by this region")
