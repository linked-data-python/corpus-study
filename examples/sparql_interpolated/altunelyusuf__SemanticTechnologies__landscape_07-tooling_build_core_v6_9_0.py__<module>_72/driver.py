"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_core_v6_9_0.py__<module>_72.

IDENTITY translation (see meta.json): the region validates SPARQL/Turtle/
JSON text read at runtime from `eg.SNIPPETS` -- out of reach for `g{ }`/
`s{ }`, which are parsed at transpile time (see translation_notes).

No rdflib Graph survives at module level (each `Graph()` is throwaway,
built only to call `.parse()` for its side effect of raising or not), so
module-state comparison's graph check contributes nothing here; what
actually proves the two sides agree is `errs`, the module-level list both
sides build by validating context_shim.eg.SNIPPETS -- crafted (see that
file's header) to hit every branch: a valid+known snippet of each check
kind (silent), a known snippet with broken syntax ("snippet invalid"), an
unknown-but-valid one ("snippet class unknown"), an unknown AND invalid one
(both errors), and a known garbage snippet whose check is "none" (skipped,
must NOT raise).
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout and other module-level values,
# `errs` among them).
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
