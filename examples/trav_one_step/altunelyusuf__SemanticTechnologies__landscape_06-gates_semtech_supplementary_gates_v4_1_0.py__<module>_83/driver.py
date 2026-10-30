"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_06-gates_semtech_supplementary_gates_v4_1_0.py__<module>_83.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a bare module-level statement (no enclosing function), so
entry=None is the oracle here: module-state comparison (rdfeval/harness.py).
`ab` is read but never written, so its isomorphism alone would be a hollow
green — but the harness's module-state branch also compares every other
comparable module-level value (`_values`), which is what actually exercises
the loop: `bad`, `ks`, `notes`, `insts` and `kind_cls` are all plain
lists/sets of RDF terms and strings, so they are compared directly. Checked
by deliberately mistranslating the m{ } pattern for `ks` during review: the
verdict failed on `bad`, `ks` and stdout together, confirming the comparison
is load-bearing, not vacuous.

`bad` collects every instance, so one fixture serves every case: each
instance decides one condition of the gate on its own (repair of
2026-10-30, fixture.ttl inst5..inst11).  inst5 has two notes (keeping only
the first, or testing `len(notes) < 1`, would let it pass); inst6 one kind
and a mismatched note (only the third condition fails); inst7 a kind and
zero notes; inst8/inst9 notes that match as `@en` and `^^xsd:string`
literals, with a blank-node and an integer provenance; inst10 the falsy
note ""; inst11 kind and note under neighbour predicates.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
