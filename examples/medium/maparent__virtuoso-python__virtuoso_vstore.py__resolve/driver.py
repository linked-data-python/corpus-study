"""Validation driver: resolve() maps a Virtuoso value tuple to an RDF node.

`resolver` is a pyodbc cursor, used only in the DV_IRI_ID branch (one SQL
round-trip); the driver supplies a recording stub.  The other fixtures walk
every dvtype branch of the dispatch, using the real Virtuoso type codes
(pyodbc_constants.py, transcribed from the project's own pyodbc patch).
"""
import pyodbc_constants as pyodbc

from rdfeval.harness import run_pair

# NB: str, not bytes.  The region compares dtype with XSD["gYear"].encode()
# — Python-2 era code, where pyodbc handed back bytes.  Under rdflib 7 a
# bytes datatype makes Literal() raise, so the truncation branches can no
# longer be reached at all (identically on both sides); the fixtures below
# still evaluate the comparison, which is what the translation changed.
XSD_GYEAR = "http://www.w3.org/2001/XMLSchema#gYear"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"


class StubCursor:
    """Stand-in for the pyodbc cursor: answers __ro2sq() with a fixed IRI."""

    def __init__(self, answer):
        self.answer = answer
        self.queries = []

    def execute(self, q):
        self.queries.append(q)

    def fetchone(self):
        return (self.answer,)

    def __eq__(self, other):
        return self.queries == other.queries and self.answer == other.answer


def _tuple(value, dvtype, dttype=0, flag=0, lang=None, dtype=None):
    return (value, dvtype, dttype, flag, lang, dtype)


def not_a_tuple():
    return ((None, 42), {})


def iri_id():
    return ((StubCursor("http://example.org/thing"),
             _tuple(1234, pyodbc.VIRTUOSO_DV_IRI_ID)), {})


def iri_id_bnode():
    return ((StubCursor("nodeID://b10102030405060708"),
             _tuple(1234, pyodbc.VIRTUOSO_DV_IRI_ID)), {})


def rdf_typed():
    return ((None, _tuple("42", pyodbc.VIRTUOSO_DV_RDF, dtype=XSD_STRING)), {})


def rdf_gyear():
    """Reaches the xsd:gYear comparison (see the note on XSD_GYEAR above)."""
    return ((None, _tuple("2020-01-01", pyodbc.VIRTUOSO_DV_RDF,
                          dtype=XSD_GYEAR)), {})


def rdf_lang():
    return ((None, _tuple("bonjour", pyodbc.VIRTUOSO_DV_RDF, lang="fr")), {})


def string_as_iri():
    return ((None, _tuple("http://example.org/x", pyodbc.VIRTUOSO_DV_STRING,
                          flag=1)), {})


def string_as_bnode():
    return ((None, _tuple("nodeID://b10102030405060708",
                          pyodbc.VIRTUOSO_DV_STRING, flag=1)), {})


def string_as_literal():
    return ((None, _tuple("a string with spaces", pyodbc.VIRTUOSO_DV_STRING,
                          flag=1)), {})


def wide_bytes_literal():
    return ((None, _tuple("café".encode("utf-8"), pyodbc.VIRTUOSO_DV_WIDE,
                          flag=0)), {})


def latin1_bytes_literal():
    return ((None, _tuple("café".encode("iso-8859-1"),
                          pyodbc.VIRTUOSO_DV_BLOB_WIDE_HANDLE, flag=0)), {})


def long_int():
    return ((None, _tuple("17", pyodbc.VIRTUOSO_DV_LONG_INT)), {})


def single_float():
    return ((None, _tuple(bytearray(b"\x00\x00\x80\x3f"),
                          pyodbc.VIRTUOSO_DV_SINGLE_FLOAT)), {})


def double_float():
    return ((None, _tuple(bytearray(b"\x00\x00\x00\x00\x00\x00\xf0\x3f"),
                          pyodbc.VIRTUOSO_DV_DOUBLE_FLOAT)), {})


def numeric():
    # llen=2, rlen=2 then the digits 1 2 . 3 4 (values are offsets from '0')
    return ((None, _tuple(bytearray([2, 2, 0, 0, 1, 2, 3, 4]),
                          pyodbc.VIRTUOSO_DV_NUMERIC)), {})


def datetime_date():
    return ((None, _tuple("2020-01-02 03:04:05", pyodbc.VIRTUOSO_DV_DATETIME,
                          dttype=pyodbc.VIRTUOSO_DT_TYPE_DATE)), {})


def datetime_time():
    return ((None, _tuple("2020-01-02 03:04:05", pyodbc.VIRTUOSO_DV_TIMESTAMP,
                          dttype=pyodbc.VIRTUOSO_DT_TYPE_TIME)), {})


def datetime_datetime():
    return ((None, _tuple("2020-01-02 03:04:05", pyodbc.VIRTUOSO_DV_DATETIME,
                          dttype=pyodbc.VIRTUOSO_DT_TYPE_DATETIME)), {})


def datetime_unknown_subtype():
    return ((None, _tuple("2020-01-02 03:04:05", pyodbc.VIRTUOSO_DV_DATETIME,
                          dttype=99)), {})


def date_only():
    return ((None, _tuple("2020-01-02", pyodbc.VIRTUOSO_DV_DATE)), {})


def time_only():
    return ((None, _tuple("03:04:05", pyodbc.VIRTUOSO_DV_TIME)), {})


def db_null():
    return ((None, _tuple(None, pyodbc.VIRTUOSO_DV_DB_NULL)), {})


def unhandled_dvtype():
    return ((None, _tuple("whatever", 255)), {})


VERDICT = run_pair(__file__, entry="resolve", calls=[
    not_a_tuple, iri_id, iri_id_bnode, rdf_typed, rdf_gyear,
    rdf_lang, string_as_iri, string_as_bnode, string_as_literal,
    wide_bytes_literal, latin1_bytes_literal, long_int, single_float,
    double_float, numeric, datetime_date, datetime_time, datetime_datetime,
    datetime_unknown_subtype, date_only, time_only, db_null,
    unhandled_dvtype,
])
