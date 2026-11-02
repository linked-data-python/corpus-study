"""Validation driver for MDD4REST__mdd4rest-annotator__server_src_rdflib2_plugins_parsers_pyRdfa_parse.py___parse_1_1.

The region is a statement run at module level: it fills `graph` from the
`state` of context_shim.py. Both modules are executed top to bottom and the
module graphs are compared by isomorphism (blank-node list heads are fresh
on each side). The shim's state holds the three shapes the region branches
on -- an initiated-but-empty list (rdf:nil), a one-element list, a list of
IRI / language literal / blank node -- and the graph starts with a triple
that must survive.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
