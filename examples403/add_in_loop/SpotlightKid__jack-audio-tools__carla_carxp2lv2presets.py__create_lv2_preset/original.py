# Extracted from SpotlightKid/jack-audio-tools@a64f1f86ba : carla/carxp2lv2presets.py
# region: create_lv2_preset (lines 48-75, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, BNode, URIRef
from rdflib.namespace import Namespace, NamespaceManager, RDF, RDFS, XSD

def create_lv2_preset(label, plugin):
    graph = get_graph()
    preset = URIRef('')
    graph.add((preset, RDF.type, NS.pset.Preset))
    graph.add((preset, NS.lv2.appliesTo, URIRef(plugin.uri)))
    graph.add((preset, RDFS.label, Literal(label)))

    for param in plugin.params:
        port = BNode()
        graph.add((port, NS.lv2.symbol, Literal(param.symbol)))
        graph.add((port, NS.pset.value, Literal(param.value)))
        graph.add((preset, NS.lv2.port, port))

    if plugin.properties:
        state = BNode()

        for prop in plugin.properties.values():
            if prop.type == str(NS.atom.Path):
                value = URIRef(prop.value)
            else:
                # XXX: handle other Atom types?
                value = Literal(prop.value)

            graph.add((state, URIRef(prop.key), value))

        graph.add((preset, NS.state.state, state))

    return graph.serialize(format='turtle')
