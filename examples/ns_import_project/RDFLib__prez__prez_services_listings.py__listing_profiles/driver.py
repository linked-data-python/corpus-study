"""Validation driver for RDFLib__prez__prez_services_listings.py__listing_profiles.

The region is an `async def`: the harness calls a function and compares what
it returns, so each side's coroutine functions are wrapped to run to
completion (asyncio.run) as soon as the module has been executed.  Nothing
else of the harness is touched.

What the region does, and what the call shows:

  * it formats two SPARQL queries with `PROF.Profile`/`prof:Profile` and the
    limit/offset it derives from the page, and sends them through
    `system_repo.send_queries` -- the stub repository records them, and the
    harness compares the repository (an argument) after the call;
  * it reads the graph the repository answers (`fixture.ttl`) for every
    subject typed prof:Profile, WHILE adding to that same graph, and adds
    `a prez:FocusNode` and a `prez:link` literal built from the curie of the
    profile (the real prez `get_curie_id_for_uri`, see prez_context.py);
  * it hands the graph, the selected media type/profile, the headers and
    `prof:Profile` to `return_from_graph`, whose stand-in returns them.

Calls: a first page (3 profiles of 3 namespaces, neighbours that must stay
untouched), a third page of five (the offset), and an answer with no profile
at all (zero solutions: no triple added, queries still sent).
"""
import asyncio
import functools
import inspect
import types
from pathlib import Path

from rdflib import Graph, Literal, URIRef

from rdfeval import harness
from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent

_exec_artefact = harness._exec_artefact


def _runs_to_completion(coroutine_function):
    @functools.wraps(coroutine_function)
    def call(*args, **kwargs):
        return asyncio.run(coroutine_function(*args, **kwargs))
    return call


def _sync_coroutines(path, name):
    ns, out = _exec_artefact(path, name)
    for key, value in list(ns.items()):
        # only the region's own coroutine functions: the stand-in renderer's
        # `return_from_graph` is awaited by the region and must stay one
        if inspect.iscoroutinefunction(value) and value.__module__ == name:
            ns[key] = _runs_to_completion(value)
    return ns, out


harness._exec_artefact = _sync_coroutines


class _Repo:
    """A repository stub: answers a given graph and keeps what it was asked."""

    def __init__(self, answer=None):
        self.answer = answer
        self.queries = []

    async def send_queries(self, rdf_queries, sparql_queries):
        self.queries.append((list(rdf_queries), list(sparql_queries)))
        return self.answer, Graph()


class _Pmts:
    selected = {"mediatype": "text/anot+turtle", "profile": URIRef("https://prez.dev/profile/open")}

    def generate_response_headers(self):
        return {"Link": "<https://prez.dev/profile/open>; rel=profile"}


def _page(limit, page, answer):
    def build():
        system_repo = _Repo(answer())
        data_repo = _Repo()
        params = types.SimpleNamespace(limit=limit, page=page)
        return (data_repo, system_repo, params, _Pmts()), {}
    return build


def _fixture():
    return fixture_graph(HERE / "fixture.ttl")


def _no_profile():
    g = _fixture()
    for s in list(g.subjects(predicate=URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                             object=URIRef("http://www.w3.org/ns/dx/prof/Profile"))):
        g.remove((s, None, None))
    return g


VERDICT = run_pair(
    __file__,
    entry="listing_profiles",
    fixture="fixture.ttl",
    calls=[_page(10, 1, _fixture), _page(5, 3, _fixture), _page(10, 1, _no_profile)],
)
