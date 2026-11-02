# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/api/trace.py
# region: StoredTraceMixin.create_obsel (lines 415-531, stratum add_in_loop)
# licence of the source repository: see meta.json
from numbers import Integral, Real
from rdflib import Graph, Literal, RDF, RDFS, URIRef, XSD
from rdflib.term import Node
from datetime import datetime
from context_shim import parse_date, ParseError, UTC
from context_shim import cache_result, coerce_to_node, coerce_to_uri
from context_shim import ObselMixin, ObselProxy
from context_shim import KTBS
_NOW = datetime.now

def create_obsel(self, id=None, type=None, begin=None, end=None, 
                 subject=None, attributes=None, relations=None, 
                 inverse_relations=None, source_obsels=None, label=None,
                 no_return=False):
    """
    Creates a new obsel for the stored trace.

    :param id: see :ref:`ktbs-resource-creation`.
    :param type: Obsel type, defined by the Trace model.
    :param begin: Begin timestamp of the obsel, can be an int.
    :param end: End timestamp of the obsel, can be an int.
    :param subject: Subject of the obsel.
    :param attributes: explain.
    :param relations: explain.
    :param inverse_relations: explain.
    :param source_obsels: explain.
    :param label: explain.
    :param no_return: if True, None will be returned instead of the created obsek;
        this saves time and (in the case of a remote kTBS) network traffic

    :rtype: `ktbs.client.obsel.Obsel`
    """
    # redefining built-in 'id' #pylint: disable=W0622

    # We somehow duplicate Obsel.complete_new_graph and
    # Obsel.check_new_graph here, but this is required if we want to be
    # able to set _trust=True below.
    # Furthermore, the signature of this method makes it significantly
    # easier to produce a valid graph, so there is a benefit to this
    # duplication.

    if type is None:
        raise ValueError("type is mandatory for obsel creation")
    if begin is None:
        begin = _NOW(UTC)
    if end is None:
        end = begin
    if subject is None:
        subject = self.get_default_subject()
    elif not isinstance(subject, URIRef):
        subject = Literal(subject)

    trust = False # TODO SOON decide if we can trust anything
    # this would imply verifying that begin and end are mutually consistent
    # knowing that they could be heterogeneous (int/datetime)
    graph = Graph()
    obs = coerce_to_node(id, self.uri) # return BNode if id is None
    graph.add((obs, RDF.type, coerce_to_uri(type, self.uri)))
    graph.add((obs, KTBS.hasTrace, self.uri))

    if isinstance(begin, str):
        begin = parse_date(begin)
    if isinstance(begin, Integral):
        graph.add((obs, KTBS.hasBegin, Literal(int(begin))))
    elif isinstance(begin, datetime): # will use KTBS.hasBeginDT
        graph.add((obs, KTBS.hasBeginDT, Literal(begin)))
    else:
        raise ValueError("Could not interpret begin %s", begin)

    if isinstance(end, str):
        end = parse_date(end)
    if isinstance(end, Integral):
        graph.add((obs, KTBS.hasEnd, Literal(int(end))))
    elif isinstance(end, datetime): # will use KTBS.hasEndDT
        graph.add((obs, KTBS.hasEndDT, Literal(end)))
    else:
        raise ValueError("Could not interpret end %s", end)

    if subject is not None:
        graph.add((obs, KTBS.hasSubject, subject))

    for key, val in (attributes or {}).items():
        # TODO LATER do something if val is a list
        graph.add((obs, coerce_to_uri(key), val if isinstance(val, Node) else Literal(val)))

    for rtype, other in relations or ():
        graph.add((obs, coerce_to_uri(rtype), coerce_to_uri(other)))

    for other, rtype in inverse_relations or ():
        graph.add((coerce_to_uri(other), coerce_to_uri(rtype), obs))

    for src in source_obsels or ():
        graph.add((obs, KTBS.hasSourceObsel, coerce_to_uri(src)))

    if label is not None:
        graph.add((obs, RDFS.label, Literal(label)))

    uris = self.post_graph(graph, None, trust, obs, KTBS.Obsel)
    assert len(uris) == 1
    self.obsel_collection.force_state_refresh()
    if not no_return:
        ret = self.factory(uris[0], [KTBS.Obsel])
        assert isinstance(ret, ObselMixin)
        return ret


# Demo harness (identical on both sides, see meta.json): create_obsel builds
# its graph and hands it to self.post_graph(...) -- a side effect, not a
# returned value -- so the driver cannot compare the graph by simply calling
# create_obsel(self, ...) and looking at the result. This wraps the call
# with a self stand-in (context_shim._TraceStub) that captures exactly the
# graph it was posted, called with no_return=True to stay clear of
# self.factory()/ObselMixin (the REST resource-creation step, out of scope
# for a region under study for its graph construction).
def demo(**kwargs):
    from context_shim import _TraceStub
    self = _TraceStub()
    create_obsel(self, no_return=True, **kwargs)
    return self.captured_graph
