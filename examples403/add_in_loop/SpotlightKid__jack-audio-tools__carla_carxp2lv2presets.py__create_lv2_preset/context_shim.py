# Context shim (see meta.json), for
# SpotlightKid/jack-audio-tools@a64f1f86ba : carla/carxp2lv2presets.py.
#
# NS and get_graph() are module-level definitions in that file (lines 23-45),
# just above the extracted region (create_lv2_preset, lines 48-75) -- outside
# its line range, so extraction did not capture them. Copied verbatim.
#
# Param/Property/PluginInstance are minimal stand-ins for the @dataclass
# definitions in carla/loadcarxp.py (Param lines 34-41, Property lines 44-48,
# PluginInstance lines 51-59), reduced to the fields create_lv2_preset reads
# (`.params`, `.properties`, `.uri` on the plugin; `.symbol`/`.value` on each
# param; `.type`/`.key`/`.value` on each property). Note: loadcarxp.py types
# Property.key as `int`, but parse_carxp() (lines 117-128 of that file)
# actually stores the CustomData `<Key>` element's text -- a string, used
# directly as a URI -- so `key: str` here matches what create_lv2_preset
# really receives, not the (misleading) declared type.
#
# Identical bindings for both representations.
import rdflib
from dataclasses import dataclass, field
from rdflib import Graph
from rdflib.namespace import NamespaceManager


class NS:
    atom = rdflib.Namespace('http://lv2plug.in/ns/ext/atom#')
    lv2 = rdflib.Namespace('http://lv2plug.in/ns/lv2core#')
    patch = rdflib.Namespace('http://lv2plug.in/ns/ext/patch#')
    pset = rdflib.Namespace('http://lv2plug.in/ns/ext/presets#')
    state = rdflib.Namespace('http://lv2plug.in/ns/ext/state#')

    @classmethod
    def bind_all(cls, nsmanager):
        for name in dir(cls):
            ns = getattr(cls, name)
            if isinstance(ns, rdflib.Namespace):
                nsmanager.bind(name, ns, override=True, replace=True)


def get_graph():
    graph = Graph()
    NS.bind_all(NamespaceManager(graph))
    return graph


@dataclass
class Param:
    symbol: str
    value: float


@dataclass
class Property:
    type: str
    key: str
    value: str


@dataclass
class PluginInstance:
    uri: str
    params: list = field(default_factory=list)
    properties: dict = field(default_factory=dict)
