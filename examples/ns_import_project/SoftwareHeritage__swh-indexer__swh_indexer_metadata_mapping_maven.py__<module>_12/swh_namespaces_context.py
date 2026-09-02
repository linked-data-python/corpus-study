# Context shim (see meta.json): the one binding this region needs from
# SoftwareHeritage/swh-indexer@95f3e654628b68ea963d06fb83b93011a6c2b47e :
# swh/indexer/namespaces.py -- SCHEMA, a plain `Namespace(...)` object.
# The real module is itself nothing but a small set of such bindings
# (SCHEMA, CODEMETA, FORGEFED, ACTIVITYSTREAMS, SPDX_LICENSES, XSD, plus a
# re-export of rdflib's own RDF) -- textbook ns_import_project shape, see
# meta.json's translation_notes for whether it should itself have been an
# ldpy module. `swh.indexer` is on PyPI (verified: `pip index versions
# swh.indexer` -> 4.12.0 latest) but not installed in this venv, and even
# installed it would not help: it is an ordinary Python file and exports no
# `__namespaces__`, which ldpy's `from … import p:` needs. Value transcribed
# verbatim (namespaces.py: SCHEMA = _Namespace("http://schema.org/")).
from rdflib import Namespace

SCHEMA = Namespace("http://schema.org/")

__namespaces__ = {"schema": SCHEMA}
