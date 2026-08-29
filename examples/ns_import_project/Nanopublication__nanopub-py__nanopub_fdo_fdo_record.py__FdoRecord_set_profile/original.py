# Extracted from Nanopublication/nanopub-py@05022dc4bc : nanopub/fdo/fdo_record.py
# region: FdoRecord.set_profile (lines 137-139, stratum ns_import_project)
# licence of the source repository: see meta.json
from typing import Optional, Union, List
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, DCTERMS, PROV
from nanopub.namespaces import FDOF, FDOC

def set_profile(self, uri: Union[str, URIRef], use_fdof: bool = False) -> None:
    pred = FDOC.hasFdoProfile if use_fdof else DCTERMS.conformsTo
    self.tuples[pred] = URIRef(uri)
