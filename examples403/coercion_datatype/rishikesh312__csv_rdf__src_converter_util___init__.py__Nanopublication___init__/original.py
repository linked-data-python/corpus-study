# Extracted from rishikesh312/csv_rdf@2daa5e3c23 : src/converter/util/__init__.py
# region: Nanopublication.__init__ (lines 158-247, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef
import os
import datetime
import uuid
namespaces = {}

def __init__(self, file_name):
    """
    Initialize the graphs needed for the nanopublication
    """
    super().__init__()

    # Virtuoso does not accept BNodes as graph names
    self.default_context = Graph(store=self.store,
                                 identifier=URIRef(uuid.uuid4().urn))


    # Assign default namespace prefixes
    for prefix, namespace in namespaces.items():
        self.bind(prefix, namespace)

    # Get the current date and time (UTC)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")

    # Obtain a hash of the source file used for the conversion.
    # TODO: Get this directly from GitLab
    source_hash = open_file_then_apply_git_hash(file_name)

    # Shorten the source hash to 8 digits (similar to Github)
    short_hash = source_hash[:8]

    # Determine a 'hash_part' for all timestamped URIs generated through
    # this procedure
    hash_part = f"{short_hash}/{timestamp}"

    # A URI that represents the version of the file being converted
    self.dataset_version_uri = SDR[source_hash]
    self.add((self.dataset_version_uri, SDV['path'],
              Literal(file_name, datatype=XSD.string)))
    self.add((self.dataset_version_uri, SDV['sha1_hash'],
              Literal(source_hash, datatype=XSD.string)))

    # ----
    # The nanopublication graph
    # ----
    name = (os.path.basename(file_name)).split('.')[0]
    self.uri = SDR[f"{name}/nanopublication/{hash_part}"]


    # The Nanopublication consists of three graphs
    assertion_graph_uri = SDR[f"{name}/assertion/{hash_part}"]
    provenance_graph_uri = SDR[f"{name}/provenance/{hash_part}"]
    pubinfo_graph_uri = SDR[f"{name}/pubinfo/{hash_part}"]

    self.ag = self.graph(assertion_graph_uri)
    self.pg = self.graph(provenance_graph_uri)
    self.pig = self.graph(pubinfo_graph_uri)

    # The nanopublication
    self.add((self.uri , RDF.type, NP['Nanopublication']))
    # The link to the assertion
    self.add((self.uri , NP['hasAssertion'], assertion_graph_uri))
    self.add((assertion_graph_uri, RDF.type, NP['Assertion']))
    # The link to the provenance graph
    self.add((self.uri , NP['hasProvenance'], provenance_graph_uri))
    self.add((provenance_graph_uri, RDF.type, NP['Provenance']))
    # The link to the publication info graph
    self.add((self.uri , NP['hasPublicationInfo'], pubinfo_graph_uri))
    self.add((pubinfo_graph_uri, RDF.type, NP['PublicationInfo']))

    # ----
    # The provenance graph
    # ----

    # Provenance information for the assertion graph (the data structure
    # definition itself)
    self.pg.add((assertion_graph_uri, PROV['wasDerivedFrom'],
                 self.dataset_version_uri))
    # self.pg.add((dataset_uri, PROV['wasDerivedFrom'],
    #              self.dataset_version_uri))
    self.pg.add((assertion_graph_uri, PROV['generatedAtTime'],
                 Literal(timestamp, datatype=XSD.dateTime)))

    # ----
    # The publication info graph
    # ----

    # The URI of the latest version of this converter
    # TODO: should point to the actual latest commit of this converter.
    # TODO: consider linking to this as the plan of some activity, rather
    # than an activity itself.
    clariah_uri = URIRef('https://github.com/CLARIAH/wp4-converters')

    self.pig.add((self.uri, PROV['wasGeneratedBy'], clariah_uri))
    self.pig.add((self.uri, PROV['generatedAtTime'],
                  Literal(timestamp, datatype=XSD.dateTime)))
