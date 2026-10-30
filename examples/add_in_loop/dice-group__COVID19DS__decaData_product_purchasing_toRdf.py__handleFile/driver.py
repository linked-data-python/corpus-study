"""Validation driver for dice-group__COVID19DS__decaData_product_purchasing_toRdf.py__handleFile.

Establishes semantic equivalence of original.py and translated.ldpy.

handleFile() takes no argument and returns nothing: it mutates the
module-level graph `g` (closure over a global, not a parameter), so the
entry-mode comparison (which only looks at a call's return value, its
mutated args/kwargs and stdout) would see nothing to compare and report a
hollow pass. Both original.py and translated.ldpy therefore carry an
identical "demo harness" appendix (see meta.json) that calls handleFile()
once at module level, so entry=None / module-state comparison picks up `g`
by name and compares it by graph isomorphism -- the same pattern as
examples/remove/DataDrivenCPS__acquirium__.../driver.py.

The input CSV (COVID19_INDEX_SAMPLE_....csv, alongside this driver) and the
context shim (context_shim.py: pandas, OrderedDict, repl()) are read by both
representations identically; see meta.json.

What the CSV exercises (repair of 2026-10-30, rows numbered from 1):
  * the ten columns the dataset README documents (DATE, STORE_ZIP_CODE,
    UPC, QTY, NET_SALES, GROSS_SALES, BRAND, PRODUCT_DESCRIPTION,
    SUB_CATEGORY, PERSONA), so every `if heading == ...` branch and the
    generic cvdo[...] predicate are reached;
  * row 3 has an EMPTY STORE_ZIP_CODE: the guard `if row[heading] != ""`
    around the zipcodes lookup is decided here (without it,
    zipcodes.matching('') raises), and the empty postalCode value is
    skipped by the second guard; it also carries a negative QTY (refunds,
    per the README) and NET_SALES "0", a falsy-looking value that must
    still be written;
  * row 4 has a zip with a leading zero (02139, Massachusetts), a second
    county and city, and empty BRAND / PERSONA cells;
  * pandas infers mixed column types (UPC int, NET_SALES float, the
    others str because of an empty cell), as on the real file, and both
    sides receive the same values.
Mutants killed by this CSV and not by the former 2-row one: the zip guard
replaced by `if True:`.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
