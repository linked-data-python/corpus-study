"""Validation driver for
ktbs__ktbs__lib_ktbs_methods_hrules.py___HRulesMethod_do_compute_obsels.

EXCLUDED (see meta.json). Both original.py and translated.ldpy do
`from rdfrest.util import check_new` at module level; `rdfrest` (kTBS's own
RDF-REST framework, a separate PyPI-less package this corpus does not
vendor) is not installed here (verified:
`~/.venvs/ldpy/bin/python -c "import rdfrest"` -> ModuleNotFoundError).
`_exec_python`/`_exec_ldpy` therefore fail identically at that import, on
*both* sides, before `entry`/`calls` is ever reached.

The region's real body also drives `computed_trace.source_traces`,
`source.obsel_collection` / `computed_trace.obsel_collection` (kTBS
ObselCollection objects backed by an RDF store with SPARQL-query and
edit-transaction methods -- `.build_select`, `.state.query`, `.edit(...)`,
`.add_obsel_graph`, `._empty()`), and calls `copy_obsel`/`translate_node`
(from the sibling `.utils` module) and `check_new` (from `rdfrest.util`).
kTBS's own test suite (utest/test_ktbs_method_hrules.py) exercises this
exact method only indirectly, through a live in-memory kTBS engine
(`KtbsTestCase`, `self.my_ktbs.create_base(...)`,
`ctr.obsel_collection.force_state_refresh()`) -- itself built on `rdfrest`,
`fsa4streams`, and friends, none installed here either. None of this is a
context-shim job: a shim restores a broken *binding* (an import path, a
constant -- see ktbs_namespace_context.py for the one that IS just that,
KTBS/KTBS_NS_URI). Reproducing kTBS's obsel-collection/trace-computation
engine well enough to drive this method for real would mean
re-implementing the system under test, which AGENT_BATCH.md forbids
("n'inventez pas de logique") -- the same call made for the vital-graph
sibling of this stratum (coercion_datatype), whose driver this one mirrors.

The one real ns_import_project rewrite here -- `from ..namespace import
KTBS, KTBS_NS_URI` -> `from ktbs_namespace_context import KTBS_NS_URI,
ktbs:`, `KTBS.hasTrace` -> `ktbs:hasTrace` -- transpiles cleanly (verified
directly: `python -m ldpy.transpiler` on translated.ldpy) and is not in
doubt; what cannot be established is whether the REGION as a whole still
behaves identically, because neither side can be executed past the
`rdfrest` import.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='do_compute_obsels',
    calls=[((), {})],  # never reached: the ModuleNotFoundError above fires
                        # while loading original.py/translated.ldpy, before
                        # entry is looked up
)
