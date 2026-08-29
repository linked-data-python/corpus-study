# Extracted from schemaorg/sdopythonapp@128be97d35 : lib/rdflib/plugins/sparql/parser.py
# region: <module> (lines 322-323, stratum coercion_datatype)
# licence of the source repository: see meta.json
# `import re` and `from pyparsing import Regex` restore bindings the context
# lines do not carry (they are the real file's own top-of-module imports,
# lines 10 and 12-14 of lib/rdflib/plugins/sparql/parser.py).
import re
from pyparsing import Regex
from rdflib.compat import decodeUnicodeEscape
import rdflib
STRING_LITERAL2 = Regex(
    u'"(?:[^"\\n\\r\\\\]|\\\\["ntbrf\\\\])*"(?!")', flags=re.U)

STRING_LITERAL2.setParseAction(
    lambda x: rdflib.Literal(decodeUnicodeEscape(x[0][1:-1])))


# Demo harness (identical on both sides, see meta.json): the region only
# DEFINES a pyparsing grammar rule and its parse action -- nothing runs it,
# so nothing is observable at module scope.  demo() runs the parser on a
# concrete SPARQL string-literal token and returns the rdflib term the parse
# action built, which is what driver.py compares.
def demo(text):
    return STRING_LITERAL2.parseString(text, parseAll=True)[0]
