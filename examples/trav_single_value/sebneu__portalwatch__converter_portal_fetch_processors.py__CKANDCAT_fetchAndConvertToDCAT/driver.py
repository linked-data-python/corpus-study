"""Validation driver for
sebneu__portalwatch__converter_portal_fetch_processors.py__CKANDCAT_fetchAndConvertToDCAT.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side and is what `graph`
already holds before the call -- but the traversal pattern this region reads
(hydra pagination, then dcat:Dataset subjects) does not live in the graph it
is handed: it lives in what `graph.parse(portal_api, ...)` and the pagination
loop *fetch*.  `fetchAndConvertToDCAT` never touches the network here: the
"fetch" is `graph.parse()` given a local file path or a file: IRI, which
rdflib treats like any other input source, so `portal_api` and
`hydra:nextPage` point at files on disk instead of URLs.

The region decides three reads, each a `.first()` in the translation:

  R1  cur       = ?s a hydra:PagedCollection            (in `graph`)
  R2  next_page = {cur} hydra:nextPage ?v               (in `graph`)
  R3  next_page = {URIRef(next_page)} hydra:nextPage ?v (in `g`, the page
                                                         just fetched)

and a final loop over `?d a dcat:Dataset`.  What the region produces is the
final state of `graph` (compared by isomorphism, rdfeval.harness
_compare_value), the calls it makes to quality.add_quality_measures, and the
debug log of how many pages it walked.  Two SEAMS, set here and identical
for both sides, make the last two observable:

  * quality.add_quality_measures is the context shim's no-op; the driver
    replaces it with a recorder that writes `(d, probe:qualityMeasured,
    activity)` into `graph` -- the real function also writes DQV triples into
    `graph` while the loop iterates it (quality.py:46 in the repository), so
    the recorder keeps that shape.  A mutant that empties, widens or narrows
    the final loop changes the graph.
  * the module loggers (`__original__`, `__translated__`) get a handler that
    prints each record to the stdout the harness captures per call, so
    'Total pages:N' is compared.

The real input shape: ckanext-dcat's catalog endpoint (not in the corpus
clones; its `_add_pagination_triples`) writes the page as
`<current-page-url> a hydra:PagedCollection ; hydra:nextPage "next-url"`:
the next page is a plain LITERAL, and the subject of each page is the page's
own URL.  The pages of the calls marked [real shape] follow it; they are
generated into a temporary directory at import time (removed at exit),
because their subjects and literals must be absolute file: IRIs.

Calls, and what each one decides:

  0 with_pagination (static fixtures) -- page1's nextPage is an IRI to
    page2, page2 has no nextPage: R1, R2 one solution each, R3 ZERO
    solutions; final loop two dcat:Dataset.
  1 no_pagination (static fixture) -- a PagedCollection with no nextPage:
    R2 zero solutions, the while loop never runs; final loop zero solutions.
  2 chain3 [real shape] -- three pages linked by LITERAL nextPage: R3 has ONE
    solution (the only call where it has one: removing R3, dropping its
    `(g)`, or interpolating `{next_page}` bare loses page 3), then on page 3
    R3 yields the falsy literal "" and the loop stops.  Each page puts, BEFORE
    the decisive node, a neighbour that shares two of the three terms and
    whose visit would be visible (it points at a decoy page that holds its
    own dcat:Dataset), so a widened pattern's `.first()` lands on it:
      page 1, R1: `ex:coll a hydra:Collection` (same predicate) and
              `ex:link ex:kind hydra:PagedCollection` (same object);
      page 1, R2: `ex:coll hydra:nextPage "decoy"` (same predicate) and
              `<P1> hydra:previousPage "decoy"` (same subject);
      page 2, R3: `ex:other hydra:nextPage "decoy"` (same predicate) and
              `<P2> hydra:previousPage "decoy"` (same subject).
  3 two_solutions [real shape] -- page 1 holds TWO PagedCollection subjects,
    the first of which has TWO nextPage literals, and the page they lead to
    has TWO nextPage literals: R1, R2 and R3 each have several solutions.
    `graph.value` takes the first match and never raises; `.first()` must do
    the same (`.one()` would raise ValueError).  Both walk graph.triples() in
    the same store order, so the choice is the same on both sides and is
    visible in which pages got merged.
  4 no_collection [real shape] -- no hydra:PagedCollection at all, but a
    hydra:nextPage triple on an unrelated subject: R1 zero solutions, so cur
    is None.  `graph.value(subject=None, predicate=...)` returns None without
    looking; the translation's `{cur}` must not turn into a wildcard that
    finds the neighbour (`?q hydra:nextPage ?v` would follow it).

`self` is unused by the region (never read through it), so `None` stands in.
`portal_ref` / `snapshot` are opaque to the region; `activity` only reaches
quality.add_quality_measures, whose recorder writes it into the graph.
"""
import atexit
import logging
import shutil
import sys
import tempfile
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import quality  # noqa: E402 - the context shim both sides import
from rdflib import Literal, URIRef  # noqa: E402

