"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_06-gates_semtech_supplementary_gates_v1_0_0.py__<module>_149.

Module-level script (kind="statement"), so entry=None: both original.py and
translated.ldpy are executed as modules and every module-level value is
compared -- both the parsed `g_ab` graph (isomorphism) and, crucially, the
derived `ex_no_prov` list of strings (module-state values, per
rdfeval.harness._values: "a region that neither builds nor mutates a graph
... leaves its result in a module variable").  There is no `fixture.ttl`
here: both sides parse the SAME real ontology file via the `H` context shim
(see meta.json/context.py), not a synthetic input.

Caveat, stated rather than hidden: at commit bad0fa7c46,
landscape/02-ontology/semtech_abox_v1_0_0.ttl happens to have provenance
recorded for every T-prefixed owl:NamedIndividual, so `ex_no_prov == []` on
*both* sides here -- a real risk of a hollow green (corpus/405: "un fixture
pauvre rend un vert sans valeur"). This OK is therefore not, by itself, proof
that the m{ } join + negation is right; it only proves the two sides agree on
this one (here: empty) input. The join/negation logic was independently
exercised against a small synthetic graph covering several solutions, the
zero-solution case, and non-matching neighbours (wrong type prefix, has
provenance, not a NamedIndividual at all) -- see translation_notes in
meta.json for the result.
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
