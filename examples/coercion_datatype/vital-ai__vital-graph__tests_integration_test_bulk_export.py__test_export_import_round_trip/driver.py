"""Validation driver for vital-ai__vital-graph__tests_integration_test_bulk_export.py__test_export_import_round_trip.

EXCLUDED (see meta.json). Both original.py and translated.ldpy import
`vitalgraph.db.sparql_sql.bulk_export` at module level, and `vitalgraph` is
vital-graph's own async SQL-backed store implementation -- not published to
PyPI, not vendored here, and not importable without it (verified:
`~/.venvs/ldpy/bin/python -c "import vitalgraph"` -> ModuleNotFoundError).
`_exec_python`/`_exec_ldpy` therefore fail identically at the very first
line of the region, on *both* sides, before `entry`/`calls` is ever reached.

The region's real body also calls `_counts`/`_quad_uuids`, two sibling test
helpers defined elsewhere in the ~200-line source file and not carried by
the extraction, and drives `space_impl`/`two_spaces`, pytest fixtures that
(per the source repository's test suite) stand up a live async connection
pool against a real database. None of this is a context-shim job: a shim
restores a broken *binding* (an import path, a constant); reproducing
vitalgraph's SQL store or a live DB pool would mean re-implementing the
system under test, which AGENT_BATCH.md forbids ("n'inventez pas de
logique"). No `calls=` fixture can make this reach the coercion_datatype
site under study -- the import fails first, for both sides, so any fixture
list would be theatre.

The coercion_datatype rewrite itself (Literal(i, datatype=XSD.integer),
i a loop counter -> f{i}; URIRef(f"urn:export:e:{i}") -> f<urn:export:e:{i}>)
was checked independently by direct execution against ldpy.runtime, outside
this harness (see translation_notes in meta.json): for every int i in
range(30), ldpy.runtime.node(i) == Literal(i, datatype=XSD.integer) and
ldpy.runtime.firi('urn:export:e:', i) == URIRef(f"urn:export:e:{i}"),
term-for-term, datatype included.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_export_import_round_trip',
    calls=[((), {})],  # never reached: the ModuleNotFoundError above fires
                        # while loading original.py/translated.ldpy, before
                        # entry is looked up
)
