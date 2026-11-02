# Context shim (see meta.json): `CompiledExpander` (kindynsyn/synthesizer/
# synthesizer.py) and `prepare_query` (kindynsyn/rdflib_tools/helpers.py),
# copied verbatim from comp-rob2b/kindyngen@414ebd52b2, so the extracted
# `TreeExpander.expand` executes outside the package: its signature
# annotation names CompiledExpander, and the driver builds the expanders it
# stores in the result. Identical bindings for both representations.
import typing

from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.sparql import Query


def prepare_query(sparql_str, base={}, initNs={}):
    """
    Pre-compile a SPARQL query so that it executes faster.
    """
    return translateQuery(parseQuery(sparql_str), base=base, initNs=initNs)


class SweepConfig:
    """Only named by the annotation of CompiledExpander.append upstream."""


class Traverser:
    """Only named by the annotation of CompiledExpander.append upstream."""


class CompiledExpander:
    def __init__(self, query: str):
        self.compiled: Query = prepare_query(query)
        self.traversers: dict[SweepConfig, list[Traverser]] = {}

    def append(self, sweep: SweepConfig, traverser: Traverser):
        if sweep not in self.traversers:
            self.traversers[sweep] = []
        self.traversers[sweep].append(traverser)
