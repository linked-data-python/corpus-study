# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/api/trace.py
# region: StoredTraceMixin.set_trace_begin (lines 373-382, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, RDF, RDFS, URIRef, XSD
from ..namespace import KTBS

def set_trace_begin(self, val):
    """
    I set the begin timestamp of the obsel.

    This will automatically unset the trace_begin_dt property.
    """
    assert isinstance(val, int)
    with self.edit(_trust=True) as graph:
        graph.set((self.uri, KTBS.hasTraceBegin, Literal(val)))
        graph.remove((self.uri, KTBS.hasTraceBeginDT, None))
