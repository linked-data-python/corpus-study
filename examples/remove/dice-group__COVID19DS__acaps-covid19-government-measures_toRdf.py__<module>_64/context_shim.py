"""Context shim (see meta.json): the two bindings the region needs from its
enclosing script, dice-group/COVID19DS@7842845de5
acaps-covid19-government-measures/toRdf.py lines 10 and 47:

    import pandas as pd
    xls = pd.ExcelFile('acaps_covid19_government_measures_dataset.xlsx')

The spreadsheet is not in the repository and pandas is not in the evaluation
venv, so this module stands in for `pd` and `xls` with the smallest object
that answers `read_excel` / `fillna` / `iterrows` the way a DataFrame does.
No RDF logic here: the shim only restores the two missing bindings, and it is
imported identically by both representations.

The rows reproduce the shape the region sees *after* the enclosing script has
run (spaces already replaced by "_" in COUNTRY / REGION / ADMIN_LEVEL_NAME,
empty cells still None so that `fillna("unknown")` is exercised here).  They
cover, deliberately: a complete row; missing cells of each of the four
datatypes the region marks "unknown" (IRI, xsd:string, xsd:integer,
xsd:date), which are what the four `remove` calls delete; a LINK containing a
space (the `quote_plus` branch); and both separators of the
`Alternative source` column.  Three further rows give the `remove` calls
neighbours they must leave alone (missing ISO / COUNTRY / SOURCE, which write
`cvdr:unknown` and "unknown"@en rather than the removed markers; "Unknown" and
"unknown " in text cells), the input types a spreadsheet read gives (float
PCODE, datetime dates) and falsy cells (an ID of 0, "" cells).
"""

import copy
import datetime

