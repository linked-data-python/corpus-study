"""Context shim (see meta.json) for the virtuoso-python mapping test.

The region under evaluation is one method of
`virtuoso/tests/test_mapping.py::TestMapping`.  Running it for real needs a
live OpenLink Virtuoso server, SQLAlchemy, sqla_rdfbridge and nose: the test
declares an RDF quad-storage over SQL tables, inserts two rows and then reads
the resulting named graph back through the `Virtuoso` rdflib store.

None of that is available in the evaluation environment, so this module
provides the *smallest* stand-ins that let the region's own statements run:

  * `Session` / `session.add` / `session.commit` -- an in-memory stand-in for
    the SQLAlchemy session; committing materialises the rows as the quad map
    would (``tst:tA/1 a tst:tA``, ``tst:tB/1 tst:alink tst:tA/1``);
  * `A` / `B` -- stand-ins for the two declarative classes;
  * `TestContext` -- stand-in for the `TestMapping` instance (`self`),
    carrying `store` and `graphname` in place of the Virtuoso store.

It is imported IDENTICALLY by original.py and translated.ldpy, so the
comparison remains a comparison of the two representations.  What it really
exercises is the one term the translation changes: `TST.alink` / `tst:alink`.
"""

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib.plugins.stores.memory import Memory

TST = Namespace("http://example.com/test#")


class _Mapped(object):
    """Stand-in for a sqlalchemy declarative instance."""

    iri = None

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class A(_Mapped):
    pass


class B(_Mapped):
    a = None


class Session(object):
    """In-memory stand-in for sqlalchemy.orm.sessionmaker(bind=engine)()."""

    def __init__(self, autocommit=False):
        self.autocommit = autocommit
        self.pending = []
        self.counters = {}
        self.target = Graph()          # replaced by TestContext

    def add(self, obj):
        self.pending.append(obj)

    def commit(self):
        # ids are handed out in insertion order, per class, exactly as the
        # SQL sequences would; the IRIs follow the VirtuosoPatternIriClass
        # templates of the test module ('http://example.com/test#tA/%d').
        for obj in self.pending:
            name = type(obj).__name__
            self.counters[name] = self.counters.get(name, 0) + 1
            obj.iri = URIRef("http://example.com/test#t%s/%d"
                             % (name, self.counters[name]))
        for obj in self.pending:
            self.target.add((obj.iri, RDF.type, TST["t" + type(obj).__name__]))
            linked = getattr(obj, "a", None)
            if linked is not None:
                self.target.add((obj.iri, TST.alink, linked.iri))
        self.pending = []


class TestContext(object):
    """Stand-in for the `self` of TestMapping (quad storage + named graph)."""

    graphname = TST.g

    def __init__(self, session):
        self.session = session
        self.store = Memory()
        session.target = Graph(self.store, identifier=self.graphname)

    def create_qs_graph(self):
        return "qs", "g", "cpe"

    def declare_qs_graph(self, qs):
        return "shim: %s declaration clause (no Virtuoso server)" % (qs,)
