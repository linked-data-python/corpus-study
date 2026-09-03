"""Validation driver for jupyrdf__ipyradiant__src_ipyradiant_query_framer.py__SPARQLQueryFramer_print_vars.

NOT-EXPRESSIBLE (see meta.json): `print_vars` is a generic reflection
utility called on WHATEVER SPARQL a subclass has set -- `cls.sparql`
(compiled via `prepareQuery(cls.sparql, initNs=cls.initNs)`) or an
already-prepared `cls.query` object. Neither branch has a SPARQL query text
known at the call site the way `s{ }` requires (it validates and parses its
query text at TRANSPILE time): `cls.sparql` is a runtime string set by
whichever subclass calls this, and `cls.query` is an opaque, already-compiled
Query object with no text at all by the time this method sees it.
Structurally the same gap as the TDCC-NES/askwol `_prepare` region elsewhere
in this stratum. translated.ldpy is byte-identical to original.py;
`constructions` is empty on purpose, not an oversight.

`print_vars` is also a classmethod reading class attributes rather than a
function with arguments to vary, and it prints rather than returning a
value: entry=/calls= directly on `print_vars` would exercise only the
class's default (empty) state every time, and a callable `case()` in
`calls` has no handle onto the class objects `original.py`/`translated.ldpy`
each construct in their own execution namespace (see rdfeval.harness
`_exec_python`/`_exec_ldpy`) to mutate them from here. `demo` (identical on
both sides, see meta.json/original.py) sidesteps this by building its own
subclasses INSIDE the module under test and calling `.print_vars()` on
each, covering both of the method's branches; run_pair's per-call stdout
capture is the actual comparison ("a region whose whole effect is printing
has nothing else to compare").
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[((), {})],
)
