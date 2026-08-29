"""Validation driver for mpsonntag__snippets__python_odmlToRDF_subclassing.py__test_rdf_subclassing_queries.

EXCLUDED (see meta.json): the region needs the third-party `odml` package
(odml.Document, odml.Section, odml.tools.RDFWriter) to build the RDF graph
it then queries -- the RDFS-subclass entailment under test is produced by
running odml's real RDF writer and owlrl's real DeductiveClosure, not
something a fixture graph or a hand-written shim could stand in for without
inventing the very logic the test exists to check. `odml` is not installed
in ~/.venvs/ldpy (`owlrl` is, but `import odml` fails), so this driver
cannot run; the translation itself is otherwise believed correct (see
translation_notes) and would be checked here if the dependency were
available.

The region is a pytest test that only ever asserts and returns nothing, so
both files carry an identical `demo` harness (excluded from surface
metrics, same convention as the `bind_initbindings/...zone_surfaces`-style
and LA3D trav_existence precedents) that turns a failed assertion into a
comparable value instead of letting it abort the driver with nothing
observed.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[((), {})],
)
