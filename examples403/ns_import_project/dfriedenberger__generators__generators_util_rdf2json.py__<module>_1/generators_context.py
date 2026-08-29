# Context shim (see meta.json): stands in for two bindings the extracted
# region cannot resolve on its own.
#
# 1. `ANS`, from dfriedenberger/generators@7bc5db6a5c :
#    generators/util/namespaces.py. There, ANS is populated at IMPORT TIME
#    by SPARQL-querying an external ontology file, `models/assets-0.0.2.ttl`
#    (OntologyReader(...).get_class('#Asset') etc.) -- that file ships with
#    NEITHER the repository nor any published release: verified absent from
#    the full git tree at this commit (`git ls-tree -r` / GitHub API,
#    recursive) and absent from every sdist/wheel of the `artifact-generator`
#    package on PyPI (versions 0.0.1 through 2.0.0, checked). So the
#    ontology's real, published base IRI cannot be recovered -- there is no
#    "faithful" IRI to reproduce, only the real local names (the fragments
#    literally passed to OntologyReader.get_*() in namespaces.py). This is
#    immaterial to the region's own behaviour: ANS's attributes are used only
#    as opaque predicate/class IRIs to walk an RDF graph, and rdf2json.py
#    never returns an IRI in its JSON output (see original.py) -- so any
#    consistent base yields identical observable behaviour, as long as BOTH
#    representations resolve through this SAME shim.
#
# 2. `SparQLWrapper`, verbatim (trimmed to the one thing this region touches,
#    `self.graph`) from dfriedenberger/obse@43d0cc1 : obse/sparql_queries.py
#    -- `obse` is not installed here (ModuleNotFoundError, verified) and its
#    other query methods are not reached by rdf2json.py, so they are left
#    out rather than vendored unused.
from rdflib import Namespace

ANS = Namespace("http://example.org/dfriedenberger/generators/assets#")
__namespaces__ = {"ans": ANS}


class SparQLWrapper:
    def __init__(self, graph):
        self.graph = graph
