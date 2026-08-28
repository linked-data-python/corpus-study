"""Validation driver for the kgsum dataset_preparation module.

The module itself only defines functions (no module-level graph, no output),
so entry=process_file_full_inplace is used instead: it drives every SPARQL
query of the region over a small local dataset and returns the extracted
feature dictionary, which the harness normalises and compares term by term.
"""
import os

from rdfeval.harness import run_pair

SAMPLE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                      'sample_dataset.ttl')

VERDICT = run_pair(
    __file__,
    entry='process_file_full_inplace',
    calls=[
        lambda: ((SAMPLE,), {}),
        lambda: ((SAMPLE,), {'ingest_lov': True}),
        lambda: (('',), {}),
    ],
)
