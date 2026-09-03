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


from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='add_table_data',
    calls=[lambda: ((_make_self(), Graph()), {})],
)
