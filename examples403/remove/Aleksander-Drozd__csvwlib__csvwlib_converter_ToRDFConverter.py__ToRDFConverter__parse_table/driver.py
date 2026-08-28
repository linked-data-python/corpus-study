"""Validation driver for Aleksander-Drozd__csvwlib__…__ToRDFConverter__parse_table.

The region BUILDS a graph (and, in minimal mode, takes one triple back out of
it), so the oracle is RDF isomorphism, as `meta.oracle` says.  `entry` is the
`demo` harness both files carry identically (see meta.json): the region is a
method body lifted out of its class, so `demo` rebuilds the converter, seeds
its graph with `fixture.ttl` and returns the graph the region wrote.

Three calls:

  1. minimal mode -- the `remove` site.  `_parse_row` adds
     `(dummy, csvw:describes, row_node)` for each of the two rows and the
     region removes both; what must survive is the seeded neighbourhood, which
     carries `csvw:describes` triples of its own.
  2. standard mode on the same table -- the `remove` branch is not taken and
     the three `graph.add` of the head become one `+{ … ; … }`.
  3. standard mode on a table without '@id', so `table_node` is a blank node
     rather than a URIRef -- the other side of the region's first line.
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph

HERE = Path(__file__).resolve().parent

TABLE_METADATA = {
    '@id': 'http://example.org/tables/people',
    'url': 'http://example.org/tables/people.csv',
    'tableSchema': {
        'columns': [{'name': 'name', 'titles': 'name'},
                    {'name': 'age', 'titles': 'age'}],
    },
}

# same table, without '@id': the region falls back to a blank node
ANONYMOUS_TABLE_METADATA = {k: v for k, v in TABLE_METADATA.items()
                            if k != '@id'}

TABLE_DATA = {
    'columns': [{'name': 'name'}, {'name': 'age'}],
    'rows': [
        {'number': 1, '@id': 'http://example.org/tables/people.csv#row=2',
         'url': 'http://example.org/tables/people.csv#row=2', 'cells': {}},
        {'number': 2, '@id': 'http://example.org/tables/people.csv#row=3',
         'url': 'http://example.org/tables/people.csv#row=3', 'cells': {}},
    ],
}


def case(mode, table_metadata):
    """A fresh neighbourhood graph per side: the region writes into it."""
    return lambda: ((mode, table_metadata, TABLE_DATA,
                     fixture_graph(HERE / "fixture.ttl")), {})


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        case('minimal', TABLE_METADATA),
        case('standard', TABLE_METADATA),
        case('standard', ANONYMOUS_TABLE_METADATA),
    ],
)
