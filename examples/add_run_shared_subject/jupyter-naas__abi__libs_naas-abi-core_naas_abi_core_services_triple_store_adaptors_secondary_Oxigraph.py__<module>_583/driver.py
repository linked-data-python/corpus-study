"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_services_triple_store_adaptors_secondary_Oxigraph.py__<module>_583.

Establishes semantic equivalence of original.py and translated.ldpy. The
region's RDF logic was restored out of an `if __name__ == "__main__":`
guard (see meta.json / original.py header) so it actually runs under
run_pair's `exec()` (which never sets `__name__` to "__main__"). The
`Oxigraph` adapter (network dependency) is replaced by an in-memory shim
(oxigraph_shim.py) so `test_graph` is actually built and inserted/queried,
identically on both sides -- module-state comparison then judges `test_graph`
by isomorphism and the rest by matching stdout.

The region's own `row.count` (line `f"  Total triples: {row.count}"`) is a
pre-existing bug in the source, not something translation touches:
`ResultRow` is a `tuple` subclass, so `.count` resolves to the inherited
`tuple.count` *bound method*, never the SPARQL-bound `?count` value.
Printing that bound method embeds its `id()`, which differs between the two
runs (fresh objects each time) though the underlying program is unchanged
on both sides -- so `stdout_filter` blanks that one address out, the same
way the harness's own docs treat a fresh `Graph()` identifier.
"""
import re

from rdfeval.harness import run_pair


def _blank_method_addresses(text: str) -> str:
    return re.sub(r"at 0x[0-9a-fA-F]+", "at 0x_", text)


# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
    stdout_filter=_blank_method_addresses,
)
