# Extracted from statnett/KGraphPy@38859be62f : kgraphpy/header.py
# region: CIMMetadataHeader.from_manifest (lines 192-228, stratum ns_import_project)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import Graph, Node, URIRef, RDF, BNode, Literal
from rdflib.namespace import DCTERMS, NamespaceManager
from kgraphpy.namespaces import MD, collect_specific_namespaces


# Binding restoration (see meta.json): the region is a classmethod extracted
# without its enclosing class, so `cls` has no referent. CIMMetadataHeader
# here reproduces only the __init__ of the real class (subject, graph) --
# enough to build the object the extracted method returns -- and the trailing
# module-level alias makes `from_manifest` reachable as a plain callable for
# the driver, exactly as `self.graph`/parameter restoration is done for the
# other 163 regions missing their binding.
class CIMMetadataHeader:
    def __init__(self, subject=None, graph=None):
        self.subject = subject
        self.graph = graph if graph is not None else Graph()

    def __eq__(self, other):
        # Duck-typed, not isinstance(): original.py and translated.ldpy each
        # exec in their own namespace, so "the same class" is two distinct
        # class objects even with an identical body.
        return (hasattr(other, "subject") and hasattr(other, "graph")
                and self.subject == other.subject
                and set(self.graph) == set(other.graph))

    @classmethod
    def from_manifest(cls, file_path: str|Path, graph_uri: URIRef|str, format: str="trig") -> "CIMMetadataHeader":
        """Creates a header from a manifest file.

        The manifest file can contain headers for multiple graphs. The correct header is found by the graph id.

        Parameters:
            file_path (str|Path): Path to manifest file. The file must be a valid RDF file.
            graph_uri (URIRef|str): The identifier of the graph.
            format (str): The format of the manifest file. Default is "trig".

        Raises:
            ValueError: If no header triples matching the graph_uri is found.

        Returns:
            CIMMetadataHeader: The new header.
        """
        graph_uri = URIRef(graph_uri)

        manifest_graph = Graph()
        manifest_graph.parse(source=file_path, format=format)

        header_graph = Graph()
        for triple in manifest_graph.triples((graph_uri, None, None)):
            header_graph.add(triple)

        if len(header_graph) == 0:
            raise ValueError(f"No header triples matching graph identifier {graph_uri} found in manifest file.")

        nm = NamespaceManager(header_graph, bind_namespaces="none")
        used_namespaces = collect_specific_namespaces(list(header_graph), manifest_graph.namespace_manager)
        for prefix, ns_uri in used_namespaces.items():
            nm.bind(prefix, ns_uri, override=True)

        header_graph.namespace_manager = nm

        return cls(subject=graph_uri, graph=header_graph)


from_manifest = CIMMetadataHeader.from_manifest
