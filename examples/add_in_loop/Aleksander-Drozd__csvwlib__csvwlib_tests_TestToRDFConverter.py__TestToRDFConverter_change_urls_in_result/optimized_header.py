# Extracted from Aleksander-Drozd/csvwlib@6359de9b32 : csvwlib/tests/TestToRDFConverter.py
# region: TestToRDFConverter.change_urls_in_result (lines 29-42, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import URIRef

def change_urls_in_result(self, graph):
    for triple in graph.triples((None, None, None)):
        new_triple = tuple(URIRef(term.replace(self._remote_tests_location, self._tests_location))
                           if self._remote_tests_location in term else term for term in triple)
        if new_triple != triple:
            graph.remove(triple)
            graph.add(new_triple)
