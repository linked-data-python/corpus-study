# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Ontology._set_imports (lines 647-651, band medium)
# licence of the source repository: see meta.json
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def _set_imports(self, other):
    if not other:
        return
    for o in other:
        self.graph.add((self.identifier, OWL_NS['imports'], o))
