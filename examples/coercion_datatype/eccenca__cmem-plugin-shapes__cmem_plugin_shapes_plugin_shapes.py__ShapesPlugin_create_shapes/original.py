# Extracted from eccenca/cmem-plugin-shapes@52d5b16c05 : cmem_plugin_shapes/plugin_shapes.py
# region: ShapesPlugin.create_shapes (lines 395-446, stratum coercion_datatype)
# licence of the source repository: see meta.json
from uuid import NAMESPACE_URL, uuid5
from rdflib import DCTERMS, RDF, RDFS, SH, XSD, Graph, Literal, Namespace, URIRef
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
