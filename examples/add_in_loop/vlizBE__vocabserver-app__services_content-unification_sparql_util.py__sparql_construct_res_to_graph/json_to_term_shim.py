# Context shim (see meta.json): json_to_term from
# vlizBE/vocabserver-app@af910ef750244b7320fa5d2cdf67a44abfec51f4,
# services/content-unification/sparql_util.py, so the region executes
# outside the module. Identical bindings for both representations.
from rdflib.term import URIRef, Literal


def json_to_term(json_term):
    if json_term['type'] == 'uri':
        return URIRef(json_term['value'])
    else:
        if 'xml:lang' in json_term:  # SELECT
            lang = json_term['xml:lang']
            return Literal(json_term['value'], lang=lang)
        elif 'lang' in json_term:  # CONSTRUCT
            lang = json_term['lang']
            return Literal(json_term['value'], lang=lang)
        else:
            if 'datatype' in json_term:
                return Literal(json_term['value'], datatype=json_term['datatype'])
            else:
                return Literal(json_term['value'])
