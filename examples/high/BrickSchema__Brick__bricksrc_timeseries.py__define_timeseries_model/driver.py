"""Validation driver: define_timeseries_model mutates the graph it receives."""
from rdflib import Graph

from rdfeval.harness import run_pair


def fresh_graph():
    return ((Graph(),), {})


VERDICT = run_pair(__file__, entry="define_timeseries_model",
                   calls=[fresh_graph])
