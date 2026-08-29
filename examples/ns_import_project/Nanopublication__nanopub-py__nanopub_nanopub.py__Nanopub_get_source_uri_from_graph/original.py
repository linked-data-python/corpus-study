# Extracted from Nanopublication/nanopub-py@05022dc4bc : nanopub/nanopub.py
# region: Nanopub.get_source_uri_from_graph (lines 473-487, stratum ns_import_project)
# licence of the source repository: see meta.json
import re
from typing import Any, List, Optional, Union, Tuple
from rdflib import RDF, Literal
from nanopub.namespaces import HYCL, NP, NPX, NTEMPLATE, ORCID, PAV

@property
def get_source_uri_from_graph(self) -> Optional[str]:
    """Get the source URI of the nanopublication from the header.

    This is usually something like: http://purl.org/np/RAnksi2yDP7jpe7F6BwWCpMOmzBEcUImkAKUeKEY_2Yus
    """
    for s, _, _, _ in self._rdf.quads((None, RDF.type, NP.Nanopublication, None)):
        extract_trusty = re.search(
            r'^[a-z0-9+.-]+:\/\/[a-zA-Z0-9\/._-]+\/(RA.*)$',
            str(s),
            re.IGNORECASE
        )
        if extract_trusty:
            return str(s)
    return None
