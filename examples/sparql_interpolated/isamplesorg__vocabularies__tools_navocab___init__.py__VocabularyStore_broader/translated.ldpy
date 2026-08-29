# Extracted from isamplesorg/vocabularies@a67087996f : tools/navocab/__init__.py
# region: VocabularyStore.broader (lines 375-400, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import typing
import rdflib
import rdflib.namespace
import rdflib.plugins.sparql

def broader(self, concept: str, v: typing.Optional[str] = None, abbreviate: bool = False) -> list[str]:
    concept = self.expand_name(concept)
    if v is None:
        q = rdflib.plugins.sparql.prepareQuery(
            VocabularyStore._PFX
            + """SELECT ?s
        WHERE {
            ?child skos:broader ?s .
        }"""
        )
        qres = self._g.query(q, initBindings={"child": concept})
    else:
        v = self.expand_name(v)
        q = rdflib.plugins.sparql.prepareQuery(
            VocabularyStore._PFX
            + """SELECT ?s
        WHERE {
            ?s skos:inScheme ?vocabulary .
            ?child skos:broader ?s .
        }"""
        )
        qres = self._g.query(q, initBindings={"vocabulary": v, "child": concept})
    res = []
    # Should only ever be a single broader term in a well constructed taxonomy,
    # but who knows how well these things are constructed?
    return self._one_res(qres, abbreviate=abbreviate)
