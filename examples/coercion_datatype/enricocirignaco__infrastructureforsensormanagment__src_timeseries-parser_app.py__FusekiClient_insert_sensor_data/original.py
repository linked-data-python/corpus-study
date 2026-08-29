# Extracted from enricocirignaco/infrastructureforsensormanagment@2aa301380c : src/timeseries-parser/app.py
# region: FusekiClient.insert_sensor_data (lines 198-222, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, RDF, Namespace, XSD, SOSA
from uuid import uuid4
from datetime import datetime

def insert_sensor_data(self, device_id, timestamp, sensor_values):
    time_str = datetime.fromisoformat(timestamp).isoformat()
    observation_id = str(uuid4())

    g = Graph()
    g.bind("sosa", SOSA)
    g.bind("xsd", XSD)
    bfh = Namespace("http://data.bfh.ch/")
    g.bind("bfh", bfh)

    observation_uri = URIRef(f"http://data.bfh.ch/observations/{observation_id}")

    g.add((observation_uri, RDF.type, URIRef(SOSA.Observation)))
    g.add((observation_uri, SOSA.madeBySensor, URIRef(f"http://data.bfh.ch/sensorNodes/{device_id}")))
    g.add((observation_uri, SOSA.resultTime, Literal(time_str, datatype=XSD.dateTime)))

    for key, value in sensor_values.items():
        result_uri = URIRef(f"http://data.bfh.ch/results/{observation_id}_{key}")
        g.add((observation_uri, SOSA.hasResult, result_uri))
        g.add((result_uri, RDF.type, URIRef(SOSA.Result)))
        g.add((result_uri, bfh.fieldName, Literal(key)))
        g.add((result_uri, SOSA.hasSimpleResult, Literal(value)))

    query = f"""INSERT DATA {{ {g.serialize(format='nt')} }}"""
    self._execute_update(query)
