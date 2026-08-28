# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/api/trace.py
# region: StoredTraceMixin.set_trace_begin_dt (lines 384-392, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, RDF, RDFS, URIRef, XSD
from ..namespace import KTBS

def set_trace_begin_dt(self, val):
    """
    I return the begin datetime of the obsel.

    This will automatically update the trace_begin property.
    """
    with self.edit() as graph:
        graph.set((self.uri, KTBS.hasTraceBeginDT, Literal(val, datatype=XSD.dateTime)))
        graph.remove((self.uri, KTBS.hasTraceBegin, None))
