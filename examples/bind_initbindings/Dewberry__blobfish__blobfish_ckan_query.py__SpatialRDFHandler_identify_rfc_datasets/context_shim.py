# Context shim (see meta.json): the names that
# SpatialRDFHandler.identify_rfc_datasets (Dewberry/blobfish@db89f34228,
# blobfish/ckan/query.py) takes from its package, so the method executes
# outside it. Identical bindings for both representations.
#
#  * RFC_SHP_URL, CKAN_URL, SF, GEOF: blobfish/ckan/const.py, verbatim.
#  * AORC: blobfish/pyrdf/_AORC.py defines a DefinedNamespace whose _NS is
#    the IRI below; a plain Namespace of that IRI stands in for it.
#  * Point, Polygon, MultiPolygon: `shapely` is not installed in the study
#    venv; Point keeps the one thing the region uses (.wkt).
#  * SpatialRDFHandler: only `graph` and `prepend_crs` (verbatim) of the
#    class, which the region reads through `self`.
from rdflib import Graph, Literal, Namespace
from rdflib.namespace._GEO import GEO

CKAN_URL = "https://ckan.dewberryanalytics.com"
RFC_SHP_URL = "https://www.weather.gov/source/gis/Shapefiles/Misc/rf12ja05.zip"
SF = Namespace("http://www.opengis.net/ont/sf#")
GEOF = Namespace("http://www.opengis.net/def/function/geosparql/")
AORC = Namespace("https://github.com/Dewberry/blobfish/blob/aorc_refactor/semantics/rdf/aorc.ttl#")


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @property
    def wkt(self):
        return f"POINT ({self.x} {self.y})"


class Polygon:
    pass


class MultiPolygon:
    pass


class SpatialRDFHandler:
    def __init__(self):
        self.graph = Graph()

    @staticmethod
    def prepend_crs(input_wkt: str) -> Literal:
        wkt_with_crs = f"<http://www.opengis.net/def/crs/OGC/1.3/CRS84> {input_wkt}"
        literal = Literal(wkt_with_crs, datatype=GEO.wktLiteral)
        return literal
