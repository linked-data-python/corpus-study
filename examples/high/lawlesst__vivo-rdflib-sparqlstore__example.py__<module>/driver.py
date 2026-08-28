"""Validation driver for the vivo-rdflib-sparqlstore example module.

The region is a whole script: ``run_pair`` with ``entry=None`` executes both
representations and compares every rdflib Graph left in the module globals
(``g`` and ``named_graph``) plus the captured stdout -- which here carries
both the N3 serialisation of the parsed data and the concept listing, so the
comparison covers term identity, graph content AND iteration order.

The three VIVO_* environment variables the script reads are provided here
(the shim store ignores the endpoints; see vstore.py).
"""
import os

os.environ.setdefault("VIVO_EMAIL", "curator@example.org")
os.environ.setdefault("VIVO_PASSWORD", "s3cret")
os.environ.setdefault("VIVO_BASE", "http://vivo.example.org")

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
