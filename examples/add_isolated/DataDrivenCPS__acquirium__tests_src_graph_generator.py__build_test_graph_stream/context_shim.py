# Context shim (see meta.json): subset of
# src/acquirium/internals/internals_namespaces.py from
# DataDrivenCPS/acquirium@e3bffb4bed8d358aba1e24fe6f5b8f780ac06d61, trimmed
# to the names build_test_graph_stream actually reaches (ACQUIRIUM_NS,
# BRICK_REF, S223, QUDT and the predicate/class constants derived from
# them), so the region executes outside the package. Real IRIs, copied
# verbatim -- unlike the region's own draft note ("prefixes: RDF->rdf"),
# this file does not invent anything: every constant below is the actual
# binding at the pinned commit.
#
# Identical bindings for both representations.
from rdflib.namespace import Namespace

ACQUIRIUM_NS = Namespace("urn:acquirium#")
QUDT = Namespace("http://qudt.org/schema/qudt/")
S223 = Namespace("http://data.ashrae.org/standard223#")
BRICK_REF = Namespace("https://brickschema.org/schema/Brick/ref#")

HAS_EXTERNAL_REFERENCE = BRICK_REF.hasExternalReference
HAS_MEDIUM = S223.hasMedium
OF_SUBSTANCE = S223.ofSubstance
HAS_QUANTITY_KIND = QUDT.hasQuantityKind
HAS_UNIT = QUDT.hasUnit
DATA_SOURCE = ACQUIRIUM_NS.dataSource
MQTT_REFERENCE = BRICK_REF.MQTTReference
MQTT_BROKER = BRICK_REF.MQTTBroker
MQTT_TOPIC = BRICK_REF.MQTTTopic
TIME_KEY = ACQUIRIUM_NS.timeKey
VALUE_KEY = ACQUIRIUM_NS.valueKey
