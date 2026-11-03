# Extracted from MaxBerktoldRWTH/BRICKbuilder@28f0710933 : src/app/ifc_populate_window.py
# region: IfcBrickAnnotator.rebuild_output_graph (lines 484-550, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib
from rdflib import Graph, Namespace, RDF

def rebuild_output_graph(self):
    """Clears and re-serializes components according to active configuration settings mapping definitions."""
    self.output_graph = graph = Graph()

    # Consistent prefix generation definitions
    base_inst = self.settings.value("ns_inst", "http://example.org/project#")
    if not str(base_inst).endswith(('#', '/')):
        base_inst = str(base_inst) + '#'

    ifc_inst_ns = Namespace(base_inst + "ifcInst:")
    brick_inst_ns = Namespace(base_inst + "brickInst:")
    bacnet_ns = Namespace("http://buildingsmart.org/bacnet#")
    bldg_ns = Namespace(base_inst + "bldg:")
    ifc_core_ns = Namespace(
        self.settings.value(
            "ns_ifc", "http://standards.buildingsmart.org/IFC/RELEASE/IFC4/Ontology#"
        )
    )

    # 1. Bind core standard and target custom namespaces
    for prefix, namespace in [("brick", self.BRICK), ("ref", self.REF), ("ifcInst", ifc_inst_ns),
                              ("brickInst", brick_inst_ns), ("bacnet", bacnet_ns),
                              ("bldg", bldg_ns), ("ifc", ifc_core_ns)]:
        graph.bind(prefix, namespace)

    # 2. Sequential structural iteration over individual items
    for data in self.annotations_registry.values():
        eq_uri = ifc_inst_ns[data["eq_guid"]]
        graph.add((eq_uri, RDF.type, ifc_core_ns[data.get("ifc_type") or "IfcSensor"]))

        pt_uri = brick_inst_ns[data["point_id"]]
        # Link Brick point to physical asset
        graph += [(pt_uri, RDF.type, self.BRICK[data["point_type"]]),
                  (pt_uri, self.BRICK.isPointOf, eq_uri)]

        # 3. Handle BACnet nested blank node structures
        if data.get("bacnet_name"):
            bacnet_bnode = rdflib.BNode()
            raw_type = (
                str(data.get("bacnet_type", ""))
                .lower()
                .replace("analoginput", "analog-input")
                .replace("analogvalue", "analog-value")
            )
            graph += [
                (pt_uri, self.REF.hasExternalReference, bacnet_bnode),
                (bacnet_bnode, RDF.type, self.REF.BACnetReference),
                (bacnet_bnode, bacnet_ns["object-identifier"],
                 rdflib.Literal(f"{raw_type},{data.get('bacnet_instance')}",
                                datatype=bacnet_ns.objectIdentifier)),
                (bacnet_bnode, bacnet_ns["object-name"], rdflib.Literal(data.get("bacnet_name"))),
                (bacnet_bnode, bacnet_ns.objectOf, bldg_ns["sample-device"]),
            ]
