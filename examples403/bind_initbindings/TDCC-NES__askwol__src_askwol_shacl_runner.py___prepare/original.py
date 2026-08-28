# Extracted from TDCC-NES/askwol@3534557e8b : src/askwol/shacl_runner.py
# region: _prepare (lines 33-36, stratum bind_initbindings)
# licence of the source repository: see meta.json
import functools
from rdflib.plugins.sparql import prepareQuery

@functools.lru_cache(maxsize=256)
def _prepare(query_text: str, init_ns_items: tuple | None, base: str | None):
    init_ns = dict(init_ns_items) if init_ns_items else None
    return prepareQuery(query_text, initNs=init_ns, base=base)
