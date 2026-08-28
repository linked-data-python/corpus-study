# Context shim (see meta.json): subset of arango_rdf/main.py and
# arango_rdf/typings.py from ArangoDB-Community/ArangoRDF@48cfed903a, so the
# region executes outside the package.  Identical bindings for both
# representations; excluded from the surface metrics.
#
# The region is a method of ArangoRDF extracted as a top-level function, so
# `self.__adb_col_statements` is NOT name-mangled here (mangling applies only
# inside a class body) and the attribute is literally "__adb_col_statements".
# ArangoRDFStub carries the two attributes the region touches:
#   self.adb_col_uri          -- URIRef("http://www.arangodb.com/collection"),
#                                as set in ArangoRDF.__init__
#   self.__adb_col_statements -- the rdflib Graph of (s, adb_col_uri, "col")
#                                statements the method adds to and removes from
# __eq__ is the oracle, not behaviour of the original class: the harness
# compares the receiver argument of the two runs, and two graphs built in two
# module namespaces are equal only up to RDF isomorphism.
from rdflib import Graph, URIRef

ADB_COL_URI = URIRef("http://www.arangodb.com/collection")

# arango_rdf/typings.py — only RDFTerm is used by the region (an annotation).
RDFTerm = URIRef
ADBDocs = ADBMetagraph = Json = PredicateScope = object
RDFListData = RDFListHeads = RDFTermMeta = TypeMap = object


class ArangoRDFStub:
    def __init__(self):
        self.adb_col_uri = ADB_COL_URI
        setattr(self, "__adb_col_statements", Graph())

    def statements(self):
        return getattr(self, "__adb_col_statements")

    def __eq__(self, other):
        from rdflib.compare import isomorphic
        return (isinstance(other, ArangoRDFStub)
                and self.adb_col_uri == other.adb_col_uri
                and isomorphic(self.statements(), other.statements()))

    def __repr__(self):
        return f"ArangoRDFStub({sorted(map(str, self.statements()))})"
