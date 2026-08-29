# Extracted from enricocirignaco/infrastructureforsensormanagment@2aa301380c : src/webapp-backend/app/repositories/sensor_node_repository.py
# region: SensorNodeRepository.create_sensor_node (lines 19-78, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from app.models.sensor_node import SensorNodeDB, SensorNodeOutSlim, SensorNodeLocation, SensorNodeStateEnum, ConfigurableAssignment, ConfigurableTypeEnum, SensorNodeLogbookEntry, SensorNodeLogbookEnum, TimeseriesData, TimeseriesField
from rdflib import Graph, URIRef, Literal, RDF

def create_sensor_node(self, sensor_node: SensorNodeDB) -> SensorNodeDB:
    g = Graph()
    g.bind('schema', self.schema)
    g.bind('bfh', self.bfh)

    sensor_uri = URIRef(f"http://data.bfh.ch/sensorNodes/{sensor_node.uuid}")

    # Basisdaten
    g.add((sensor_uri, RDF.type, URIRef(self.bfh + "SensorNode")))
    g.add((sensor_uri, URIRef(self.bfh + "identifier"), Literal(str(sensor_node.uuid))))
    g.add((sensor_uri, URIRef(self.schema + "name"), Literal(sensor_node.name)))
    if sensor_node.description:
        g.add((sensor_uri, URIRef(self.schema + "description"), Literal(sensor_node.description)))
    g.add((sensor_uri, URIRef(self.bfh + "state"), URIRef(sensor_node.state.rdf_uri)))
    g.add((sensor_uri, URIRef(self.bfh + "ttnDeviceLink"), Literal(str(sensor_node.ttn_device_link))))
    g.add((sensor_uri, URIRef(self.bfh + "gitlabRef"), Literal(sensor_node.gitlab_ref)))

    # Standort
    if sensor_node.location.latitude is not None:
        g.add((sensor_uri, URIRef(self.bfh + "latitude"), Literal(sensor_node.location.latitude)))
    if sensor_node.location.longitude is not None:
        g.add((sensor_uri, URIRef(self.bfh + "longitude"), Literal(sensor_node.location.longitude)))
    if sensor_node.location.altitude is not None:
        g.add((sensor_uri, URIRef(self.bfh + "altitude"), Literal(sensor_node.location.altitude)))
    if sensor_node.location.postalcode:
        g.add((sensor_uri, URIRef(self.bfh + "postalcode"), Literal(sensor_node.location.postalcode)))

    # Verlinkung zum NodeTemplate
    g.add((sensor_uri, URIRef(self.bfh + "usesNodeTemplate"),
        URIRef(f"http://data.bfh.ch/nodeTemplates/{sensor_node.node_template_uuid}")))

    # Verlinkung zum Projekt
    g.add((sensor_uri, URIRef(self.bfh + "partOfProject"),
        URIRef(f"http://data.bfh.ch/projects/{sensor_node.project_uuid}")))

    # Configurables
    for idx, conf in enumerate(sensor_node.configurables):
        conf_uri = URIRef(f"{sensor_uri}/configurable/{idx}")
        g.add((sensor_uri, URIRef(self.bfh + "hasConfigurable"), conf_uri))
        g.add((conf_uri, RDF.type, URIRef(self.bfh + "ConfigurableAssignment")))
        g.add((conf_uri, URIRef(self.schema + "name"), Literal(conf.name)))
        g.add((conf_uri, URIRef(self.bfh + "type"), URIRef(conf.type.rdf_uri)))
        g.add((conf_uri, URIRef(self.schema + "value"), Literal(conf.value)))
        if conf.display_value:
            g.add((conf_uri, URIRef(self.bfh + "displayValue"), Literal(conf.display_value)))

    # Logbuch
    for idx, entry in enumerate(sensor_node.logbook):
        log_uri = URIRef(f"{sensor_uri}/log/{idx}")
        g.add((sensor_uri, URIRef(self.bfh + "hasLogEntry"), log_uri))
        g.add((log_uri, RDF.type, URIRef(self.bfh + "LogEntry")))
        g.add((log_uri, URIRef(self.bfh + "logType"), Literal(entry.type.value)))
        g.add((log_uri, URIRef(self.schema + "dateCreated"), Literal(entry.date.isoformat())))
        g.add((log_uri, URIRef(self.schema + "creator"), URIRef(f"http://data.bfh.ch/users/{entry.user.uuid}")))

    # Persistiere Graph
    query = f"""INSERT DATA {{ {g.serialize(format='nt')} }}"""
    self.triplestore_client.update(query)

    return self.find_sensor_node_by_uuid(sensor_node.uuid)
