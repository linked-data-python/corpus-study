"""Validation driver for aminedouiri__knowledge-formalization-web-application__apps_visualisation_views.py__visualisation.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each Turtle file is parsed fresh by each side.

`visualisation` parses six ontology files, one per query (see the six
`*_path` parameters added to restore that binding — meta.json), so `calls`
is custom rather than the single-graph-argument convention `fixture=` builds.
Three calls:

  call[0]  all six paths -> fixture.ttl, one file holding instances of every
           tracked class except :Domaine (the zero-solution case for that
           query) and a little neighbourhood.  It proves each of the six
           PATTERNS, but not which graph each query runs on: the six graphs
           have the same content.

  call[1]  each path -> its own file, fixture_<name>.ttl.  Each file holds
           instances of its own class (:Domaine included, two of them) and,
           as neighbours, one instance of each of the five other tracked
           classes, the class reached through rdfs:seeAlso instead of
           rdf:type, and a same-local-name class in another namespace.  A
           query run on another of the six graphs (the `(g)` call suffix
           pointed at the wrong graph), a file parsed into the wrong graph,
           a class swapped, or `a` widened to a variable changes the result.

  call[2]  all six paths -> fixture_empty.ttl: no subject has a tracked
           class, so every query yields zero rows and every list is empty.

All three return render()'s context dict (context.py); `print(strategies)`
is compared through stdout.  The real viz_*.ttl files of the repository
hold only their four @prefix lines, `:` bound to http://dig.isi.edu/ as in
every fixture here.
"""
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
NAMES = ("tache", "activite", "historique", "phenomene", "domaine", "strategie")


def call_all(fixture):
    path = str(HERE / fixture)
    return lambda: ((None,), {f"{n}_path": path for n in NAMES})


def call_each():
    return lambda: ((None,), {f"{n}_path": str(HERE / f"fixture_{n}.ttl")
                              for n in NAMES})


VERDICT = run_pair(
    __file__,
    entry='visualisation',
    calls=[
        call_all("fixture.ttl"),
        call_each(),
        call_all("fixture_empty.ttl"),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
    ordered=False,
)
