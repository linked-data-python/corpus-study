"""Validation driver for Mat-O-Lab__ckanext-csvtocsvw__ckanext_csvtocsvw_csvw_parser.py__CSVWtoRDF_add_table_data.

Establishes semantic equivalence of original.py and translated.ldpy.

``add_table_data(self, g)`` is a class method extracted with ``self`` kept
as an explicit first parameter, so the fixture builds a minimal stand-in
object exposing exactly the attributes the region reads: ``self.tables``
(the per-table row/column data as CSVWtoRDF parses it) and ``self.csv_url``.

Every branch the translation touches is exercised by one call, over two
tables:

  - a "GID" column that is always skipped;
  - a numeric column (xsd:double) with a unit, whose string cell also hits
    the French-decimal reformatting branch;
  - a numeric column (xsd:integer) without a unit, addressed with an
    explicit ``csvw:aboutUrl`` predicate;
  - an ``xsd:anyURI`` column, once with several space-separated URIs (RDF
    collection) and once with a single URI;
  - a default (annotation) column, both with and without ``csvw:aboutUrl``,
    exercising the computed-datatype literal (``oa:value``).

A second call (``_make_self_typed``) exercises what the first one cannot
tell apart.  Cells are always ``str`` in the repository
(``parse_csv_from_url_to_list`` applies ``str()`` to each cell), and the
CSVW formats DataStoreTypes produces (boolean, date, dateTime) fall in the
default (annotation) branch, where ``oa:value`` is ``{cell}^^{format}``:

  - columns of format xsd:boolean ("True", "1", ""), xsd:date, xsd:dateTime
    (with and without a time zone), xsd:int ("007"), so that the datatype of
    ``oa:value`` is not always xsd:string and the lexical forms get
    normalised by rdflib;
  - a table with ``csvw:skipRows`` = 2 and ``csvw:headerRowCount`` = 1, so
    that the ``csvw:url`` ``.../row=N`` of each row depends on both terms of
    ``row_num``.

Mutants of translated.ldpy checked in copies, each rejected by this driver:
``oa:value {cell}^^{format}`` -> ``{cell}^^xsd:string``; the
``data["dialect"][csvw:skipRows]`` term removed from ``row_num``; the
``data["dialect"][csvw:headerRowCount]`` term removed; ``if unit:`` ->
``if False:``.
"""
from types import SimpleNamespace

from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import CSVW, XSD

QUDT = Namespace("http://qudt.org/schema/qudt/")


def _make_self():
    table_a = URIRef("http://example.org/tableA")
    table_b = URIRef("http://example.org/tableB")
    return SimpleNamespace(
        csv_url="http://example.org/tableA.csv",
        tables={
            table_a: {
                "about_url": "http://example.org/tableA/row-{GID}",
                "dialect": {CSVW.skipRows: 0, CSVW.headerRowCount: 1},
                "columns": {
                    "gid": {CSVW.name: Literal("GID")},
                    "temp": {
                        CSVW.name: Literal("temperature"),
                        CSVW.format: XSD.double,
                        QUDT.unit: URIRef("http://qudt.org/vocab/unit/DEG_C"),
                    },
                    "count": {
                        CSVW.name: Literal("count"),
                        CSVW.format: XSD.integer,
                        CSVW.aboutUrl: "http://example.org/prop/count-{GID}",
                    },
                    "tags": {
                        CSVW.name: Literal("tags"),
                        CSVW.format: XSD.anyURI,
                    },
                    "note": {
                        CSVW.name: Literal("note"),
                        CSVW.aboutUrl: "http://example.org/prop/note-{GID}",
                    },
                },
                "lines": [
                    ["1", "12.345,6", "42", "http://example.org/tag/a http://example.org/tag/b", "hello world"],
                    ["2", "7", "9", "http://example.org/tag/c", "second row"],
                ],
            },
            table_b: {
                "about_url": "http://example.org/tableB/row-{GID}",
                "dialect": {CSVW.skipRows: 0, CSVW.headerRowCount: 0},
                "columns": {
                    "gid": {CSVW.name: Literal("GID")},
                    "label": {CSVW.name: Literal("label")},
                },
                "lines": [
                    ["x1", "just a label"],
                ],
            },
        },
    )


def _make_self_typed():
    table_c = URIRef("http://example.org/tableC")
    return SimpleNamespace(
        csv_url="http://example.org/tableC.csv",
        tables={
            table_c: {
                "about_url": "http://example.org/tableC/row-{GID}",
                "dialect": {CSVW.skipRows: 2, CSVW.headerRowCount: 1},
                "columns": {
                    "gid": {CSVW.name: Literal("GID")},
                    "flag": {CSVW.name: Literal("flag"), CSVW.format: XSD.boolean},
                    "day": {
                        CSVW.name: Literal("day"),
                        CSVW.format: XSD.date,
                        CSVW.aboutUrl: "http://example.org/prop/day-{GID}",
                    },
                    "ts": {CSVW.name: Literal("ts"), CSVW.format: XSD.dateTime},
                    "n": {CSVW.name: Literal("n"), CSVW.format: XSD.int},
                    "plain": {CSVW.name: Literal("plain")},
                },
                "lines": [
                    ["1", "True", "2020-04-01", "2020-04-01T10:00:00", "007", "a"],
                    ["2", "1", "2021-12-31", "2020-04-01T10:00:00+02:00", "7", ""],
                    ["3", "", "", "", "", "c"],
                ],
            },
        },
    )


from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='add_table_data',
    calls=[
        lambda: ((_make_self(), Graph()), {}),
        lambda: ((_make_self_typed(), Graph()), {}),
    ],
)
