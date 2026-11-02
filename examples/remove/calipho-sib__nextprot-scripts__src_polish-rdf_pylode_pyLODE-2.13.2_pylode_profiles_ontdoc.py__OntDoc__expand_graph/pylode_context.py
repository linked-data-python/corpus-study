# Context shim (see meta.json): the part of OntDoc that the region touches,
# from calipho-sib/nextprot-scripts@f03504ce5e
# src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/ontdoc.py, so the region
# (a method body lifted out of its class) executes outside pyLODE 2.13.2.
# Identical for both representations.  OntDoc.__init__ builds `self.G` from a
# parsed source; here the caller hands the graph in.
class OntDoc:
    def __init__(self, G):
        self.G = G
