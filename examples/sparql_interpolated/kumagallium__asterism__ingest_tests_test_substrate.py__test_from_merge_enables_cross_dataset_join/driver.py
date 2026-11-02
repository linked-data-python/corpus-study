"""Validation driver for test_from_merge_enables_cross_dataset_join.

The region is a test with no parameter and no return value: its whole effect
is two `assert`s over two queries on a Dataset in which the join `?s madeOf ?e .
?e rdfs:label ?l` has its two facts in two different named graphs (no fixture:
the test builds its own Dataset).  Run as it stands it returns None on both
sides, which proves "does not raise" and nothing else.  So each call below
changes ONE thing the test depends on -- installed in the child process, just
before the call, by the call's own `_make` -- and the outcome (None, or the
exception) is what is compared; the Dataset subclass also prints the rows of
every query it receives, so stdout shows what each query returned:

  * genuine: `asterism.substrate` untouched, plain Dataset -> None; prints no
    row for the query without FROM, the one row "Bismuth" for the FROM query;
  * default_union=True: the query WITHOUT FROM already sees the join, so
    `assert none == []` fails (this is the call that exercises the s{ } query:
    a translation whose pattern matched nothing would let the test pass);
  * canonical_from_clauses patched to emit only FROM <g_a>, only FROM <g_b>, FROM
    NAMED for both, or nothing: the second assert fails;
  * canonical_graph_iri patched so both datasets share one graph: the join
    then lives in a single graph and the FROM query resolves with one clause.
"""
from rdfeval.harness import run_pair


def _patch(*, union=False, clauses=None, graph_iri=None):
    """Install, in this process, the variant the next call runs against."""
    import rdflib
    import asterism.substrate as sub

    if not hasattr(sub, "_genuine"):
        sub._genuine = (sub.canonical_from_clauses, sub.canonical_graph_iri)
        rdflib._genuine_dataset = rdflib.Dataset
    sub.canonical_from_clauses, sub.canonical_graph_iri = sub._genuine
    if clauses is not None:
        sub.canonical_from_clauses = clauses
    if graph_iri is not None:
        sub.canonical_graph_iri = graph_iri

    class ShowingDataset(rdflib._genuine_dataset):
        def __init__(self, *a, **kw):
            super().__init__(*a, default_union=union, **kw)

        def query(self, *a, **kw):
            res = super().query(*a, **kw)
            print("rows:", sorted(str(r[0]) for r in res))
            return res

    rdflib.Dataset = ShowingDataset


def variant(**kw):
    def _make():
        _patch(**kw)
        return (), {}
    return _make


def only(i):
    return lambda graphs, **k: f"FROM <{graphs[i]}>\n"


VERDICT = run_pair(
    __file__,
    entry='test_from_merge_enables_cross_dataset_join',
    calls=[
        variant(),
        variant(union=True),
        variant(clauses=only(0)),
        variant(clauses=only(1)),
        variant(clauses=lambda graphs, **k: "".join(f"FROM NAMED <{g}>\n" for g in graphs)),
        variant(clauses=lambda graphs, **k: ""),
        variant(graph_iri=lambda ds_id: "https://ex/graph/shared",
                clauses=lambda graphs, **k: f"FROM <{graphs[0]}>\n"),
    ],
)
