"""Validation driver for cognitedata__neat__cognite_neat__v0_core__data_model_exporters__data_model2semantic_model.py__OWLClass_title_triples.

The region is a @property body lifted out of its pydantic class, so `demo`
(identical on both sides, see meta.json) attaches it to a minimal
reconstruction of OWLClass and reads the property off a fresh instance. The
oracle is value equality on the returned triple list -- rdfeval.harness
compares RDF terms (URIRef, Literal with its datatype), not raw reprs, so a
coercion mistake would be caught even though there is no Graph here to check
by isomorphism.

Two cases: `self.label` truthy (the branch that builds the triple, where the
stratum's site sits) and falsy (the early `return []`).
"""
from rdflib import URIRef

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        ((URIRef("http://example.org/ns#Widget"), "Widget"), {}),
        ((URIRef("http://example.org/ns#Widget"), None), {}),
    ],
)
