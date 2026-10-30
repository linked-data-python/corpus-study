"""Validation driver for usc-gria__sw-kg__materials_rdflib_python_task04.py__<module>_1.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a whole module (a notebook): it loads fixture.ttl, runs five
queries and prints their rows, so the oracle is module-state plus the
captured stdout -- every row of every query is compared, in order.

What makes the green mean something is fixture.ttl (strengthened by the
repair of 2026-10-30): q3 and q5 bind a variable through initBindings
(Literal('Smith'/'Jane Smith', datatype=XSD.string)), which the translation
writes as a typed literal term in the pattern.  The fixture holds, for each
term of those patterns, a neighbour sharing the other two -- a person who
knows someone NOT named "Jane Smith", people whose "Jane Smith" or "Smith" is
plain or @en (other terms than ^^xsd:string), the same typed literal under
another predicate, a relation to Jane other than foaf:knows, a knower with
no vcard:Given, an e-mail under vcard:EMAIL -- so dropping a bound term,
widening it to a variable, or changing its datatype adds or removes a
printed row.  A second knower of Jane (as in the repository's example3.rdf)
gives q5 more than one solution.
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
