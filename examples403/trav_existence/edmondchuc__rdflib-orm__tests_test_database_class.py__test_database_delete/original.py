# Extracted from edmondchuc/rdflib-orm@b278d9699b : tests/test_database_class.py
# region: test_database_delete (lines 115-124, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib_orm.db import Database, InvalidDBKeyTypeError
from tests import BASE_URI

def test_database_delete():
    """Ensure data is deleted."""
    g = Graph()
    Database.set_db(g, BASE_URI)
    db = Database.get_db()
    triple = (URIRef('s'), URIRef('p'), URIRef('o'))
    db.write(triple)
    assert triple in g.triples((None, None, None))
    db.delete(triple)
    assert triple not in g.triples((None, None, None))
