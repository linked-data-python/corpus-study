# Context shim (see meta.json): restores the `g` graph that
# get_bind_tests() builds and closes over before yielding `check` as a
# closure, in bindings/python/tests/rdflib_suite/vendor/test_evaluate_bind.py
# from Blackcat-Informatics/purrdf@3aa4ba514e. The extracted region is only
# `check` itself, which reads the free variable `g` -- restored here so the
# region executes standalone. Identical bindings for both representations.
from rdflib import Graph, Literal, URIRef

base = "http://example.org/"
g = Graph()
g.add((URIRef(base + "thing"), URIRef(base + "ns#comment"), Literal("anything")))
