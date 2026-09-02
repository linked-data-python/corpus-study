# Extracted from eccenca/cmem-plugin-shapes@52d5b16c05 : cmem_plugin_shapes/plugin_shapes.py
# region: ShapesPlugin.create_shapes (lines 395-446, stratum coercion_datatype)
# licence of the source repository: see meta.json
from types import SimpleNamespace
from uuid import NAMESPACE_URL, uuid5
from rdflib import DCTERMS, RDF, RDFS, SH, XSD, Graph, Literal, Namespace, URIRef
from context_shim import format_namespace  # context shim, see meta.json
SHUI = Namespace("https://vocab.eccenca.com/shui/")

def create_shapes(self) -> None:
    """Create SHACL node and property shapes"""
    class_uuids = set()
    prop_uuids = set()
    for cls, properties in self.get_class_dict().items():
        class_uuid = uuid5(NAMESPACE_URL, cls)
        node_shape_uri = URIRef(f"{format_namespace(self.shapes_graph_iri)}{class_uuid}")

        if class_uuid not in class_uuids:
            self.shapes_count += 1
            self.shapes_graph.add((node_shape_uri, RDF.type, SH.NodeShape))
            self.shapes_graph.add((node_shape_uri, SH.targetClass, URIRef(cls)))
            name = self.get_name(cls)
            self.shapes_graph.add((node_shape_uri, SH.name, Literal(name, lang="en")))
            self.shapes_graph.add((node_shape_uri, RDFS.label, Literal(name, lang="en")))
            class_uuids.add(class_uuid)

        for prop in properties:
            prop_uuid = uuid5(
                NAMESPACE_URL, f"{prop['property']}{'inverse' if prop['inverse'] else ''}"
            )
            property_shape_uri = URIRef(f"{format_namespace(self.shapes_graph_iri)}{prop_uuid}")
            if prop_uuid not in prop_uuids:
                self.shapes_count += 1
                name = self.get_name(prop["property"])
                self.shapes_graph.add((property_shape_uri, RDF.type, SH.PropertyShape))
                self.shapes_graph.add((property_shape_uri, SH.path, URIRef(prop["property"])))
                self.shapes_graph.add(
                    (property_shape_uri, SH.nodeKind, SH.Literal if prop["data"] else SH.IRI)
                )
                self.shapes_graph.add(
                    (
                        property_shape_uri,
                        SHUI.showAlways,
                        Literal("true", datatype=XSD.boolean),
                    )
                )
                if prop["inverse"]:
                    self.shapes_graph.add(
                        (
                            property_shape_uri,
                            SHUI.inversePath,
                            Literal("true", datatype=XSD.boolean),
                        )
                    )
                    name = "← " + name
                self.shapes_graph.add((property_shape_uri, SH.name, Literal(name, lang="en")))
                self.shapes_graph.add(
                    (property_shape_uri, RDFS.label, Literal(name, lang="en"))
                )
                prop_uuids.add(prop_uuid)
            self.shapes_graph.add((node_shape_uri, SH.property, property_shape_uri))


# Demo harness (identical on both sides, see meta.json): create_shapes is a
# bound-method extraction -- ShapesPlugin is the enclosing class, defined
# outside the extracted region, and the region only reaches through
# self.shapes_graph / self.shapes_graph_iri / self.shapes_count and two self
# methods: self.get_class_dict() (a SPARQL SELECT over the plugin's data
# graph in the real plugin) and self.get_name(iri) (a network call to
# Corporate Memory's /explore/title endpoint). Neither exists here, so
# `self` stands in as a SimpleNamespace exposing exactly what the region
# reads, with get_class_dict/get_name as plain stub callables returning
# fixed data instead of a network/SPARQL endpoint. demo() calls
# create_shapes(self) and returns self.shapes_graph, not self (comparing the
# stub instance itself would need an __eq__ for no benefit, since only the
# graph is the observable effect).
def demo(class_dict):
    def get_name(iri):
        return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]

    self = SimpleNamespace(
        shapes_graph=Graph(),
        shapes_graph_iri="https://example.org/shapes",
        shapes_count=0,
        get_class_dict=lambda: class_dict,
        get_name=get_name,
    )
    create_shapes(self)
    return self.shapes_graph
