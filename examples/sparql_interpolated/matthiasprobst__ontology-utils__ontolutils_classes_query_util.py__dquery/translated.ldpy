# Extracted from matthiasprobst/ontology-utils@668f1b884a : ontolutils/classes/query_util.py
# region: dquery (lines 200-240, stratum sparql_interpolated)
# licence of the source repository: see meta.json
#
# `import logging` restores a binding the sampled context lines dropped (the
# region only got `logger = logging.getLogger('ontolutils')`, not the import
# that makes it resolve) -- see meta.json / AGENT_BATCH.md "shim de contexte".
# `expand_sparql_res` is not part of the region either (it is a sibling
# function in the same source file, called by `dquery` but never sampled by
# it): context_shim.py carries it, and everything it in turn calls,
# verbatim.
import logging
import pathlib
from typing import Union, Dict, List, Optional, Type
import rdflib
from context_shim import expand_sparql_res
logger = logging.getLogger('ontolutils')

def dquery(subject: str,
           source: Optional[Union[str, pathlib.Path]] = None,
           data: Optional[Union[str, Dict]] = None,
           context: Optional[Dict] = None) -> List[Dict]:
    """Return a list of resutls. The entries are dictionaries.

    Example
    -------
    >>> # Query all agents from the source file
    >>> import ontolutils
    >>> ontolutils.dquery(subject='prov:Agent', source='agent1.jsonld')
    """
    g = rdflib.Graph()
    g.parse(source=source,
            data=data,
            format='json-ld',
            context=context)
    if context is None:
        context = {}
    prefixes = "".join([f"PREFIX {k}: <{p}>\n" for k, p in context.items() if not k.startswith('@')])

    assert isinstance(subject, str), f"Subject must be a string, not {type(subject)}"

    query_str = f"""
    SELECT *
    WHERE {{
        ?id a {subject}.
        ?id ?p ?o .
}}"""

    res = g.query(prefixes + query_str)

    if len(res) == 0:
        return []

    logger.debug(f'Querying subject="{subject}" with query: "{prefixes + query_str}" and got {len(res)} results')

    kwargs: Dict = expand_sparql_res(res.bindings, g, True, True)
    for _id in kwargs:
        kwargs[_id]['@id'] = _id
    return [v for v in kwargs.values()]
