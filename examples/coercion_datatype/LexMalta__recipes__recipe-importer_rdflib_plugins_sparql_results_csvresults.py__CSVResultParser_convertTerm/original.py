# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/plugins/sparql/results/csvresults.py
# region: CSVResultParser.convertTerm (lines 46-53, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, Literal, URIRef, Variable

def convertTerm(self, t):
    if t == "":
        return None
    if t.startswith("_:"):
        return BNode(t)  # or generate new IDs?
    if t.startswith("http://") or t.startswith("https://"):  # TODO: more?
        return URIRef(t)
    return Literal(t)
