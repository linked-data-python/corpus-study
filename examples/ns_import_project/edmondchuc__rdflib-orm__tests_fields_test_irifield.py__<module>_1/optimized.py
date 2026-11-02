# Extracted from edmondchuc/rdflib-orm@b278d9699b : tests/fields/test_irifield.py
# region: <module> (lines 1-84, stratum ns_import_project)
# licence of the source repository: see meta.json
import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL

from orm_context import models, Database, BASE_URI


def test_required_field_raises():
    class TestModel(models.Model):
        class_type = models.IRIField(RDF.type, OWL.Thing)
        irifield = models.IRIField(RDF.value, required=True)

    with pytest.raises(models.FieldError):
        TestModel(uri='test')


def test_irifield_create():
    class TestModel(models.Model):
        class_type = models.IRIField(RDF.type, OWL.Thing)
        irifield = models.IRIField(RDF.value)

    assert TestModel(uri='test', irifield='123').irifield == '123'


def test_irifield_convert_to_rdf():
    g = Graph()
    Database.set_db(g, base_uri=BASE_URI)

    class TestModel(models.Model):
        class_type = models.IRIField(RDF.type, OWL.Thing)
        irifield = models.IRIField(RDF.value)

    TestModel(uri='test', irifield='123').save()
    assert g.value(BASE_URI.test, RDF.value) == URIRef('123')


def test_irifield_convert_to_rdf_none():
    g = Graph()
    Database.set_db(g, base_uri=BASE_URI)

    class TestModel(models.Model):
        class_type = models.IRIField(RDF.type, OWL.Thing)
        irifield = models.IRIField(RDF.value)

    TestModel(uri='test', irifield=None).save()
    assert g.value(BASE_URI.test, RDF.value) is None


def test_irifield_convert_to_rdf_list_value():
    g = Graph()
    Database.set_db(g, base_uri=BASE_URI)

    class TestModel(models.Model):
        class_type = models.IRIField(RDF.type, OWL.Thing)
        irifield = models.IRIField(RDF.value, many=True)

    TestModel(uri='test', irifield=['123', '456']).save()
    assert set(g.objects(BASE_URI.test, RDF.value)) == {URIRef('123'), URIRef('456')}


def test_irifield_convert_to_rdf_list_value_raises():
    Database.set_db(Graph(), base_uri=BASE_URI)

    class TestModel(models.Model):
        class_type = models.IRIField(RDF.type, OWL.Thing)
        irifield = models.IRIField(RDF.value, many=True)

    model = TestModel(uri='test', irifield='123')
    with pytest.raises(models.FieldError):
        model.save()
