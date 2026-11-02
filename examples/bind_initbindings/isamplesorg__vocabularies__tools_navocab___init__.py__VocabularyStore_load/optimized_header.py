# Extracted from isamplesorg/vocabularies@a67087996f : tools/navocab/__init__.py
# region: VocabularyStore.load (lines 136-211, stratum bind_initbindings)
# licence of the source repository: see meta.json
import logging
import typing
import rdflib
L = logging.getLogger("navocab")
import vocabulary_context
from vocabulary_context import DEFAULT_FORMAT, rdfsT

# Restored class statement (see vocabulary_context.py): the region is a method.
class VocabularyStore(vocabulary_context.VocabularyStore):

    def load(
        self,
        source: str,
        voc_uri: str,
        format: str = DEFAULT_FORMAT,
        bindings: typing.Optional[dict] = None,
    ):
        g_loaded = self._g.parse(source, format=format)
        L.info("Navocab.load.source: %s", source)

        for prefix, ns_url in self._g.namespace_manager.namespaces():
            print(f"{prefix}: {ns_url}")
            self._g.bind(prefix, ns_url)

        if bindings is not None:
            for k, v in bindings.items():
                L.debug("binding item k: %", k)
                L.debug("binding item v: %", v)
                self._g.bind(k, v)
        # Figure the broader concept vocabularies.
        # First check for extension_vocab rdfs:subPropertyOf extended_vocab
        # if not present, then compute and add it for later use.
        # What vocabulary did we just load?
        #        q = (
        #           VocabularyStore._PFX
        #            + """SELECT ?s
        #        WHERE {
        #            ?s rdf:type skos:ConceptScheme .
        #        }"""
        #       )
        # this query will return multiple values if more than one vocab has been loaded
        #        qres = g_loaded.query(q)
#        loaded_vocabulary = self._result_single_value(qres, abbreviate=False)
        if voc_uri is not None:
            L.info("Loaded vocabulary %s", voc_uri)
            qres = self._g.query(self._PFX + """SELECT ?extended
            WHERE {
                ?vocabulary rdfs:subPropertyOf ?extended .
            }""", initBindings={"vocabulary": voc_uri})
            _extended_vocab = self._result_single_value(qres, abbreviate=False)
            if _extended_vocab is not None:
                L.info("subPropertyOf Extends: %s", _extended_vocab)
                return
            # The extended vocabulary is not specified
            # Figure it by examining the broader concepts for each
            # concept in the loaded vocabulary
#            qres = g_loaded.query(q)
            broader_concepts = self._one_res(g_loaded.query(self._PFX + """SELECT ?s
            WHERE {
                ?child rdf:type skos:Concept .
                ?child skos:broader ?s .
                ?child skos:inScheme ?voc .
            }""", initBindings={"voc": voc_uri}))
            for vocab in {self.concept(str(c)).vocabulary for c in broader_concepts} - {None}:
                if str(vocab) != str(voc_uri):
                    L.info("broader concept Extends: %s", vocab)
                    self._g.add((rdflib.URIRef(voc_uri), rdfsT("subPropertyOf"), rdflib.URIRef(vocab)))
                    self._g.commit()
            return
        L.warning("Loaded vocabulary does not specify skos:ConceptScheme")


# driver helper (see vocabulary_context.py) -- not part of the extracted region.
def _load(g, *args, fixed_concept=False, **kwargs):
    store = VocabularyStore(g)
    if fixed_concept:
        store.concept = vocabulary_context.uri_concept(store)
    return store.load(*args, **kwargs)
