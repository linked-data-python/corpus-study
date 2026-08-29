# Context shim (see meta.json): the region's module preamble is
#     g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v6_8_0.ttl")
# where HERE is a module global of landscape/07-tooling/build_page_v6_9_0.py
# (altunelyusuf/SemanticTechnologies@bad0fa7c46).  Neither HERE nor the ABox
# is part of the extracted region, and the ABox is not vendored here, so this
# shim points HERE at this directory, which holds a minimal stand-in ABox with
# the rdfs:label / skos:definition / skos:note / skos:scopeNote statements the
# region redefines.  `replay` holds the calls the module makes to redefine()
# further down the file (also outside the region), so that the mutation of the
# module-level graph is observable.  Identical bindings for both
# representations; excluded from the surface metrics.
import os

from rdflib import Namespace

HERE = os.path.dirname(os.path.abspath(__file__))

SEMTECH = Namespace("https://altunelyusuf.github.io/SemanticTechnologies/07-tooling#")


def replay(redefine):
    """Exercise every branch of redefine() against the stand-in ABox.

    Protege has two rdfs:label values (the wildcard removal must take both),
    a definition, a note and a scope note; GraphDB has no skos:definition (the
    removal matches nothing); NewThing is not in the graph at all; and the
    bare call leaves everything alone.
    """
    redefine(SEMTECH.Protege,
             label="Protégé",
             defn="An ontology editor maintained by Stanford.",
             note="Desktop and web versions.",
             scope="Restricted to the tooling landscape.")
    redefine(SEMTECH.GraphDB, defn="An RDF database with reasoning.")
    redefine(SEMTECH.GraphDB)
    redefine(SEMTECH.NewThing, label="Not yet described")
