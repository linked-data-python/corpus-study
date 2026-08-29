# Extracted from SoftwareHeritage/swh-indexer@95f3e65462 : swh/indexer/metadata_mapping/dart.py
# region: PubspecMapping._translate_author (lines 52-67, stratum coercion_datatype)
# licence of the source repository: see meta.json
import re
from rdflib import RDF, BNode, Graph, Literal, URIRef
from swh.indexer.namespaces import SCHEMA

def _translate_author(self, graph, s):
    name_email_re = re.compile("(?P<name>.*?)( <(?P<email>.*)>)")
    if isinstance(s, str):
        author = BNode()
        graph.add((author, RDF.type, SCHEMA.Person))
        match = name_email_re.search(s)
        if match:
            name = match.group("name")
            email = match.group("email")
            graph.add((author, SCHEMA.email, Literal(email)))
        else:
            name = s

        graph.add((author, SCHEMA.name, Literal(name)))

        return author
