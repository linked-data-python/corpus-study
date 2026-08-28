# Extracted from dev365code/iirds-validate@4b3f840df8 : src/iirds/_package.py
# region: subclasses_of (lines 27-39, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

def subclasses_of(graph: Graph, cls) -> frozenset:
    """`cls` plus every class the *package itself* declares beneath it.

    Section 7 lets a package subclass the standard's classes and requires
    consumers to treat instances as the parent. This closure walks only
    the data graph: the SDK bundles no ontology (that file is third-party
    material with its own licence apparatus), so its answer is always a
    subset of a fuller validator's — never a contradiction. Note the
    standard's 1.3 core declares no subclasses of any concrete class, so
    for Topic, Document, Rendition and friends this subset is in fact
    the whole answer.
    """
    return frozenset({cls} | set(graph.transitive_subjects(RDFS.subClassOf, cls)))
