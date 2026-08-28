# Extracted from enricocirignaco/infrastructureforsensormanagment@2aa301380c : src/webapp-backend/app/repositories/node_template_repository.py
# region: NodeTemplateRepository.create_node_template (lines 21-74, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from app.models.node_template import (
    NodeTemplateDB, ProtobufDatatypeEnum, NodeTemplateOutSlim, NodeTemplateLogbookEnum, NodeTemplateLogbookEntry, NodeTemplateStateEnum, NodeTemplateField, ConfigurableDefinition, HardwareBoard, ConfigurableTypeEnum, ProtobufSchema, ProtobufSchemaField)
from rdflib import Graph, URIRef, Literal, RDF, Namespace, XSD

def create_node_template(self, node_template: NodeTemplateDB) -> NodeTemplateDB:
    g = Graph()
    g.bind('schema', self.schema)
    g.bind('bfh', self.bfh)

    template_uri = URIRef(f"http://data.bfh.ch/nodeTemplates/{node_template.uuid}")

    # Basisdaten
    g.add((template_uri, RDF.type, URIRef(self.bfh + "NodeTemplate")))
    g.add((template_uri, URIRef(self.bfh + "identifier"), Literal(str(node_template.uuid))))
    g.add((template_uri, URIRef(self.schema + "name"), Literal(node_template.name)))
    g.add((template_uri, URIRef(self.schema + "description"), Literal(node_template.description)))
    g.add((template_uri, URIRef(self.schema + "url"), Literal(str(node_template.gitlab_url))))
    g.add((template_uri, URIRef(self.bfh + "state"), URIRef(node_template.state.rdf_uri)))
    g.add((template_uri, URIRef(self.bfh + "protobufMessageName"), Literal(f"Msg_{node_template.uuid.hex}")))

    # Board
    g.add((template_uri, URIRef(self.bfh + "boardCore"), Literal(node_template.board.core)))
    g.add((template_uri, URIRef(self.bfh + "boardVariant"), Literal(node_template.board.variant)))

    # Configurables
    for idx, conf in enumerate(node_template.configurables):
        conf_uri = URIRef(f"{template_uri}/configurable/{idx}")
        g.add((template_uri, URIRef(self.bfh + "hasConfigurable"), conf_uri))
        g.add((conf_uri, RDF.type, URIRef(self.bfh + "Configurable")))
        g.add((conf_uri, URIRef(self.schema + "name"), Literal(conf.name)))
        g.add((conf_uri, URIRef(self.bfh + "type"), URIRef(conf.type.rdf_uri)))

    # Felder
    for idx, field in enumerate(node_template.fields or []):
        field_uri = URIRef(f"{template_uri}/field/{idx}")
        g.add((template_uri, URIRef(self.bfh + "hasField"), field_uri))
        g.add((field_uri, RDF.type, URIRef(self.bfh + "Field")))
        g.add((field_uri, URIRef(self.bfh + "fieldName"), Literal(field.field_name)))
        g.add((field_uri, URIRef(self.bfh + "protobufDatatype"), URIRef(field.protbuf_datatype.rdf_uri)))
        g.add((field_uri, URIRef(self.bfh + "unit"), Literal(field.unit)))
        if field.commercial_sensor:
            sensor_uri = URIRef(f"http://data.bfh.ch/commercialSensors/{field.commercial_sensor.uuid}")
            g.add((field_uri, URIRef(self.bfh + "linkedCommercialSensor"), sensor_uri))

    # Logbuch
    for idx, entry in enumerate(node_template.logbook):
        log_uri = URIRef(f"{template_uri}/log/{idx}")
        g.add((template_uri, URIRef(self.bfh + "hasLogEntry"), log_uri))
        g.add((log_uri, RDF.type, URIRef(self.bfh + "LogEntry")))
        g.add((log_uri, URIRef(self.bfh + "logType"), Literal(entry.type.value)))
        g.add((log_uri, URIRef(self.schema + "dateCreated"), Literal(entry.date.isoformat())))
        g.add((log_uri, URIRef(self.schema + "creator"), URIRef(f"http://data.bfh.ch/users/{entry.user.uuid}")))

    # Persistiere Graph
    query = f"""INSERT DATA {{ {g.serialize(format='nt')} }}"""
    self.triplestore_client.update(query)

    return self.find_node_template_by_uuid(node_template.uuid)
