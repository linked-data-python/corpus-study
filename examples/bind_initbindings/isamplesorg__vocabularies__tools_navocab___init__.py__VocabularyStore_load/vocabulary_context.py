# Context shim (see meta.json): the parts of tools/navocab/__init__.py in
# isamplesorg/vocabularies@a67087996f that the extracted `VocabularyStore.load`
# needs, so that it executes outside the package. Everything below is copied
# VERBATIM from that file, except `VocabularyStore.__init__` (upstream opens an
# SQLAlchemy/SQLite store, which is not installed; here the store is any rdflib
# graph, passed in), the absence of `load` itself (the region), and of the
# methods nothing in the region reaches. `uri_concept` at the end is NOT
# upstream: see its docstring. Identical bindings for both representations.
import dataclasses
import logging
import typing
import rdflib
import rdflib.namespace
import rdflib.plugins.sparql
import logging.config

NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "obo": "http://purl.obolibrary.org/obo/",
    "geosciml": "http://resource.geosciml.org/classifier/cgi/lithology",
}



L = logging.getLogger("navocab")

def skosT(term):
    return rdflib.URIRef(f"{NS['skos']}{term}")


def rdfT(term):
    return rdflib.URIRef(f"{NS['rdf']}{term}")


def rdfsT(term):
    return rdflib.URIRef(f"{NS['rdfs']}{term}")


@dataclasses.dataclass
class VocabularyConcept:
    uri: str
    name: str
    label: list[str]
    definition: str
    broader: list[str]
    narrower: list[str]
    vocabulary: str


@dataclasses.dataclass
class Vocabulary:
    uri: str
    label: str
    description: str
    extends: typing.Optional[str] = None


class VocabularyStore:
    _PFX = f"""
PREFIX skos: <{NS['skos']}>
PREFIX owl: <{NS['owl']}>
PREFIX rdf: <{NS['rdf']}>
PREFIX rdfs: <{NS['rdfs']}>
"""
    DEFAULT_FORMAT = "text/turtle"
    DEFAULT_STORE = "sqlite://"

    def __init__(self, g):
        self._g = g

    def expand_name(self, n: typing.Optional[str]) -> typing.Optional[str]:
        if n is None:
            return n
        try:
            return self._g.namespace_manager.expand_curie(n)
        except (ValueError, TypeError):
            pass
        return n

    def compact_name(self, n:typing.Optional[str]) -> typing.Optional[str]:
        if n is None:
            return n
        try:
            return rdflib.URIRef(n).n3(self._g.namespace_manager)
        except (ValueError, TypeError):
            pass
        return n

    def _one_res(self, rows, abbreviate=False) -> list[str]:
        res = []
        for r in rows:
            if abbreviate:
                res.append(self.compact_name(r[0]))
            else:
                res.append(r[0])
        return res

    def _result_single_value(self, rows, abbreviate=False) -> typing.Any:
        L.debug(f"result_single_value-count rows in query result: {len(rows)}")
        for r in rows:
            L.debug(f"VocabularyStore-result single value row: {self.compact_name(r[0])}")
        for r in rows:
            if abbreviate:
                return self.compact_name(r[0])
            return r[0]
        return None


    def objects(self, subject: str, predicate: str) -> list[str]:
        q = rdflib.plugins.sparql.prepareQuery(
            VocabularyStore._PFX
            + """SELECT ?o
        WHERE {
            ?subject ?predicate ?o .
        }"""
        )
        qres = self._g.query(
            q, initBindings={"subject": subject, "predicate": predicate}
        )
        res = []
        for row in qres:
            v = row[0]
            v = str(v).strip()
            if len(v) > 0:
                res.append(v)
        return res

    def narrower(
        self, concept: str, v: typing.Optional[str] = None, abbreviate: bool = False
    ) -> list[str]:
        concept = self.expand_name(concept)
        if v is None:
            q = rdflib.plugins.sparql.prepareQuery(
                VocabularyStore._PFX
                + """SELECT ?s
            WHERE {
                ?s skos:broader ?parent .
            }"""
            )
            qres = self._g.query(q, initBindings={"parent": concept})
        else:
            v = self.expand_name(v)
            q = rdflib.plugins.sparql.prepareQuery(
                VocabularyStore._PFX
                + """SELECT ?s
            WHERE {
                ?s skos:inScheme ?vocabulary .
                ?s skos:broader ?parent .
            }"""
            )
            qres = self._g.query(q, initBindings={"vocabulary": v, "parent": concept})
        return self._one_res(qres, abbreviate=abbreviate)

    def concept(self, term: str):
        term = self.expand_name(term)
        if "#" in term:
            ab = term.split("#")
        else:
            ab = term.split("/")
        name = ab[-1]
        # _v = self.objects(term, skosT("inScheme"))[0]
        _v = None
        labels = self.objects(term, skosT("prefLabel"))
        labels += self.objects(term, skosT("label"))
        tmp = self.objects(term, skosT("definition"))
        definition = "\n".join(tmp)
        broader = self.objects(term, skosT("broader"))
        narrower = self.narrower(term, _v)
        vocabulary = self.objects(term, skosT("inScheme"))
        if len(vocabulary) >0:
            vocabulary = vocabulary[0]
        else:
            vocabulary = None
        return VocabularyConcept(
            uri=str(term),
            name=name,
            label=labels,
            definition=definition.strip(),
            broader=broader,
            narrower=narrower,
            vocabulary = vocabulary
        )


DEFAULT_FORMAT = VocabularyStore.DEFAULT_FORMAT   # a bare name in the signature of `load` (class scope upstream)


def uri_concept(store):
    """A `concept(term)` for `store` that finds the vocabulary of a concept.

    NOT upstream. `VocabularyStore.concept` looks its data up through
    `objects()`, which binds the concept as a plain `str` in `initBindings`;
    rdflib never matches a `str` against a URIRef, so upstream `concept()`
    always answers `vocabulary=None` and the branch of `load` that adds
    `rdfs:subPropertyOf` is unreachable through it. The driver installs this
    function as `store.concept` to make that branch reachable (the call with
    the real `concept` is kept too).
    """
    def concept(term):
        t = rdflib.URIRef(term)
        found = list(store._g.objects(t, skosT("inScheme")))
        return VocabularyConcept(
            uri=str(t), name=str(t).split("/")[-1], label=[], definition="",
            broader=[], narrower=[],
            vocabulary=found[0] if found else None)
    return concept
