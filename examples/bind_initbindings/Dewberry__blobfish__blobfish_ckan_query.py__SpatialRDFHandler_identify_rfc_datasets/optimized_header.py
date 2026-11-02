# Extracted from Dewberry/blobfish@db89f34228 : blobfish/ckan/query.py
# region: SpatialRDFHandler.identify_rfc_datasets (lines 101-118, stratum bind_initbindings)
# licence of the source repository: see meta.json
from context_shim import Point, GEOF, AORC
from rdflib import RDF, DCTERMS
from rdflib.namespace._GEO import GEO
from rdflib.query import Result

def identify_rfc_datasets(self, x: float, y: float) -> Result:
    raise NotImplementedError("This function relies on geosparql functions which are not implemented in the SPARQL processor for RDFLib")
    query = """
    SELECT  ?s3
    WHERE   {
        ?r rdf:type aorc:RFC .
        ?r dct:spatial/geosparql:hasGeometry ?g .
        ?g geosparql:asWKT ?w .
        ?r ^aorc:hasRFC ?p .
        ?p dcat:dataset ?sda .
        ?sda ^aorc:hasSourceDataset ?s3 .
        FILTER (geof:sfWithin(?p, ?w))
    }
    """
    return self.graph.query(query, initNs={"rdf": RDF, "aorc": AORC, "dct": DCTERMS, "geosparql": GEO, "geof": GEOF}, initBindings={"p": self.prepend_crs(Point(x, y).wkt)})