PROBE = "http://example.org/probe#"


def _record_quality(dataset_uri, graph, act):
    """Seam: the no-op shim made visible, the same on both sides."""
    graph.add((dataset_uri, URIRef(PROBE + "qualityMeasured"), Literal(act)))


quality.add_quality_measures = _record_quality


class _ToCurrentStdout(logging.Handler):
    """Print each record to whatever sys.stdout is at emit time: the
    per-call buffer of the harness."""

    def emit(self, record):
        print(f"{record.levelname}:{record.getMessage()}")


for _name in ("__original__", "__translated__"):
    _logger = logging.getLogger(_name)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(_ToCurrentStdout())
    _logger.propagate = False


# --- generated pages [real shape]: absolute file: IRIs ----------------------
_TMP = Path(tempfile.mkdtemp(prefix="portalwatch_pages_"))
atexit.register(shutil.rmtree, _TMP, True)

_PREFIXES = """\
@prefix hydra: <http://www.w3.org/ns/hydra/core#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix ex: <http://example.org/> .
"""
_NAMES = ("c1", "c2", "c3", "d1", "d2", "d3", "d4", "t1", "t2a", "t2b",
          "t2c", "t3a", "t3b", "n1", "n2")
_IRI = {k: (_TMP / f"{k}.ttl").as_uri() for k in _NAMES}


def _page(name, body):
    path = _TMP / f"{name}.ttl"
    path.write_text(_PREFIXES + body.format(**_IRI))
    return str(path)


# decoys: a page whose merge into `graph` shows it was (wrongly) visited
for _d in ("d1", "d2", "d3", "d4", "t2b", "t2c", "t3b", "n2"):
    _page(_d, f"ex:ds_{_d} a dcat:Dataset .\n")

# call 2: three pages, LITERAL links, neighbours before the decisive node
_page("c1", """
ex:coll a hydra:Collection ;
    hydra:nextPage "{d1}" .
ex:link ex:kind hydra:PagedCollection .
<{c1}> hydra:previousPage "{d2}" .
<{c1}> a hydra:PagedCollection ;
    hydra:nextPage "{c2}" .
ex:ds_c1 a dcat:Dataset .
""")
_page("c2", """
ex:other hydra:nextPage "{d3}" .
<{c2}> hydra:previousPage "{d4}" .
<{c2}> a hydra:PagedCollection ;
    hydra:nextPage "{c3}" .
ex:ds_c2 a dcat:Dataset .
""")
_page("c3", """
<{c3}> a hydra:PagedCollection ;
    hydra:nextPage "" .
ex:ds_c3 a dcat:Dataset .
ex:noise_c3 a ex:NotADataset .
""")

# call 3: several solutions for R1, R2 and R3
_page("t1", """
<{t1}> a hydra:PagedCollection ;
    hydra:nextPage "{t2a}", "{t2b}" .
ex:second a hydra:PagedCollection ;
    hydra:nextPage "{t2c}" .
ex:ds_t1 a dcat:Dataset .
""")
_page("t2a", """
<{t2a}> a hydra:PagedCollection ;
    hydra:nextPage "{t3a}", "{t3b}" .
ex:ds_t2a a dcat:Dataset .
""")
_page("t3a", "ex:ds_t3a a dcat:Dataset .\n")

# call 4: no PagedCollection, a nextPage on an unrelated subject
_page("n1", """
ex:unrelated hydra:nextPage "{n2}" .
ex:ds_n1 a dcat:Dataset .
""")


def _call(portal_api):
    # `graph` (from fixture.ttl) is parsed fresh per side, as usual; the
    # other arguments are strings, equal by value on both sides.
    def make():
        graph = fixture_graph(HERE / "fixture.ttl")
        return (
            (None, graph, "test-portal", portal_api, "test-snapshot",
             "test-activity"),
            {},
        )
    return make


VERDICT = run_pair(
    __file__,
    entry='fetchAndConvertToDCAT',
    fixture="fixture.ttl",
    calls=[
        _call(str(HERE / "fixture_ckan_page1.ttl")),
        _call(str(HERE / "fixture_ckan_page1_nopagination.ttl")),
        _call(str(_TMP / "c1.ttl")),
        _call(str(_TMP / "t1.ttl")),
        _call(str(_TMP / "n1.ttl")),
    ],
    # The region returns None; what is compared is the final state of
    # `graph` (isomorphism), the other arguments, and the per-call stdout
    # (the log records, through the handler above).  No order is imposed.
)