_ROWS = [
    {
        "ID": 1,
        "ISO": "AFG",
        "COUNTRY": "Afghanistan",
        "REGION": "Asia",
        "ADMIN_LEVEL_NAME": "National",
        "PCODE": 12345,
        "LOG_TYPE": "Introduction / extension of measures",
        "CATEGORY": "Social distancing",
        "MEASURE": "Schools closure",
        "TARGETED_POP_GROUP": "No",
        "COMMENTS": "All schools closed until further notice",
        "NON_COMPLIANCE": "Not applicable",
        "DATE_IMPLEMENTED": "2020-03-16",
        "SOURCE": "Government of Afghanistan",
        "SOURCE_TYPE": "Government",
        "LINK": "https://example.org/afg/1",
        "ENTRY_DATE": "2020-04-01",
        "Alternative source": "https://example.org/alt/1; https://example.org/alt/2",
    },
    {
        # every "unknown" flavour at once: an unknown Alternative source
        # becomes URIRef("unknown"), an unknown PCODE an xsd:integer literal,
        # an unknown DATE_IMPLEMENTED an xsd:date one, the rest xsd:string.
        "ID": 2,
        "ISO": "ALB",
        "COUNTRY": "Albania",
        "REGION": "Europe",
        "ADMIN_LEVEL_NAME": None,
        "PCODE": None,
        "LOG_TYPE": "Phase-out measure",
        "CATEGORY": None,
        "MEASURE": "Partial lockdown",
        "TARGETED_POP_GROUP": "No",
        "COMMENTS": None,
        "NON_COMPLIANCE": "Fines",
        "DATE_IMPLEMENTED": None,
        "SOURCE": "Ministry of Health",
        "SOURCE_TYPE": "Government",
        "LINK": "https://example.org/alb 2",
        "ENTRY_DATE": "2020-04-02",
        "Alternative source": None,
    },
    {
        # same COUNTRY as row 1 (the country triples are re-added, and the
        # graph is a set), an unknown LINK, and the " AND " separator.
        "ID": 3,
        "ISO": "AFG",
        "COUNTRY": "Afghanistan",
        "REGION": "Asia",
        "ADMIN_LEVEL_NAME": "Provincial",
        "PCODE": 6789,
        "LOG_TYPE": "Introduction / extension of measures",
        "CATEGORY": "Movement restrictions",
        "MEASURE": "Border closure",
        "TARGETED_POP_GROUP": "Yes",
        "COMMENTS": "Land borders closed",
        "NON_COMPLIANCE": None,
        "DATE_IMPLEMENTED": "2020-03-21",
        "SOURCE": "WHO",
        "SOURCE_TYPE": "Other organisation",
        "LINK": None,
        "ENTRY_DATE": "2020-04-03",
        "Alternative source": "https://example.org/alt/3 AND https://example.org/alt/4",
    },
    {
        # the neighbours the four `remove` calls must NOT touch: ISO,
        # COUNTRY and SOURCE are missing, so the row writes cvdr:unknown (an
        # IRI in the cvdr namespace, not the bare IRI "unknown" that the
        # first remove deletes), "unknown"@en (a language literal, not the
        # xsd:string one) and, for the ISO, cvdr:unknown isoCodeRegion
        # "unknown"^^xsd:string, a triple whose SUBJECT is not this row's;
        # COMMENTS "Unknown" and ADMIN_LEVEL_NAME "unknown " differ from the
        # marker by case and by a trailing space; the Alternative source ends
        # in ';', so the split leaves an empty last item (URIRef('')).
        "ID": 4,
        "ISO": None,
        "COUNTRY": None,
        "REGION": None,
        "ADMIN_LEVEL_NAME": "unknown ",
        "PCODE": 4321,
        "LOG_TYPE": "Introduction / extension of measures",
        "CATEGORY": "Public health measures",
        "MEASURE": "Mask wearing",
        "TARGETED_POP_GROUP": "Yes",
        "COMMENTS": "Unknown",
        "NON_COMPLIANCE": "Fines",
        "DATE_IMPLEMENTED": "2020-05-01",
        "SOURCE": None,
        "SOURCE_TYPE": "Media",
        "LINK": "https://example.org/mask  with spaces",
        "ENTRY_DATE": "2020-05-02",
        "Alternative source": "https://example.org/alt/5;",
    },
    {
        # the input types a real spreadsheet read gives: float PCODE, dates
        # as datetime objects, and falsy cells (0, "") that are not missing:
        # an ID of 0, an empty LINK (URIRef('') after strip), an empty
        # ADMIN_LEVEL_NAME, a PCODE of 0.
        "ID": 0,
        "ISO": "MEX",
        "COUNTRY": "Mexico",
        "REGION": "Americas",
        "ADMIN_LEVEL_NAME": "",
        "PCODE": 0,
        "LOG_TYPE": "Phase-out measure",
        "CATEGORY": "Lockdown",
        "MEASURE": "Curfew",
        "TARGETED_POP_GROUP": "No",
        "COMMENTS": "",
        "NON_COMPLIANCE": "Not applicable",
        "DATE_IMPLEMENTED": datetime.datetime(2020, 6, 1, 0, 0),
        "SOURCE": "",
        "SOURCE_TYPE": "Government",
        "LINK": "",
        "ENTRY_DATE": datetime.datetime(2020, 6, 2, 0, 0),
        "Alternative source": "",
    },
    {
        # a float PCODE and an unknown PCODE next to an integer one
        "ID": 6,
        "ISO": "MEX",
        "COUNTRY": "Mexico",
        "REGION": "Americas",
        "ADMIN_LEVEL_NAME": "National",
        "PCODE": 4321.0,
        "LOG_TYPE": "Introduction / extension of measures",
        "CATEGORY": "Lockdown",
        "MEASURE": "Curfew",
        "TARGETED_POP_GROUP": "No",
        "COMMENTS": "unknown",
        "NON_COMPLIANCE": "Not applicable",
        "DATE_IMPLEMENTED": datetime.datetime(2020, 6, 3, 0, 0),
        "SOURCE": "Ministry",
        "SOURCE_TYPE": "Government",
        "LINK": "https://example.org/mex/6",
        "ENTRY_DATE": "2020-06-04",
        "Alternative source": "https://example.org/alt/6 and https://example.org/alt/7",
    },
]


class _Frame:
    """The three DataFrame operations the region and its context use."""

    def __init__(self, rows):
        self._rows = rows

    def fillna(self, value):
        return _Frame([{k: (value if v is None else v) for k, v in row.items()}
                       for row in self._rows])

    def iterrows(self):
        for index, row in enumerate(self._rows):
            yield index, row


class _ExcelFile:
    def __init__(self, sheets):
        self._sheets = sheets


class _Pandas:
    @staticmethod
    def ExcelFile(path):                        # noqa: N802 - pandas' name
        return _ExcelFile({"Dataset": _ROWS})

    @staticmethod
    def read_excel(xls, sheet_name):
        # a fresh copy per call: the region mutates row['LINK'], and the two
        # representations are executed in the same process.
        return _Frame(copy.deepcopy(xls._sheets[sheet_name]))


pd = _Pandas()
xls = pd.ExcelFile('acaps_covid19_government_measures_dataset.xlsx')
