# Extracted from schemaorg/sdopythonapp@128be97d35 : lib/rdflib/plugins/sparql/parser.py
# region: <module> (lines 322-323, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib.compat import decodeUnicodeEscape
import rdflib
STRING_LITERAL2 = Regex(
    u'"(?:[^"\\n\\r\\\\]|\\\\["ntbrf\\\\])*"(?!")', flags=re.U)

STRING_LITERAL2.setParseAction(
    lambda x: rdflib.Literal(decodeUnicodeEscape(x[0][1:-1])))
