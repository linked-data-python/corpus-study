"""Context shim (see meta.json) for the `yatter` package.

yatter (the YARRRML -> [R2]RML translator) is not installable in the
evaluation environment: it pulls in `coloredlogs` and `pyjelly`, neither of
which is available.  The region under evaluation only *calls* yatter and then
does rdflib work with the Turtle it returns, so this stub supplies
`translate()` and leaves the region's own RDF operations (two Graph(), two
parse(), one isomorphism check) fully exercised.

`translate()` returns the RML mapping the real yatter produces for
YARRRMLTC-0050, taken from the test case's own reference file mapping.ttl,
but re-serialised: the blank-node labels and the statement order therefore
differ from the reference, so the region's `compare.isomorphic` really has to
compute an isomorphism over the ten blank nodes of the three triples maps
rather than compare two identical strings.

Imported IDENTICALLY by original.py and translated.ldpy.
"""

import os

from rdflib.graph import Graph

RML_URI = "http://semweb.mmlab.be/ns/rml#"

_HERE = os.path.dirname(os.path.realpath(__file__))


def translate(yarrrml_data, mapping_format=RML_URI):
    """Stand-in for yatter.translate(): returns the expected RML as Turtle."""
    if "mappings" not in yarrrml_data:
        raise ValueError("shim yatter: not a YARRRML document")
    g = Graph()
    g.parse(os.path.join(_HERE, "mapping.ttl"), format="ttl")
    return g.serialize(format="ttl")
