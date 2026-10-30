"""Validation driver for SynBioDex__sbol_factory__custom_eval.py__<module>_1.

Establishes semantic equivalence of original.py and translated.ldpy. The
region's RDF logic was restored out of an `if __name__ == "__main__":`
guard (see meta.json / original.py header) so it actually runs under
run_pair's `exec()` (which never sets `__name__` to "__main__"), against
foaf.n3 (also restored, see that file's header): 213 triples, 26 of them
`foaf:Person`, none directly `foaf:Agent` -- so the query's 26 solutions
only appear if the custom SPARQL eval + the added `foaf:Person
rdfs:subClassOf foaf:Agent` triple actually combine to infer them; an empty
result (e.g. a broken custom eval registration) would be silently wrong,
not just quantitatively different.

`x` (each solution row) is only printed, never assigned to a comparable
module-level variable, so module-state comparison's stdout check is what
actually exercises the query here. One of the 26 solutions is an inline
blank node from foaf.n3 itself ("Danny Ayers", typed foaf:Person with no
IRI) -- run_pair execs original.py and translated.ldpy in sequence in the
SAME process, so rdflib's process-global auto-BNode-id counter has already
advanced by the time the second side parses the same foaf.n3, and the two
sides print two DIFFERENT auto-generated labels for what is otherwise the
identical blank node (same predicates, same neighbourhood) -- not a
difference in what either program computes. stdout_filter blanks out the
label (never a program's meaning per rdfeval.harness's own docs) so the
comparison is on content, not on this process-order artefact.

Repair (2026-10-30), three strengthenings.

1. The two sides run in the same process, and rdflib's registry
   `rdflib.plugins.sparql.CUSTOM_EVALS` is process-global: whatever the
   original registers stays visible to the translation, so a translation that
   forgot the registration line would still have its query rewritten by the
   original's function.  `_isolated` wraps the harness's artefact execution:
   the registry is emptied before each side, and after it the side must have
   registered ITS OWN `customEval` (the function object of its own namespace,
   under "exampleEval", and nothing else); otherwise the side fails with an
   AssertionError, which run_pair reports as the verdict's error.  The
   registry is restored afterwards.
2. foaf.n3 gets three resources the 26 people do not cover (see its last
   block): one typed foaf:Agent directly, one instance of a declared subclass
   of foaf:Agent, one that is no Agent.  The query for foaf:Agent now has 28
   solutions, and a query for foaf:Person (26) or for any other class, or a
   missing `+{ foaf:Person rdfs:subClassOf foaf:Agent }`, changes the output.
3. Only the stdout of the query is the observable, so the rows are compared
   as printed (blank-node labels masked, as above).
"""
import re

import rdflib
import rdflib.plugins.sparql

from rdfeval import harness
from rdfeval.harness import run_pair


def _blank_bnode_labels(text: str) -> str:
    return re.sub(r"BNode\('[^']*'\)", "BNode('_')", text)


_execute = harness._exec_artefact


def _isolated(path, name):
    """Execute one side with an empty registry and require its own entry."""
    registry = rdflib.plugins.sparql.CUSTOM_EVALS
    saved = dict(registry)
    registry.clear()
    try:
        ns, out = _execute(path, name)
        mine = dict(registry)
        assert set(mine) == {"exampleEval"}, (
            f"{path.name} registered {sorted(mine)}, expected ['exampleEval']")
        assert mine["exampleEval"] is ns["customEval"], (
            f"{path.name}: CUSTOM_EVALS['exampleEval'] is not its own customEval")
        return ns, out
    finally:
        registry.clear()
        registry.update(saved)


harness._exec_artefact = _isolated

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
    stdout_filter=_blank_bnode_labels,
)
