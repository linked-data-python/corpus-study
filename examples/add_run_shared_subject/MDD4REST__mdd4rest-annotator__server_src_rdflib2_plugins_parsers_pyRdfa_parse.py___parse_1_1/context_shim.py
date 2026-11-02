# Context shim (see meta.json): subset of the pyRdfa execution context from
# MDD4REST/mdd4rest-annotator@c46839aa3d, so the region of
# server/src/rdflib2/plugins/parsers/pyRdfa/parse.py (_parse_1_1) executes
# outside the package. Identical bindings for both representations.
#
# `ns_rdf` is the rdf: namespace as pyRdfa defines it. `state` carries only
# the five members the region calls (pyRdfa's ExecutionContext keeps the
# collected rdf:List material in its own structures; here it is a plain
# mapping property -> values, None standing for "initiated, never filled").
from rdflib import BNode, Graph, Literal, Namespace, URIRef

ns_rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")


class _State:
    def __init__(self, origin, lists):
        self.new_list = True
        self._origin = origin
        self._lists = lists

    def list_empty(self):
        return not self._lists

    def get_list_props(self):
        return list(self._lists)

    def get_list_value(self, prop):
        return self._lists[prop]

    def get_list_origin(self):
        return self._origin


EX = Namespace("http://example.org/")

graph = Graph()
# a triple that is already there, and must stay
graph.add((EX.doc, EX.title, Literal("a document")))

state = _State(
    EX.doc,
    {
        # initiated by <... rel="prop" inlist> but never filled: rdf:nil
        EX.emptyList: None,
        # a one-element list
        EX.oneItem: [URIRef("http://example.org/a")],
        # several elements of all kinds: IRI, language literal, blank node
        EX.manyItems: [
            URIRef("http://example.org/b"),
            Literal("deux", lang="fr"),
            BNode("inner"),
        ],
    },
)
