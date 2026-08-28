# Extracted from SoftwareHeritage/swh-indexer@95f3e65462 : swh/indexer/metadata_mapping/nuget.py
# region: NuGetMapping.normalize_tags (lines 86-88, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, BNode, Graph, Literal, URIRef

def normalize_tags(self, s):
    if isinstance(s, str):
        return [Literal(tag) for tag in s.split(" ")]
