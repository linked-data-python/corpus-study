"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_query___init__.py__Query_ontdoc_inference.

The region is a module-level statement acting on `g`; the shim binds `g` to
a graph parsed from fixture.ttl (fresh in each side's process).  The graph
is compared by isomorphism after the loop has moved dc:creator /
schema:creator / schema:author to dcterms:creator.  The fixture has
neighbours that must stay: dc:contributor, dcterms:creator already present,
the http:// (not https://) schema.org creator, a non-author schema.org
property, and a triple whose OBJECT is the subject of a dc:creator.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
