# Context shim (see meta.json), for dice-group/RELD@7ca93acbb6 : V1/semEval.py.
#
# The extracted region (lines 145-259) is the BODY of `create_rdf(output,
# dsName, subject_dict, object_dict)` (the real function starts at line 120)
# -- it reads several names that are either the function's own parameters
# (`output`, `dsName`, `subject_dict`, `object_dict`) or locals the real
# function sets up just above the extracted range (`sent_counter = 0`,
# `ne_counter = 0`, `list_Others = [...]`, `rel_data = pd.read_csv(...)`,
# lines 121-127 of that file), none of which the extraction captured.
#
# containsNumber/returnValue/check_type/remove_alphaNumeric are copied
# verbatim from V1/validate.py (a sibling module in the same repository,
# fetched at the pinned commit via `gh api`) -- all four are pure string/dict
# functions with no external dependency. is_date/clean_sentences/
# wikidata_id_toText are imported by original.py (matching the real file's
# import line) but never called inside create_rdf; is_date and
# clean_sentences are copied too (also pure, cheap to keep faithful);
# wikidata_id_toText needs SPARQLWrapper and the network, so it stays an
# unused placeholder, imported by name only, per the boricles/ontosphere
# GraphService precedent already in this corpus.
#
# RelData stands in for the pandas DataFrame `rel_data`: pandas is not
# installed in this study's venv, and the source CSV
# (data/AllRelationWithCrossCheck.csv) is not committed to the repository
# either, so pulling in the real dependency is out of reach either way. The
# region's ENTIRE use of it is one lookup --
# `rel_data.loc[rel_data[col] == value, 'Srid'].iloc[0]`, a single-column
# equality selection returning the first match -- so this reproduces exactly
# that indexing behaviour (`__getitem__`/`.loc`/`.iloc`) against a plain list
# of dict rows, not a general DataFrame stand-in.
#
# Identical bindings for both representations.
import re


def returnValue(dict_, search):
    for key, value in dict_.items():
        if value == search:
            return key


def is_date(string, fuzzy=False):
    from dateutil.parser import parse
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False


def check_type(string):
    if bool(re.match(r'^[0-9\.]*$', string)):
        return True
    else:
        False  # noqa: the real source has no `return` here either (falls through to None)


def remove_alphaNumeric(string):
    new_string = re.sub(r"[^a-zA-Z0-9_]+", ' ', string)
    new_string = new_string.strip().replace(" ", "_")
    if '__' in new_string:
        new_string = new_string.replace("__", "_")
    return new_string


def containsNumber(string):
    if re.match(r".*\d+.*", string):
        return True
    else:
        return False


def clean_sentences(string, e1, e2):
    s = []
    string = string.replace('"', '')
    string = string.replace('.', '')
    string = string.split(' ')
    for w in string:
        if w.strip() == '<e1>' + e1.strip() + '</e1>':
            w = e1
        elif w.strip() == '<e2>' + e1.strip() + '</e2>':
            w = e1
        elif w.strip() == '<e1>' + e2.strip() + '</e1>':
            w = e2
        elif w.strip() == '<e2>' + e2.strip() + '</e2>':
            w = e2
        s.append(w)
    return ' '.join(map(str, s))


def wikidata_id_toText(ids):
    """Empty placeholder: needs SPARQLWrapper and the network, never called
    inside create_rdf -- imported by name only (see header)."""


class _Column:
    def __init__(self, values):
        self._values = values

    def __eq__(self, other):
        return [v == other for v in self._values]


class _ILoc(list):
    @property
    def iloc(self):
        return self


class _Loc:
    def __init__(self, table):
        self._table = table

    def __getitem__(self, key):
        mask, col = key
        return _ILoc(row[col] for row, keep in zip(self._table._rows, mask) if keep)


class RelData:
    def __init__(self, rows):
        self._rows = rows  # list of dict, e.g. {"RE-SemEval-Relation": "P7", "Srid": 7}

    def __getitem__(self, col):
        return _Column([row[col] for row in self._rows])

    @property
    def loc(self):
        return _Loc(self)
