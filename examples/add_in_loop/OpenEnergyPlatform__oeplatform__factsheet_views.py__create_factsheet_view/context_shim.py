# Context shim (see meta.json): what the loop of create_factsheet_view
# (OpenEnergyPlatform/oeplatform@ff28ef6390, factsheet/views.py) has in scope,
# so that it executes outside the Django project.
#
#   * the namespaces of factsheet/oekg/namespaces.py (the real IRIs);
#   * remove_non_printable and serialize_publication_date of
#     factsheet/utils.py, reduced to what the loop calls (the second is only
#     imported, never called by this region);
#   * the loop's three free variables, which are locals of the enclosing view
#     and were not captured by the extraction: `bundle` (the graph under
#     construction, holding the study node), `study_URI`, and `_publications`
#     (the publications of the factsheet as the front end sends them: a list
#     of dicts).  The dicts below span the branches of the loop.
#
# Identical bindings for both representations.
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, XSD  # noqa: F401

DC = Namespace("http://purl.org/dc/terms/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
OEKG = Namespace("https://openenergyplatform.org/ontology/oekg/")
OEO = Namespace("https://openenergyplatform.org/ontology/oeo/")


def remove_non_printable(text):
    return "".join(ch for ch in text if ch.isprintable())


def serialize_publication_date(date):
    return date


study_URI = URIRef("https://openenergyplatform.org/ontology/oekg/study/s1")

bundle = Graph()
bundle.add((study_URI, RDF.type, OEO.OEO_00020011))

_publications = [
    # every optional field present; a control character in the title
    {"id": "p1", "report_title": "Energy \x00 report\x07",
     "authors": [{"iri": "author/a1"}, {"iri": "author/a2"}],
     "doi": "10.1000/xyz", "date_of_publication": "2020-05-01T10:00:00",
     "link_to_study_report": "https://example.org/reports/p1.pdf"},
    # every optional field empty: only the id, the type and the study link
    {"id": "p2", "report_title": "", "authors": [], "doi": "",
     "date_of_publication": "", "link_to_study_report": ""},
    # the placeholder date is skipped; a shared author is added once
    {"id": "p3", "report_title": "Second", "authors": [{"iri": "author/a2"}],
     "doi": "", "date_of_publication": "01-01-1900",
     "link_to_study_report": ""},
    # a date that is not an xsd:dateTime lexical form; a doi that is None
    # (the original then writes the literal "None")
    {"id": "p4", "report_title": "Third", "authors": [{"iri": "author/a3"}],
     "doi": None, "date_of_publication": "2021-03-04",
     "link_to_study_report": "https://example.org/reports/p4.pdf"},
]
