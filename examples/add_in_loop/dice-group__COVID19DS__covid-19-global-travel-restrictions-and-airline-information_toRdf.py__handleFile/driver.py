"""Validation driver for dice-group__COVID19DS__covid-19-global-travel-restrictions-and-airline-information_toRdf.py__handleFile.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is module-level code (no function), so ``entry=None``: both
modules are executed and every rdflib Graph in the module globals is compared,
plus captured stdout.  What it exercises is the ``reader`` fixture of
_context.py (six rows; the CSV itself is not in the repository):

  - rows 1-3 (original fixture): single and comma-separated iso3, a valid and
    an invalid pycountry code, present and absent X/Y, a URL and a non-URL
    source, empty cells;
  - row 4 (ObjectId int 7, X float, Y int, iso3 ``"MEX, FRA ,"``, accents):
    the types ``pd.read_csv(...).to_dict('records')`` gives in the repository
    for numeric columns, and an iso3 cell whose items need ``isoitem.strip()``
    (``" FRA "``, and an empty last item);
  - row 5 (ObjectId ``"abc"``, X ``"5"`` with Y ``""``): X non-empty and Y
    empty, the only way to tell the ``latitude != ''`` guard from the
    ``longitude != ''`` one, and a non-numeric ObjectId;
  - row 6 (ObjectId ``""``, X ``""`` with Y ``"6"``, invalid iso3 last): the
    converse, X empty and Y non-empty.  The last iso3 is kept invalid so that
    the module global ``iso2`` stays ``None`` on both sides.

Run on mutants of translated.ldpy (each is rejected, 72 vs 71 triples or
non-isomorphic): drop ``and latitude != ''``; drop ``and longitude != ''``;
``isoitem = isoitem.strip()`` -> ``isoitem = isoitem``; the ObjectId datatype
xsd:nonNegativeInteger -> xsd:integer.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
