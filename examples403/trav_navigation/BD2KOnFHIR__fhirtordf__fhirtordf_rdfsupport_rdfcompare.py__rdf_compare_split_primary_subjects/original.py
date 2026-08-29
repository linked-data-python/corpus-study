# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df9f322c148b7f20ebbd6d58cb92cefc : fhirtordf/rdfsupport/rdfcompare.py
# region: rdf_compare_split.primary_subjects (lines 126-129, stratum trav_navigation)
# licence of the source repository: see meta.json
from typing import Optional, List, Set, Callable, Tuple
from rdflib import URIRef, Graph, OWL, RDF, BNode
from rdflib.term import Node

def primary_subjects(g: Graph) -> Set[Node]:
    anon_subjs = set(anon_s for anon_s in g.subjects()
                     if isinstance(anon_s, BNode) and len([g.subject_predicates(anon_s)]) == 0)
    return set(s_ for s_ in g1.subjects() if isinstance(s_, URIRef)).union(anon_subjs)


# Context restoration (see meta.json): confirmed against the upstream source
# (github.com/BD2KOnFHIR/fhirtordf/blob/05b23ba1df9f322c148b7f20ebbd6d58cb92cefc/
# fhirtordf/rdfsupport/rdfcompare.py#L114-L129), `primary_subjects` is nested
# inside `rdf_compare_split(g1, g2, ...)` and its return line reads the free
# variable `g1` from that enclosing scope instead of its own parameter `g` --
# a real, confirmed bug in the source, not an artefact of extraction.
# Extraction as a standalone function severs the closure, so `g1` would
# otherwise be an unresolved name. We restore the SAME binding the closure
# has at the call site `primary_subjects(g1)` (the first of the two calls
# `rdf_compare_split` makes) -- the OTHER call site, `primary_subjects(g2)`,
# is where the bug actually bites (it silently mixes subjects from `g1` into
# a result nominally about `g2`), and a single-argument extraction has no way
# to exercise two graphs through one parameter; see meta.json.
# The 4 lines above are the region, untouched; this wrapper only sets the
# module global before calling them, so it is testable.
g1: Graph = None


def run_primary_subjects(g: Graph) -> Set[Node]:
    global g1
    g1 = g
    return primary_subjects(g)
