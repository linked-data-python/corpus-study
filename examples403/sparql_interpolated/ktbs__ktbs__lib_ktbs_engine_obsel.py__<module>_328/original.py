# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/engine/obsel.py
# region: <module> (lines 328-338, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql.processor import prepareQuery
from ..namespace import KTBS, RDF

_RELATED_OBSELS = prepareQuery("""
    SELECT DISTINCT ?other
        $obs # selected solely to please Virtuoso
    {
        { $obs ?pred ?other . }
        UNION
        { ?other ?pred $obs . }
        $obs <%s> ?trace .
        ?other <%s> ?trace .
    }
    """ % (KTBS.hasTrace, KTBS.hasTrace))
