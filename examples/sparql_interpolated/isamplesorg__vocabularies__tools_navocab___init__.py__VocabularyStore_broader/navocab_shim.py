# Context shim (see meta.json): isamplesorg/vocabularies@a67087996f,
# tools/navocab/__init__.py -- only the VocabularyStore._PFX class attribute
# the region reads by class NAME (not through self), reduced to the minimal
# stand-in that carries it, verbatim from source (tools/navocab/__init__.py:
# 15-22, 60-65):
#
#   NS = {"rdf": ..., "rdfs": ..., "owl": ..., "skos": ..., ...}
#   class VocabularyStore:
#       _PFX = f"""
#   PREFIX skos: <{NS['skos']}>
#   PREFIX owl: <{NS['owl']}>
#   PREFIX rdf: <{NS['rdf']}>
#   PREFIX rdfs: <{NS['rdfs']}>
#   """
#
# original.py imports this to resolve `VocabularyStore._PFX`. translated.ldpy
# does NOT import it: the s{ } prologue is inherited from @prefix declarations
# instead of a concatenated PREFIX header -- see meta.json translation_notes.
NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
}


class VocabularyStore:
    _PFX = f"""
PREFIX skos: <{NS['skos']}>
PREFIX owl: <{NS['owl']}>
PREFIX rdf: <{NS['rdf']}>
PREFIX rdfs: <{NS['rdfs']}>
"""
