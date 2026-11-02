"""Validation driver for city-knowledge-graphs__python__lab6_lab6_solution.py__Lab6Solution_SimpleUniqueMapping.

`SimpleUniqueMapping` is a method (`self` explicit): the driver builds the
`self` the real constructor would (data_frame read from cities.csv with the
SAME `pd.read_csv(file, sep=',', quotechar='"', escapechar="\\\\")` call as
Lab6Solution.__init__, lab6_ns_str, lab6 namespace, empty graph with the
`lab6` prefix bound, and `is_nan` = `x != x`), calls the region, and the
harness compares what the call did to `self.g` (graph isomorphism + prefix
bindings) and to the rest of `self`.

cities.csv is written against the region (the numeric cells reach the
`^^xsd:float` / `^^xsd:long` sites as numpy values, the string cells the
`^^xsd:string` ones):
  * rows with several solutions of each column (Tokyo, Delhi, Mumbai, ...);
  * pandas turns the ISO code "NA" (Namibia) into NaN: the guarded iso2 triple
    must be left out, while the row is still emitted;
  * an empty `capital` cell is NaN (predicate stays cityIsLocatedIn), values
    "admin" / "primary" / "minor" / "other" select each predicate branch;
  * missing lat/lng/population/admin_name/iso cells (Ghostville, Kyoto);
  * a NaN city_ascii (Lyon) or NaN country (Paris) skips the whole row, a NaN
    `city` alone (Orphan) only skips lab6:name;
  * two cities of one country (Delhi, Mumbai): the country triples are added
    twice and must collapse;
  * names with a space and a comma ("New York", "Korea, South") and with
    non-ASCII characters (Zürich, Tōkyō).
Calls: the whole file; only its header (zero rows); a DataFrame whose every
row is skipped by the NaN guard.
"""
import io
import pandas as pd
from pathlib import Path

from rdflib import Graph, Namespace

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
NS = "http://www.semanticweb.org/ernesto/inm713/lab6/"


class _Lab6Base:
    """The attributes the region reads (and what Lab6Solution.__init__ sets).
    The DataFrame is a CLASS attribute of the per-call subclass (see Lab6Stub):
    the harness compares an instance by its __dict__, and a DataFrame has no
    usable ==; the graph `g` is what the call changes."""

    def __init__(self):
        self.lab6_ns_str = NS
        self.lab6 = Namespace(NS)
        self.g = Graph()
        self.g.bind("lab6", self.lab6)

    def is_nan(self, x):
        return (x != x)


def Lab6Stub(data_frame):
    return type("Lab6Stub", (_Lab6Base,), {"data_frame": data_frame})()


def read(text=None):
    src = HERE / "cities.csv" if text is None else io.StringIO(text)
    return pd.read_csv(src, sep=',', quotechar='"', escapechar="\\")


HEADER = open(HERE / "cities.csv").readline()

VERDICT = run_pair(
    __file__,
    entry="SimpleUniqueMapping",
    calls=[
        lambda: ((Lab6Stub(read()),), {}),
        lambda: ((Lab6Stub(read(HEADER)),), {}),
        lambda: ((Lab6Stub(read(HEADER + ",,,,,,,,,\n,Nobody,1,2,,US,USA,,,5\n")),), {}),
    ],
)
