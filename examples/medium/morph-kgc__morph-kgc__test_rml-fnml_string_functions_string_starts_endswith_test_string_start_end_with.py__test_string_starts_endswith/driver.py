"""Validation driver: the region is a pytest test taking no argument.

mapping.yarrrml, rmlmapperoutput.ttl and cars.csv (all tiny, Apache-2.0) were
copied next to the example.  The two first ones resolve, because the region
looks them up in dirname(realpath(__file__)) — the example directory, shared
by original.py and translated.ldpy.  The CSV does NOT: the region computes it
as dirname(dirname(realpath(__file__))), i.e. one directory ABOVE the example
(in the corpus, test/rml-fnml/string_functions/cars.csv, shared by ~18 sibling
tests), and morph-kgc reads exactly that path from the `file_path` config key.
Copying cars.csv to ../cars.csv makes both sides pass; this review was scoped
to the example directory, so the verdict stays "unresolved" — identically for
both representations, which fail with the same FileNotFoundError.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_string_starts_endswith",
                   calls=[lambda: ((), {})])
