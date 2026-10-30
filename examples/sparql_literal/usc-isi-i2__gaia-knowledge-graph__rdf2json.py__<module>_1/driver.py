"""Validation driver for usc-isi-i2__gaia-knowledge-graph__rdf2json.py__<module>_1.

The region is a whole module: it parses ``sample1.turtle`` (a fixture written
for the study, not in the repository), runs one SELECT, folds the solutions
into ``d`` and ``res`` and dumps ``res`` to ``output.json``.  With
``entry=None`` the harness executes both modules and compares their shared
module-level values in order: ``d`` and ``res`` are exactly what the file
receives, so comparing them compares the written JSON.

What the fixture makes visible (each part of the query has a node that only
it decides; checked at repair by mutating a copy of the translation):
  * ``_:st1``/``_:st3`` (first UNION branch) and ``_:st2`` (second branch):
    several solutions, both encodings of a statement;
  * ``_:untyped`` (no rdf:type) — dropping the ``rdf:type rdf:Statement``
    anchor of branch 1 adds a solution;
  * ``_:otherlink`` (``ex:kind rdf:Statement``) — widening ``rdf:type`` into
    a variable adds one;
  * ``_:claim`` (typed ``ex:Claim`` with an ``rdf:predicate``) — widening the
    object ``rdf:Statement`` into a variable adds ``ex:says``;
  * ``_:st1dup`` (same triple as ``_:st1``) — dropping DISTINCT appends
    ``ex:acme`` twice;
  * ``_:incomplete`` (no rdf:object) and a plain ``ex:name`` triple — must
    match nothing.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
