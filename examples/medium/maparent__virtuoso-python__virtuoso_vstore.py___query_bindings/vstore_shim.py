# Context shim (see meta.json): the region calls _bnode_to_nodeid, defined
# further up the same module (maparent/virtuoso-python@eba377e1fa,
# virtuoso/vstore.py:625).  That module cannot be imported here -- its header
# pulls in pyodbc, the `future` package and a live Virtuoso connection -- so the
# one helper the region needs is reproduced verbatim below.
#
# This module is imported IDENTICALLY by original.py and translated.ldpy.
from rdflib.term import URIRef


def _bnode_to_nodeid(bnode):
    from string import ascii_letters
    iri = bnode
    for c in bnode[1:]:
        if c in ascii_letters:
            # from rdflib not virtuoso
            iri = "b" + "".join(str(ord(x) - 38) for x in bnode[:8])
            break
    return URIRef("nodeID://%s" % iri)
