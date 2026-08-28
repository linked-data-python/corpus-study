# Context shim (see meta.json): _nodeid_to_bnode, the module-level helper of
# virtuoso/vstore.py that the region calls, copied verbatim from
# maparent/virtuoso-python@eba377e1fa (vstore.py lines 636-645).
# Imported identically by original.py and translated.ldpy.
from rdflib.term import BNode


def _nodeid_to_bnode(iri):
    #from string import digits
    iri = iri[9:]  # strip off "nodeID://"
    bnode = iri
    if len(iri) == 17:
        # assume we made it...
        ones, tens = iri[1::2], iri[2::2]
        chars = [x + y for x, y in zip(ones, tens)]
        bnode = "".join(str(chr(int(x) + 38)) for x in chars)
    return BNode(bnode)
