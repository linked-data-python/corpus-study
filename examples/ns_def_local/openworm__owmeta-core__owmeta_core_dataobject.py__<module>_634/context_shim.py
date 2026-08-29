# Context shim (see meta.json): the two constants this region's single
# statement needs, transcribed verbatim from owmeta_core/__init__.py of
# openworm/owmeta-core@cd69d77ad0 (local clone:
# corpus/repos/openworm__owmeta-core/owmeta_core/__init__.py, lines 25-26).
#
# DEF_CTX and RDF_CONTEXT are also imported by original.py -- matching the
# real module's `from . import BASE_DATA_URL, BASE_SCHEMA_URL, DEF_CTX,
# RDF_CONTEXT` -- but never dereferenced by this one-line region. They are
# name-only stubs: the real values are owmeta_core.context.Context /
# ClassContext instances, unrelated machinery this region does not exercise
# (same convention as the SentenceTransformer stub in the sibling example
# JustlyAI__lmss_entity_extractor__..._OntologyClassifier___init__).
BASE_SCHEMA_URL = 'http://schema.openworm.org/2020/07'
BASE_DATA_URL = 'http://data.openworm.org'
DEF_CTX = None
RDF_CONTEXT = None
