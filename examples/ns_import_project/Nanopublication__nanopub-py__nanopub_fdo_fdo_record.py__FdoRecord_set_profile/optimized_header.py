# Extracted from Nanopublication/nanopub-py@05022dc4bc : nanopub/fdo/fdo_record.py
# region: FdoRecord.set_profile (lines 137-139, stratum ns_import_project)
# licence of the source repository: see meta.json
from typing import Union
from rdflib import URIRef
from rdflib.namespace import DCTERMS
from nanopub.namespaces import FDOC

def set_profile(self, uri: Union[str, URIRef], use_fdof: bool = False) -> None:
    self.tuples[FDOC.hasFdoProfile if use_fdof else DCTERMS.conformsTo] = URIRef(uri)
