# Extracted from schemaorg/sdopythonapp@128be97d35 : lib/rdflib/plugins/sparql/results/tsvresults.py
# region: TSVResultParser.convertTerm (lines 82-91, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql.parserutils import Comp, Param, CompValue
from rdflib import Literal as RDFLiteral
NONE_VALUE = object()

def convertTerm(self, t):
    if t is NONE_VALUE:
        return None
    if isinstance(t, CompValue):
        if t.name == 'literal':
            return RDFLiteral(t.string, lang=t.lang, datatype=t.datatype)
        else:
            raise Exception("I dont know how to handle this: %s" % (t,))
    else:
        return t
