# Context shim (see meta.json): subset of V1/validate.py from
# dice-group/RELD@7ca93acbb636c54515ee50c8f07257faa1b06193, so the region
# executes outside the package. Identical bindings for both representations.
import re


def returnValue(dict, search):
    for key, value in dict.items():
        if value == search:
            return key


def check_type(string):
    if bool(re.match(r'^[0-9\.]*$', string)):
        return True
    else:
        False


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


def is_date(string, fuzzy=False):
    from dateutil.parser import parse
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
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
    listToStr = ' '.join(map(str, s))
    return listToStr


def wikidata_id_toText(ids):
    # Not exercised by this region (network call in the original); kept as
    # a stub so the unused import resolves.
    raise NotImplementedError
