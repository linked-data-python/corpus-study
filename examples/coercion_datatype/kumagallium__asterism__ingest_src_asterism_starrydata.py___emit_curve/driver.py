"""Validation driver for kumagallium__asterism__ingest_src_asterism_starrydata.py___emit_curve.

`_emit_curve(g, row, sd, sdr, ingestion_iri) -> bool` adds the triples of one
curves.csv row to `g`; the harness compares the returned bool and `g` after
the call (graph isomorphism). `sd` / `sdr` are the namespaces the source
builds from the dataset configuration (same IRIs as asterism/watcher.py's
defaults). Each call below makes the original show a different part of the
region; the typed-literal sites (`Literal(x, datatype=XSD.double)` on
min/max of the arrays, `XSD.integer` on the point count, `XSD.dateTime` on the
parsed timestamp) are reached by the values that rdflib normalises:

  * call 0, the complete row: every guarded triple present, every mapped
    quantity kind and unit (QUDT IRIs), JSON arrays, two project names, a
    created_at / updated_at pair with a `GMT+0900 (Japan Standard Time)` offset
    (prov:atTime is the UTC instant), an ingestion activity;
  * call 1, arrays whose extremes rdflib writes differently from Python's
    str(): `1e-05`, ints (`3` -> "3.0"), `1e+22`, negative, with NaN / null /
    a non-number inside (dropped by parse_float_array); the longer y array
    makes point_count the SHORTER length;
  * call 2, created_at WITHOUT a timezone: parse_curator_timestamp returns
    None, so dcterms:created is written and prov:atTime is not; updated_at is
    set, `ingestion_iri` is None;
  * call 3, unmapped property / unit and empty arrays: no QUDT triple, no
    min/max, no pointCount; only the string predicates;
  * call 4, only `updated_at` (created_at empty): dcterms:modified without
    dcterms:created, and no atTime;
  * calls 5-7, a missing figure_id / sample_id / SID: the region returns
    False and writes NOTHING (the graph stays empty);
  * call 8, values with surrounding spaces and JSON-quoted strings:
    strip_quoted / strip(), a quoted name that is not valid JSON;
  * call 9, a graph that already holds triples about the same curve: the
    added ones merge with them (and the pre-existing prefix is kept).
"""
from rdflib import Graph, Literal, Namespace, URIRef

from rdfeval.harness import run_pair

SD = Namespace("https://kumagallium.github.io/asterism/starrydata/ontology#")
SDR = Namespace("https://kumagallium.github.io/asterism/starrydata/resource/")
ING = URIRef("https://kumagallium.github.io/asterism/starrydata/resource/ingestion/2026-01-01")

FULL = {
    "figure_id": "12", "sample_id": "345", "SID": "1001",
    "figure_name": '"Figure 3a"',
    "prop_x": '"Temperature"', "prop_y": "Seebeck coefficient",
    "unit_x": "K", "unit_y": "V*K^(-1)",
    "comments": '"measured in vacuum"',
    "x": "[300, 400.5, 500]", "y": "[-1.5e-05, 2.5e-05, 3.0e-05]",
    "project_names": '["Thermoelectric", " Bulk ", ""]',
    "created_at": "Fri Sep 01 2017 18:19:39 GMT+0900 (Japan Standard Time)",
    "updated_at": "Sat Sep 02 2017 09:00:00 GMT+0900 (Japan Standard Time)",
}


def row(**changes):
    r = dict(FULL)
    r.update(changes)
    return r


def case(r, ingestion=ING, graph=None):
    return lambda: ((graph() if graph else Graph(), r, SD, SDR, ingestion), {})


def seeded():
    g = Graph()
    g.bind("sd", SD)
    curve = SDR["curve/1001-12-345"]
    g.add((curve, SD.figureName, Literal("Figure 3a")))
    g.add((curve, SD.propertyX, Literal("Temperature")))
    g.add((curve, SD.pointCount, Literal(99)))
    g.add((SDR["curve/1001-12-346"], SD.figureName, Literal("another curve")))
    return g


VERDICT = run_pair(
    __file__,
    entry="_emit_curve",
    calls=[
        case(FULL),
        case(row(x="[1e-05, 3, 2.5e10, 1e22, null, \"n/a\", -0.5, NaN]",
                 y="[7, 8, 9, 10, 11, 12, 13, 14, 15, 16]")),
        case(row(created_at="Fri Sep 01 2017 18:19:39", updated_at="Sat Sep 02 2017"),
             ingestion=None),
        case(row(prop_x="Unknown quantity", prop_y="", unit_x="furlong", unit_y="K^2",
                 x="", y="[]", project_names="not json")),
        case(row(created_at="", updated_at="Sun Sep 03 2017 01:02:03 GMT-0500 (EST)")),
        case(row(figure_id="")),
        case(row(sample_id=" ")),
        case(row(SID="")),
        case(row(figure_name='  "bad "quoted" name"  ', comments="  plain, with spaces  ",
                 prop_x="  thermopower ", unit_x="  K  ")),
        case(FULL, graph=seeded),
    ],
)
