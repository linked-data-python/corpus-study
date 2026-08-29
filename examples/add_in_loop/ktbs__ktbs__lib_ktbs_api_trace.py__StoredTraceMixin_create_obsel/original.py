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
    type_uri = coerce_to_uri(type, self.uri)
    graph.add((obs, RDF.type, type_uri))
    graph.add((obs, KTBS.hasTrace, self.uri))

    if isinstance(begin, Integral):
        graph.add((obs, KTBS.hasBegin, Literal(int(begin))))
    else: # will use KTBS.hasBeginDT
        begin_dt = begin
        if isinstance(begin, str):
            begin_dt = parse_date(begin_dt)
        elif isinstance(begin, datetime):
            if begin.tzinfo is None:
                begin = begin.replace(tzinfo=UTC)
        else:
            raise ValueError("Could not interpret begin %s", begin)
        graph.add((obs, KTBS.hasBeginDT, Literal(begin_dt)))

    if isinstance(end, Integral):
        graph.add((obs, KTBS.hasEnd, Literal(int(end))))
    else: # will use KTBS.hasEndDT
        end_dt = end
        if isinstance(end_dt, str):
            end_dt = parse_date(end_dt)
        elif isinstance(end, datetime):
            if end.tzinfo is None:
                end = end.replace(tzinfo=UTC)
        else:
            raise ValueError("Could not interpret end %s", end)
        graph.add((obs, KTBS.hasEndDT, Literal(end_dt)))

    if subject is not None:
        graph.add((obs, KTBS.hasSubject, subject))

    if attributes is not None:
        for key, val in attributes.items():
            k_uri = coerce_to_uri(key)
            if isinstance(val, Node):
                v_node = val
            else:
                v_node = Literal(val)
                # TODO LATER do something if val is a list
            graph.add((obs, k_uri, v_node))

    if relations is not None:
        for rtype, other in relations:
            rtype_uri = coerce_to_uri(rtype)
            other_uri = coerce_to_uri(other)
            graph.add((obs, rtype_uri, other_uri))

    if inverse_relations is not None:
        for other, rtype in inverse_relations:
            other_uri = coerce_to_uri(other)
            rtype_uri = coerce_to_uri(rtype)
            graph.add((other_uri, rtype_uri, obs))

    if source_obsels is not None:
        for src in source_obsels:
            s_uri = coerce_to_uri(src)
            graph.add((obs, KTBS.hasSourceObsel, s_uri))

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
