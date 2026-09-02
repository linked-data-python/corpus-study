"""Validation driver for DerwenAI__kglab__kglab_gpviz.py__GPViz___init__.

Establishes semantic equivalence of original.py and translated.ldpy.

classification: not-expressible (see meta.json) -- `translated.ldpy` is
byte-identical in RDF-relevant content to `original.py` (no island is used),
so this driver only needs to prove the constructor still runs and produces
the same `namespaces`/`blank_nodes`/`values`/`triples` state on both sides.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='_summarize',
    calls=[
        lambda: (
            (
                "SELECT ?s WHERE { ?s a ex:Thing }",
                {"ex": "http://example.org/"},
            ),
            {},
        ),
    ],
)
