"""Validation driver for
ScaDS__KGpipe__src_kgpipe_tasks_schema_alignment_transformer_tasks.py__SimpleTransformerBasedRelationLinker___init__.

This region READS a graph, so the oracle would be the equality of the
values both versions produce from the same input graph (design record
corpus/405), not isomorphism -- `__init__` parses `ontology_file` itself
(`g.parse(ontology_file)`), so -- like the owl_to_mermaid sibling in this
same batch -- the fixture PATH is the argument, not a pre-parsed graph.

EXCLUDED (see meta.json): both sides fail identically at their very first
line, `from sentence_transformers import SentenceTransformer, util` --
`sentence_transformers` is not installed in this study's rdflib==7.2.1-
pinned venv (confirmed: `python -c "import sentence_transformers"` raises
ModuleNotFoundError). Unlike a plain "present on PyPI but not installed"
gap (`pip index versions sentence-transformers` -> 6.0.1 et al., so it
COULD be installed), the constructor this `__init__` calls,
`SentenceTransformer(model_name)`, downloads real pretrained model weights
from the Hugging Face Hub at call time when they are not already cached
locally -- a standing network dependency, not a one-time package install,
and one this study's own reproducibility rule (rdfeval check must pass the
same way for anyone, offline included) treats as out of scope. So this
driver is not run to a verdict; it exists to record the intended call
shape, exactly as `translated.ldpy` was still written and independently
transpile-checked (see meta.json) even though the pilot cannot execute it.
"""
from pathlib import Path
from types import SimpleNamespace

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _case():
    # A fresh receiver per call, mirroring how `__init__` is actually used
    # (mutating a fresh instance); `ontology_file` is the fixture PATH,
    # parsed by the region's own `g.parse(ontology_file)`, not a pre-parsed
    # graph -- run_pair's generic single-graph `fixture=` wiring does not
    # apply here for the same reason it does not for owl_to_mermaid.
    return ((SimpleNamespace(), str(FIXTURE)), {})


VERDICT = run_pair(
    __file__,
    entry='__init__',
    fixture="fixture.ttl",
    calls=[_case],
)
