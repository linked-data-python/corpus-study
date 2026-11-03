# Extracted from isamplesorg/vocabularies@a67087996f : tools/navocab/__init__.py
# region: VocabularyStore.narrower (lines 402-426, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import typing
import rdflib
import rdflib.namespace
import rdflib.plugins.sparql
from navocab_shim import VocabularyStore  # context shim, see meta.json

def narrower(
    self, concept: str, v: typing.Optional[str] = None, abbreviate: bool = False
) -> list[str]:
    concept = self.expand_name(concept)
    if v is None:
        qres = self._g.query(VocabularyStore._PFX + "SELECT ?s WHERE { ?s skos:broader ?parent . }",
                             initBindings={"parent": concept})
    else:
        qres = self._g.query(
            VocabularyStore._PFX
            + "SELECT ?s WHERE { ?s skos:inScheme ?vocabulary . ?s skos:broader ?parent . }",
            initBindings={"vocabulary": self.expand_name(v), "parent": concept})
    return self._one_res(qres, abbreviate=abbreviate)
