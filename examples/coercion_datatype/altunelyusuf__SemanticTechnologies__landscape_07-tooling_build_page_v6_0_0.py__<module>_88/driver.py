"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_page_v6_0_0.py__<module>_88.

Module-level region (no function to call): entry=None executes both
original.py and translated.ldpy and compares every rdflib Graph found in the
module globals (g, by isomorphism and prefix bindings) plus the other
module-level values both sides define (HERE, lo15, w20, n13, the loop's last
tr).

`HERE`, `S` and `byid` are restored by context_shim.py (see meta.json);
`HERE` points at 04-page/semtech_page_abox_v5_4_0.ttl, a stand-in that
already holds the page, an older widget (sp:W19, which must stay untouched)
and a French label on sp:W20 itself, so the eight added triples meet
existing data rather than an empty graph. The language tag of the six
literals is part of the isomorphism, among them the one whose lexical form is
computed (`S(*refs) | S("NR-PYODIDE")`).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
