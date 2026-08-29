# Extracted from MaxBerktoldRWTH/BRICKbuilder@28f0710933 : src/app/widgets.py
# region: Canvas.import_from_graph (lines 1861-1960, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
from PyQt5.QtCore import (
    Qt, QRectF, QPointF, pyqtSignal, QByteArray, QMimeData, QPoint
)
from PyQt5.QtGui import (
    QPen, QBrush, QColor, QIcon, QPixmap, QPainter, QDrag, QTransform
)
from src.app.items import EntityItem, ConnectionItem, PortItem, JointItem
from src.ontologies.namespaces import RDF, BLDG, REC, BRICK, BRICK_REF, VISU, BACNET, bind_namespaces, short_uuid
BRICK_RELATIONSHIPS = {
    "hasLocation": rdflib.BRICK.hasLocation,
    "isLocationOf": rdflib.BRICK.isLocationOf,
    "feeds": rdflib.BRICK.feeds,
    "isFedBy": rdflib.BRICK.isFedBy,
    "hasPoint": rdflib.BRICK.hasPoint,
    "isPointOf": rdflib.BRICK.isPointOf,
    "hasPart": rdflib.BRICK.hasPart,
    "isPartOf": rdflib.BRICK.isPartOf,
}

for conn_uri in g.subjects(rdflib.RDF.type, VISU.Connection):
    print(f"Processing connection: {conn_uri}")

    # Get source and target
    source_uri = g.value(conn_uri, VISU.sourceEntity)
    target_uri = g.value(conn_uri, VISU.targetEntity)

    if not source_uri or not target_uri:
        print(f"  - Skipping: Missing source or target")
        continue

    print(f"  - Connection from {source_uri} to {target_uri}")

    # Get the entity items
    source_item = loaded_entities.get(str(source_uri))
    target_item = loaded_entities.get(str(target_uri))

    if not source_item or not target_item:
        print(f"  - Skipping: Source or target not in loaded entities")
        continue

    # Create connection
    connection = ConnectionItem(source_item.port, target_item.port)
    print(f"  - Created connection between ports")

    # Set connection URI
    connection.instance_uri = conn_uri

    # Set relationship type
    rel_type_str = g.value(conn_uri, rdflib.URIRef(VISU + "relationshipType"))
    if rel_type_str:
        print(f"  - Setting relationship type: {rel_type_str}")
        for rel_name, rel_uri in BRICK_RELATIONSHIPS.items():
            if str(rel_uri) == str(rel_type_str):
                connection.set_relationship_type(rel_uri)
                print(f"  - Matched to known relationship: {rel_name}")
                # Track this relationship as processed
                processed_relationships.add((str(source_uri), str(rel_uri), str(target_uri)))
                break

    # Set color
    for color_node in g.objects(conn_uri, rdflib.URIRef(VISU + "color")):
        red_val = g.value(color_node, VISU.red, default=0)
        green_val = g.value(color_node, VISU.green, default=0)
        blue_val = g.value(color_node, VISU.blue, default=0)

        # Convert to integers regardless of value
        red = int(red_val)
        green = int(green_val)
        blue = int(blue_val)

        color = QColor(red, green, blue)
        print(f"  - Setting color: RGB({red}, {green}, {blue})")

        # Set line style
        style_val = g.value(conn_uri, VISU.lineStyle)
        line_style_val = Qt.SolidLine
        if style_val:
            line_style_val = Qt.PenStyle(int(style_val))
            print(f"  - Setting line style: {line_style_val}")

        # Set line width
        width_val = g.value(conn_uri, VISU.lineWidth, default=2)
        width = int(width_val) if width_val else 2
        print(f"  - Setting line width: {width}")

        # Apply pen
        pen = QPen(color, width, line_style_val, Qt.RoundCap, Qt.RoundJoin)
        connection.setPen(pen)

    # Add to scene
    self.scene.addItem(connection)
    visual_conn_count += 1

    # Load joints
    joint_data = []
    joint_count = 0
    for joint_node in g.objects(conn_uri, rdflib.URIRef(VISU + "hasJoint")):
        idx_val = g.value(joint_node, VISU.jointIndex)
        x_val = g.value(joint_node, VISU.x)
        y_val = g.value(joint_node, VISU.y)

        if idx_val is not None and x_val is not None and y_val is not None:
            idx = int(idx_val)
            x = float(x_val)
            y = float(y_val)
            joint_data.append((idx, x, y))
            joint_count += 1
            print(f"  - Found joint #{idx} at ({x}, {y})")

    # Sort joints by index
    joint_data.sort(key=lambda d: d[0])
    print(f"  - Adding {joint_count} joints to connection")

    # Add joints to connection
    for _, x, y in joint_data:
        connection.add_joint_at_point(QPointF(x, y))

    # Update connection visuals
    connection.update_position()
