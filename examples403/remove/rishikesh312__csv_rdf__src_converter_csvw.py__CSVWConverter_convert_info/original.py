# Extracted from rishikesh312/csv_rdf@2daa5e3c23 : src/converter/csvw.py
# region: CSVWConverter.convert_info (lines 321-361, stratum remove)
# licence of the source repository: see meta.json
import iribaker
from .util import (patch_namespaces_to_disk, process_namespaces,
                   get_namespaces, Nanopublication, validateTerm,
                   parse_value, CSVW, PROV, DC, SKOS, RDF)
from rdflib import URIRef, Literal, Graph, BNode, XSD, Dataset
logger = logging.getLogger(__name__)

def convert_info(self):
    """Converts the CSVW JSON file to valid RDF for serializing into the Nanopublication publication info graph."""

    results = self.metadata_graph.query("""SELECT ?s ?p ?o
                                           WHERE { ?s ?p ?o .
                                                   FILTER(?p = csvw:valueUrl ||
                                                          ?p = csvw:propertyUrl ||
                                                          ?p = csvw:aboutUrl)}""")

    for (s, p, o) in results:
        # Use iribaker
        object_value = str(o)
        escaped_object = URIRef(iribaker.to_iri(object_value))
        # print(escaped_object)

        # If the escaped IRI of the object is different from the original,
        # update the graph.
        if escaped_object != o:
            self.metadata_graph.set((s, p, escaped_object))
            # Add the provenance of this operation.
            self.np.pg.add((escaped_object,
                        PROV.wasDerivedFrom,
                        Literal(object_value, datatype=XSD.string)))
            # print(str(o))

    #walk through the metadata graph to remove illigal "Resource" blank node caused by python3 transition.
    for s, p, o in self.metadata_graph.triples((None, None, None)):
        subject_value = str(s)
        if s.startswith("Resource("):
            self.metadata_graph.remove((s,p,o))
            self.metadata_graph.add((BNode(subject_value[9:-1]), p, o))
            logger.debug("removed a triple because it was not formatted right. (started with \"Resource\")")

    # Add the information of the schema file to the provenance graph of the
    # nanopublication
    self.np.ingest(self.metadata_graph, self.np.pg.identifier)

    # for s,p,o in self.np.triples((None,None,None)):
    #     print(s.__repr__,p.__repr__,o.__repr__)

    return
