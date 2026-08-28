# Context shim (see meta.json): the two helpers the region imports, copied from
# cognitedata/neat@4042d3e96d — `as_neat_compliant_uri` from
# cognite/neat/_v0/core/_utils/rdf_.py (with its dependency `get_namespace`)
# and `sentence_or_string_to_camel` from cognite/neat/_v0/core/_utils/text.py
# (with its dependencies `to_camel_case`, `_to_camel_case`, `_to_pascal_case`).
# The package is not installed, and importing it would pull in cognite-sdk and
# pydantic; the bodies below are verbatim so the region computes the same terms.
# Identical bindings for both representations.
import re

from rdflib import URIRef
from rdflib.namespace import split_uri


def get_namespace(URI: URIRef, special_separator: str = "#_") -> str:
    return split_uri(URI, special_separator)[0]


def as_neat_compliant_uri(uri: URIRef) -> URIRef:
    namespace = get_namespace(uri)
    id_ = remove_namespace_from_uri(uri)
    compliant_uri = re.sub(r"[^a-zA-Z0-9-_.]", "", id_)
    return URIRef(f"{namespace}{compliant_uri}")


def remove_namespace_from_uri(URI, *, special_separator: str = "#_",
                              validation: str = "prefix"):
    # the single-URI, validation="prefix" branch of the upstream overloaded
    # function (the only one the region reaches), body verbatim
    u = URI
    if u.lower().startswith("http"):
        return u.split(special_separator if special_separator in u
                       else "#" if "#" in u else "/")[-1]
    return str(u)


def to_camel_case(string: str) -> str:
    string = re.sub(r"[^a-zA-Z0-9_]", "_", string)
    string = re.sub("_+", "_", string)
    is_all_upper = string.upper() == string
    is_first_upper = (
        len(string) >= 2 and string[:2].upper() == string[:2] and "_" not in string[:2] and not is_all_upper
    )
    return _to_camel_case(string, is_all_upper, is_first_upper)


def _to_camel_case(string: str, is_all_upper: bool, is_first_upper: bool) -> str:
    if "_" in string:
        pascal_splits = [
            _to_pascal_case(part, is_all_upper, is_first_upper and no == 0)
            for no, part in enumerate(string.split("_"), 0)
        ]
    else:
        # Ensure pascal
        if string:
            string = string[0].upper() + string[1:]
        pascal_splits = [string]
    cleaned: list[str] = []
    for part in pascal_splits:
        if part.upper() == part and is_all_upper:
            cleaned.append(part.capitalize())
        else:
            cleaned.append(part)

    string_split = []
    for part in cleaned:
        string_split.extend(re.findall(r"[A-Z][a-z0-9]*", part))
    if not string_split:
        string_split = [string]
    if len(string_split) == 0:
        return ""
    # The first word is a single letter, keep the original case
    if is_first_upper:
        return "".join(word for word in string_split)
    else:
        return string_split[0].casefold() + "".join(word for word in string_split[1:])


def _to_pascal_case(string: str, is_all_upper: bool, is_first_upper: bool) -> str:
    camel = _to_camel_case(string, is_all_upper, is_first_upper)
    return f"{camel[0].upper()}{camel[1:]}" if camel else ""


def sentence_or_string_to_camel(string: str) -> str:
    # Could be a combination of kebab and pascal/camel case
    if " " in string:
        parts = string.split(" ")
        try:
            return parts[0].casefold() + "".join(word.capitalize() for word in parts[1:])
        except IndexError:
            return ""
    else:
        return to_camel_case(string)
