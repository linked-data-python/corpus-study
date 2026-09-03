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
"""
import re

from rdfeval.harness import run_pair


def _blank_bnode_labels(text: str) -> str:
    return re.sub(r"BNode\('[^']*'\)", "BNode('_')", text)


# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
    stdout_filter=_blank_bnode_labels,
)
