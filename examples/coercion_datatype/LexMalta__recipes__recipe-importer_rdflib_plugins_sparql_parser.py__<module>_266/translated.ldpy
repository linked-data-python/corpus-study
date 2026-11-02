# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/plugins/sparql/parser.py
# region: <module> (lines 266-266, stratum coercion_datatype)
# licence of the source repository: see meta.json
from pyparsing import (
    Combine,
    Forward,
    Group,
    Literal,
    OneOrMore,
    Optional,
    ParseResults,
    Regex,
    Suppress,
    ZeroOrMore,
    delimitedList,
    restOfLine,
)
import rdflib
DECIMAL = Regex(r"[0-9]*\.[0-9]+")  # (?![eE])

DECIMAL.setParseAction(lambda x: rdflib.Literal(x[0], datatype=rdflib.XSD.decimal))
