"""Validation driver for dice-group__COVID19DS__acaps-covid19-government-measures_toRdf.py__<module>_64.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is module-level statement code: it fills the module-level graph `g`
and prints one line per row, so the pair is compared in module-state mode
(RDF isomorphism of `g`, plus captured stdout).

Both representations read their rows from the context shim `context_shim.py`,
which restores the two bindings the enclosing script provides (`pd` and
`xls`) and hands out a fresh copy of the table per call -- the region mutates
`row['LINK']`.  See meta.json.

What the six rows exercise:

  * the four `remove` calls: each of the four "unknown" markers (an IRI, an
    xsd:string, an xsd:integer and an xsd:date literal) occurs at least once,
    as the product of a missing cell after `fillna("unknown")`;
  * what the `remove` calls must NOT delete (a pattern that is too wide stays
    green on a shim without such neighbours): a row without ISO, COUNTRY and
    SOURCE writes `cvdr:unknown`, `"unknown"@en` and a triple whose subject is
    `cvdr:unknown`, none of which is one of the four markers; texts "Unknown"
    and "unknown " differ from the marker by case and by a trailing space;
  * the `LINK` branches (a space, which goes through `quote_plus`; an empty
    string; a missing one) and the `Alternative source` splits (`;`, ` and `,
    ` AND `, a trailing `;` which leaves an empty item, the empty string);
  * the input types of a spreadsheet read: a float PCODE, dates as datetime
    objects, and falsy cells that are not missing (an ID and a PCODE of 0,
    empty strings).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
