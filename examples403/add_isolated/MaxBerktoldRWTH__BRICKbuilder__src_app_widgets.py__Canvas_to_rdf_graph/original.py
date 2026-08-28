# Extracted from MaxBerktoldRWTH/BRICKbuilder@28f0710933 : src/app/widgets.py
# region: Canvas.to_rdf_graph (lines 1602-1637, stratum add_isolated)
# licence of the source repository: see meta.json
import rdflib
from src.app.items import EntityItem, ConnectionItem, PortItem, JointItem
from src.ontologies.namespaces import RDF, BLDG, REC, BRICK, BRICK_REF, VISU, BACNET, bind_namespaces, short_uuid

for item in self.scene.items():
    if isinstance(item, ConnectionItem) and item.source_port and item.target_port:
        source_uri = item.get_source_entity_uri()
        target_uri = item.get_target_entity_uri()

        if source_uri and target_uri:
            g.add((source_uri, item.relationship_type, target_uri))

            g.add((item.instance_uri, rdflib.RDF.type, VISU.Connection))
            g.add((item.instance_uri, VISU.sourceEntity, source_uri))
            g.add((item.instance_uri, VISU.targetEntity, target_uri))
            g.add((item.instance_uri, VISU.relationshipType, item.relationship_type))

            color = item.pen().color()
            color_node = rdflib.BNode()

            g.add((item.instance_uri, VISU.color, color_node))
            g.add((color_node, VISU.red, rdflib.Literal(color.red(), datatype=rdflib.XSD.integer)))
            g.add((color_node, VISU.green, rdflib.Literal(color.green(), datatype=rdflib.XSD.integer)))
            g.add((color_node, VISU.blue, rdflib.Literal(color.blue(), datatype=rdflib.XSD.integer)))

            pen_style = item.pen().style()
            g.add((item.instance_uri, VISU.lineStyle,
                   rdflib.Literal(int(pen_style), datatype=rdflib.XSD.integer)))

            pen_width = item.pen().width()
            g.add((item.instance_uri, VISU.lineWidth, rdflib.Literal(pen_width, datatype=rdflib.XSD.integer)))

            for i, joint in enumerate(item.joints):
                joint_node = rdflib.BNode()
                g.add((item.instance_uri, VISU.hasJoint, joint_node))
                g.add((joint_node, VISU.jointIndex, rdflib.Literal(i, datatype=rdflib.XSD.integer)))

                joint_pos = joint.scenePos()
                g.add((joint_node, VISU.x, rdflib.Literal(float(joint_pos.x()), datatype=rdflib.XSD.float)))
                g.add((joint_node, VISU.y, rdflib.Literal(float(joint_pos.y()), datatype=rdflib.XSD.float)))
