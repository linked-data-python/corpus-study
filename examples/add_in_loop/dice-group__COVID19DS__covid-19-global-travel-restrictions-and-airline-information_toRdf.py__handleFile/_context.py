# Context shim (see meta.json): helpers and row data for
# covid-19-global-travel-restrictions-and-airline-information/toRdf.py in
# dice-group/COVID19DS@7842845de5.
#
# `repl` and `capitalizeWords` are copied verbatim from the module-level
# helpers of the real file (they live outside the extracted lineno range,
# lines 203-207 of the real file).
#
# `reader` stands in for
#   pd.read_csv('Data WFP Coronavirus COVID-19 Travel Restrictions - '
#                'COVID-19 airline restrictions information.csv',
#                keep_default_na=False).to_dict('records', into=OrderedDict)
# `pandas` is not installed in the study venv, and -- more fundamentally --
# the CSV itself is not committed to the repository at the pinned commit
# (checked via `gh api repos/dice-group/COVID19DS/contents/...`: the
# directory holds only README, nuts/ and toRdf.py), so no real row data can
# be recovered at all. This is a hand-written stand-in with the same shape
# an iterable of OrderedDict rows, string-valued, using the real column
# names the function branches on (ObjectId, iso3, adm0_name, X, Y, source,
# published) plus one generic column to exercise the dynamic-predicate
# default branch. It covers: several solutions (3 rows), a comma-separated
# multi-value iso3 cell (the inner `for isoitem in iso:` loop), a valid ISO
# alpha-3 code alongside an invalid one (both branches of the pycountry
# lookup below), present vs. absent geo coordinates, a "source" cell that
# is and is not a URL, and empty cells (the zero-value branch of
# `row[heading] != ""`).
#
# Identical for both representations.
import re
from collections import OrderedDict


def repl(m):
    return m.group(1).upper()


def capitalizeWords(s):
    return re.sub(r'\w+', lambda m: m.group(0).capitalize(), s).replace(" ", "")


reader = [
    OrderedDict([
        ("ObjectId", "1"),
        ("iso3", "MEX"),
        ("adm0_name", "mexico"),
        ("X", "-102.55"),
        ("Y", "23.63"),
        ("source", "https://data.humdata.org/dataset/mexico-travel-restrictions"),
        ("published", "2020-04-01"),
        ("extra_col", "note one"),
    ]),
    OrderedDict([
        ("ObjectId", "2"),
        ("iso3", "zzz"),
        ("adm0_name", ""),
        ("X", ""),
        ("Y", ""),
        ("source", "no link here"),
        ("published", ""),
        ("extra_col", ""),
    ]),
    OrderedDict([
        ("ObjectId", "3"),
        ("iso3", "MEX,FRA"),
        ("adm0_name", "Costa Rica"),
        ("X", "9.75"),
        ("Y", "-83.75"),
        ("source", "https://example.org/costa-rica-info"),
        ("published", "2020-06-15"),
        ("extra_col", "third row note"),
    ]),
]
