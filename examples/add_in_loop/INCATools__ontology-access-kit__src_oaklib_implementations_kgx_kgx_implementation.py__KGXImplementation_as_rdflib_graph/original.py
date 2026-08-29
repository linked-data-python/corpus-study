# Extracted from INCATools/ontology-access-kit@5f88047efa : src/oaklib/implementations/kgx/kgx_implementation.py
# region: KGXImplementation.as_rdflib_graph (lines 618-645, stratum add_in_loop)
# licence of the source repository: see meta.json
import logging
import re
import rdflib

def as_rdflib_graph(self) -> rdflib.Graph:
    g = rdflib.Graph()
    bnodes = {}

    uri_re = re.compile(r"^<(.*)>$")

    def tr(n: str, v: str = None, datatype: str = None):
        if n:
            uri_match = uri_re.match(n)
            if n.startswith("_"):
                if n not in bnodes:
                    bnodes[n] = rdflib.BNode()
                return bnodes[n]
            elif uri_match:
                return rdflib.URIRef(uri_match.group(1))
            else:
                return rdflib.URIRef(self.curie_to_uri(n))
        else:
            lit = rdflib.Literal(v, datatype=datatype)
            return lit

    for row in self.session.query(NodeProperty):
        s = tr(row.subject)
        p = tr(row.predicate)
        o = tr(row.object, row.value, row.datatype)
        logging.debug(f"Triple {s} {p} {o}")
        g.add((s, p, o))
    return g
