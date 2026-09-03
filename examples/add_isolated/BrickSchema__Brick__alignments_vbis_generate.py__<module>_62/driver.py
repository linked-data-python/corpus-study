"""Validation driver for BrickSchema__Brick__alignments_vbis_generate.py__<module>_62.

Module-level region (kind: statement, qualname <module>) with no entry
point: `original.py` and `translated.ldpy` are both executed top to bottom
and their module globals compared. The only rdflib Graph in scope is
`graph`, so the oracle is RDF isomorphism on it (meta.oracle ==
"isomorphism").

The region's own helpers (get_brick_class, get_vbis_tags,
rewrite_vbis_pattern) live ABOVE line 62 in the source file, outside this
extraction; the context shim vbis_context.py reproduces the three functions
verbatim so the `with open("vbis-brick-v5.csv") as f:` loop has something
to call. vbis-brick-v5.csv itself is not part of the source repository (the
real file has thousands of rows) -- it is a small fixture written for this
pair, covering: a class with a single VBIS pattern (SH:pattern branch), a
class with two patterns (SH:or + rdf:Collection branch), a class with two
fully-qualified tags (SH:in + rdf:Collection branch), a class with a single
fully-qualified tag (SH:hasValue branch), a repeated class (skipped via
`finished_brick_classes`, second occurrence must not add a second shape), a
row with no Brick Class column filled in (skipped, `bc is None`), and a
class with no VBIS tags at all (skipped, `len(tagsOrPatterns) == 0` -- the
neighbourhood that must not produce a shape).
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
