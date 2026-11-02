# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/serpar/jsonld_serializers.py
# region: trace_stats_to_json (lines 857-960, stratum bind_initbindings)
# licence of the source repository: see meta.json
from collections import OrderedDict
from itertools import groupby
# Context shim: the package-level names the region uses (see shim.py).
from shim import compact, CONTEXT_URI, load_document, KTBS_NS_STATS, ValueConverter

def trace_stats_to_json(graph, tstats, bindings=None):
    """
    I create an Ordered dictionary for a further json-ld serialization.

    :param graph: ? graph
    :param tstats: TraceStatistics object
    :param bindings: ?
    :return: The dictionnary created.
    """
    tstats_dict = OrderedDict({
        '@context': CONTEXT_URI,
        '@id': './',
        'hasTraceStatistics': {'@id': '', '@type': 'TraceStatistics'},
    })

    trace_uri = tstats.trace.uri
    model_uri = tstats.trace.model_uri
    if model_uri[-1] not in { "/", "#" }:
        model_uri += "#"
    val2jsonobj = ValueConverter(trace_uri).val2jsonobj

    initBindings = {'trace': trace_uri}

    # How could I get predicates in the form stat:xxxxx
    # in the results, InitNs does not seem to be enough
    # Is it because of the filter clause ?
    for pred, obj, _ in graph.query("""
        SELECT ?pred ?obj
            $trace # selected solely to please Virtuoso
        {{
            $trace ?pred ?obj

            filter (strstarts(xsd:string(?pred), "{0:s}"))
        }}
    """.format(KTBS_NS_STATS), initBindings=initBindings):
        if pred != KTBS_NS_STATS.obselCountPerType:
            tstats_dict[pred] = val2jsonobj(obj)

    # Recover data inside blank nodes : another request needed
    stats_infos = graph.query("""
        SELECT ?bn ?pred ?obj
            $trace # selected solely to please Virtuoso
        {
            $trace stats:obselCountPerType ?bn .

            ?bn ?pred ?obj .
        }
        ORDER BY ?bn
        """, initNs={'stats': str(KTBS_NS_STATS)}, initBindings=initBindings)

    if stats_infos:
        tstats_dict[KTBS_NS_STATS.obselCountPerType] = [
            {str(pred): val2jsonobj(obj)  # cast URIRef to plain unicode
             for _, pred, obj, _ in tuples}
            for bn, tuples in groupby(stats_infos, lambda tpl: tpl[0])]

    compact_context = {'@context': [ CONTEXT_URI,
                                     {'stats': KTBS_NS_STATS,
                                    'stats:hasObselType': {'@type': '@id'},
                                    'm': model_uri}
                                   ]
                        }

    tstats_dict = compact(tstats_dict, compact_context,
                          {'base': tstats.uri,
                           'documentLoader': load_document})

    final = OrderedDict.fromkeys(['@context', '@id', 'hasTraceStatistics', 'stats:obselCount'])
    # None as no meaning in jsonld, if there is no arc in the graph there
    # should be no value. We could remove the keys which values are None
    # instead of this test
    if tstats_dict.get('stats:minTime') is not None:
        final.update(dict.fromkeys(['stats:minTime', 'stats:maxTime', 'stats:duration']))
    final.update(tstats_dict)

    # PyLD return "@stats" for the current URI which is not wrong
    # but we prefer an empty string for the sake of consistency
    final['hasTraceStatistics']['@id'] = ''

    return final
