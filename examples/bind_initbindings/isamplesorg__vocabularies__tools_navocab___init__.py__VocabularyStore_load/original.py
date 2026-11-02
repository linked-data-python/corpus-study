# Extracted from isamplesorg/vocabularies@a67087996f : tools/navocab/__init__.py
# region: VocabularyStore.load (lines 136-211, stratum bind_initbindings)
# licence of the source repository: see meta.json
import logging
import typing
import rdflib
import rdflib.namespace
import rdflib.plugins.sparql
import logging.config
L = logging.getLogger("navocab")

    def load(
        self,
        source: str,
        voc_uri: str,
        format: str = DEFAULT_FORMAT,
        bindings: typing.Optional[dict] = None,
    ):
        g_loaded = self._g.parse(source, format=format)
        L.info("Navocab.load.source: %s", source)

        test = self._g.namespace_manager.namespaces()
        for prefix, ns_url in test:
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
        loaded_vocabulary = voc_uri
        if loaded_vocabulary is not None:
            L.info("Loaded vocabulary %s", loaded_vocabulary)
            q = (
                VocabularyStore._PFX
                + """SELECT ?extended
            WHERE {
                ?vocabulary rdfs:subPropertyOf ?extended .
            }"""
            )
            qres = self._g.query(q, initBindings={"vocabulary": loaded_vocabulary})
            _extended_vocab = self._result_single_value(qres, abbreviate=False)
            if _extended_vocab is not None:
                L.info("subPropertyOf Extends: %s", _extended_vocab)
                return
            # The extended vocabulary is not specified
            # Figure it by examining the broader concepts for each
            # concept in the loaded vocabulary
            q = (
                VocabularyStore._PFX
                + """SELECT ?s
            WHERE {
                ?child rdf:type skos:Concept .
                ?child skos:broader ?s .
                ?child skos:inScheme ?voc .
            }"""
            )
#            qres = g_loaded.query(q)
            qres = g_loaded.query(q, initBindings={"voc": loaded_vocabulary})
            broader_concepts = self._one_res(qres)
            vocabs = set()
            for c in broader_concepts:
                concept = self.concept(str(c))
                if concept.vocabulary is not None:
                    vocabs.add(concept.vocabulary)
            for vocab in vocabs:
                if str(vocab) != str(loaded_vocabulary):
                    L.info("broader concept Extends: %s", vocab)
                    self._g.add((rdflib.URIRef(loaded_vocabulary), rdfsT("subPropertyOf"), rdflib.URIRef(vocab)))
                    self._g.commit()
            return
        L.warning("Loaded vocabulary does not specify skos:ConceptScheme")
