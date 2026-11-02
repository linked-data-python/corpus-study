"""Driver for usc-gria__sw-kg__teams_pela_TAREA_6_src_preprocess.py__preprocess.

`preprocess()` takes nothing: it parses the knowledge graph at KG_PATH (the
context shim points it at `fixture.ttl`, which holds N-Triples as the region
expects), runs three SPARQL queries on it, asks Wikidata for more (through
get_wikidata_info) and writes `fields.csv` and `matches.csv`.  Observed, on
both sides: stdout (the progress lines and the Wikidata error lines), and the
two CSV files, whose text is compared (so the row order, the `resultado`
string, the cut date, the empty cells of the OPTIONALs are all checked).

The network is replaced by a local stand-in for `requests.get`, the same one
for both sides.  Three calls, one mode each:

  ok        Wikidata answers: population and image for some districts,
            description and image for one sport, nothing for the others.
  http500   every request is refused with a 500: the retry lines are printed
            and the Wikidata columns stay empty.
  raises    `requests.get` raises: the "Attempt n failed" lines.

fixture.ttl is built against the three queries:
  query 1  three fields (one district without sameAs, one with two sameAs ->
           two rows for its field), a field without coorY and a "Pista" with
           all of a field's properties: neither is a solution;
  query 2  two complete matches (a dateTime and a date for the hour), one
           without resultado2 (no row), one complete match outside any
           competition (its sport stays empty in the left merge);
  query 3  two sports (one without sameAsDeporte), one competition whose chain
           is broken before tipoDe.
"""
import time

import requests

from rdfeval.harness import run_pair

time.sleep = lambda seconds: None

Q1, Q2, Q3, Q4 = ("http://www.wikidata.org/entity/Q%d" % n for n in (1, 2, 3, 4))
POPULATION = {Q1: {"poblacion": "100000", "imagen": "http://img.example/centro.jpg"},
              Q3: {"poblacion": "250"}}
SPORT = {Q2: {"descripcion": "deporte de equipo", "imagen": "http://img.example/futbol.jpg"}}

MODE = {"value": "ok"}


class _Response:
    def __init__(self, status, payload=None):
        self.status_code = status
        self._payload = payload

    def json(self):
        return self._payload


def _get(url, params=None, headers=None, timeout=None):
    mode = MODE["value"]
    if mode == "raises":
        raise requests.ConnectionError("no network")
    if mode == "http500":
        return _Response(500)
    query = params["query"]
    table = POPULATION if "wdt:P1082" in query else SPORT
    bindings = [{"item": {"value": uri}, **{k: {"value": v} for k, v in fields.items()}}
                for uri, fields in table.items() if "<%s>" % uri in query]
    return _Response(200, {"results": {"bindings": bindings}})


requests.get = _get


def _call(mode):
    def make():
        MODE["value"] = mode
        return (), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='preprocess',
    fixture="fixture.ttl",
    calls=[_call("ok"), _call("http500"), _call("raises")],
)
