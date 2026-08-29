"""Validation driver for JustlyAI__lmss_entity_extractor__app_lmss_classification.py__OntologyClassifier___init__.

The region is a constructor lifted out of its class (see meta.json /
original.py for the `demo` harness both files carry identically). `demo`
rebuilds a minimal stand-in instance, calls the extracted __init__, and
returns the graph it wrote -- meta.oracle: isomorphism.

The fixtures: `fixture.ttl` for `self.graph.parse(graph_path, ...)`, and two
JSON files standing in for the index/top-classes files the real constructor
reads through `_load_ontology_index` / `_load_top_classes` (transcribed
verbatim in context_shim.py -- see its header).
"""
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent


def case():
    return lambda: ((str(HERE / "fixture.ttl"),
                      str(HERE / "fixture_index.json"),
                      str(HERE / "fixture_top_classes.json")), {})


VERDICT = run_pair(__file__, entry="demo", calls=[case()])
