# Extracted from Nanopublication/nanopub-py@05022dc4bc : nanopub/trustyuri/rdf/RdfPreprocessor.py
# region: transform (lines 20-29, band medium)
# licence of the source repository: see meta.json
from rdflib.term import BNode, URIRef
from nanopub.trustyuri.rdf import RdfUtils

def transform(uri, hashstr, baseuri, bnodemap):
    if uri is None:
        return None

    if baseuri is None:
        try:
            return URIRef(RdfUtils.normalize(uri, hashstr).decode('utf-8'))
        except Exception:
            return URIRef(RdfUtils.normalize(uri, hashstr))
    return RdfUtils.get_trustyuri(uri, baseuri, hashstr, bnodemap)
