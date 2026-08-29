"""Validation driver for
EMMC-ASBL__tripper__tests_test_triplestore.py__test_backend_rdflib_graph.

EXCLUDED (see meta.json). Both original.py and translated.ldpy do
`from tripper import RDF, RDFS, Triplestore` inside the function body;
`tripper` (EMMC-ASBL's own Triplestore-wrapper package, not rdflib itself)
is not installed here (verified:
`~/.venvs/ldpy/bin/python -c "import tripper"` -> ModuleNotFoundError).
The module itself execs fine (the import is inside the function, so
defining it does not trigger it); calling the entry point does, on *both*
sides, identically, before the `get_ontology_path` argument is ever used.

Most of the region's RDF traffic is not raw rdflib either: `ts.value(...)`,
`ts.bind(...)`, `ts.add_triples(...)` are tripper's `Triplestore` wrapper
API, a third-party abstraction over rdflib -- out of the language's reach
(ldpy islands address `rdflib.Graph`, not an arbitrary wrapper class), and
correctly left as plain Python in translated.ldpy.

The one genuine `rdflib.Graph` read is the last line:
`graph.value(URIRef(":Nils"), URIRef(RDF.type)) == URIRef(FAM.Father)`.
Its value is not thrown away for its truth -- it is compared to
`URIRef(FAM.Father)` -- so per INSTRUCTIONS_403 the specific construction is
`.first()`, not `bool(m{ })`; the region does not carry the trav_existence
idiom its stratum targets (see meta.json/translation_notes). That line is
the only one translated:
`m{ <:Nils> f{URIRef(RDF.type)} ?o }.first() == URIRef(FAM.Father)`.
It transpiles cleanly (verified directly) and is not in doubt on its own;
what cannot be established is whether the region AS A WHOLE still behaves
identically, because neither side can be executed past the `tripper`
import, and the `get_ontology_path("family")` fixture it would also need
is EMMC-ASBL/tripper's own test data, not vendored in this corpus either
(see ontology_path_context.py, a minimal stand-in used only by this
driver -- ts.value(FAM.Father, RDFS.subClassOf) == FAM.Person and
ts.value(FAM.Dauther, RDFS.subClassOf) == FAM.Person are the only facts it
needs, so that is all fixture.ttl holds).
"""
from rdfeval.harness import run_pair


def _case():
    from ontology_path_context import get_ontology_path
    return ((get_ontology_path,), {})


VERDICT = run_pair(
    __file__,
    entry='test_backend_rdflib_graph',
    calls=[_case],  # never reached past the ModuleNotFoundError above
)
