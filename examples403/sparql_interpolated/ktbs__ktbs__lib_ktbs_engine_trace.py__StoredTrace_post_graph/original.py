# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/engine/trace.py
# region: StoredTrace.post_graph (lines 318-358, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, XSD
from rdfrest.exceptions import InvalidDataError
from rdfrest.util import bounded_description, cache_result, random_token, replace_node_sparse, \
    Diagnosis
from .resource import KtbsPostableMixin, METADATA
from ..namespace import KTBS, KTBS_NS_URI
_SELECT_CANDIDATE_OBSELS = prepareQuery("""
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX : <%s#>
    SELECT ?obs
           (IF(bound(?b), ?b, "INF"^^xsd:float) as ?begin)
           (IF(bound(?e), ?e, ?begin) as ?end)
           $trace # selected solely to please Virtuoso
    WHERE {
        ?obs :hasTrace ?trace
        OPTIONAL { ?obs :hasBegin ?b }
        OPTIONAL { ?obs :hasEnd   ?e }
    }
    ORDER BY ?begin ?end
""" % KTBS_NS_URI)
YES = Literal('yes')

def post_graph(self, graph, parameters=None,
               _trust=False, _created=None, _rdf_type=None):
    """I override :meth:`rdfrest.util.GraphPostableMixin.post_graph`.

    I allow for multiple obsels to be posted at the same time.
    """
    base = self.get_base()
    post_single_obsel = super(StoredTrace, self).post_graph
    binding = { "trace": self.uri }
    ret = []
    candidates = [ i[0] for i in graph.query(_SELECT_CANDIDATE_OBSELS,
                                             initBindings=binding) ]
    bnode_candidates = { i for i in candidates
                           if isinstance(i, BNode) }
    with self.obsel_collection.edit({"add_obsels_only":1}, _trust=True):
        for candidate in candidates:
            if isinstance(candidate, BNode):
                bnode_candidates.remove(candidate)
            obs_graph = bounded_description(candidate, graph, prune=bnode_candidates)
            for other in bnode_candidates:
                obs_graph.remove((candidate, None, other))
                obs_graph.remove((other, None, candidate))

            ret1 = post_single_obsel(obs_graph, parameters, _trust, candidate,
                                     KTBS.Obsel)
            if ret1:
                assert len(ret1) == 1
                new_obs = ret1[0]
                ret.append(new_obs)
                if new_obs != candidate:
                    replace_node_sparse(graph, candidate, new_obs)

    assert not bnode_candidates, bnode_candidates
    if not ret:
        raise InvalidDataError("No obsel found in posted graph")

    stats = self.trace_statistics
    if stats:
        # Traces created before @stats was introduced have no trace_statistics
        stats.metadata.set((stats.uri, METADATA.dirty, YES))
    return ret
