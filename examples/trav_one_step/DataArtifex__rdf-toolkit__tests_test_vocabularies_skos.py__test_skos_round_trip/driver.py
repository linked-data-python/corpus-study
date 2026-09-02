"""Validation driver for DataArtifex__rdf-toolkit__tests_test_vocabularies_skos.py__test_skos_round_trip.

This region READS a graph, so in principle the oracle is the equality of
the values both versions produce from the same input graph (design record
corpus/405). But the graph here is not external input: the region builds
its own Concept, serialises it to Turtle itself (`concept.to_rdf("turtle")`),
reparses that, and only then reads it back (`g.subjects(RDF.type,
SKOS.Concept)`). There is nothing for a `fixture.ttl` to supply -- see
`fixture.ttl` for that note -- so `entry` calls the `demo` harness (added
identically to both original.py and translated.ldpy, see meta.json) with no
arguments; `demo` turns the region's internal assertions into a comparable
"ok" / ("assertion-failed", msg) value instead of letting an AssertionError
abort the driver.

EXCLUDED (see meta.json): `dartfx.rdf.pydantic.skos` is not resolvable in
this venv -- the package (`dartfx-rdf` on the source repo's own
pyproject.toml) is not published to PyPI at all (`pip index versions
dartfx-rdf` / `dartfx` / `dartfx-rdf-toolkit` all report no matching
distribution; verified before writing this note). This is the "inexistent
on PyPI" case, not "present but uninstalled": there is no package to
install into ~/.venvs/ldpy. `rdfeval check` therefore fails at the
`import dartfx...` line, on both sides identically, before `entry` is ever
reached. The translation itself (`m{ }` for the one-step subject read) was
verified independently as valid ldpy syntax via
`ldpy.transpiler.transpile()`, which does not need the missing package.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[lambda: ((), {})],
)
