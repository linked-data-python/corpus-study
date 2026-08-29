# Extracted from SpotlightKid/jack-audio-tools@a64f1f86ba : carla/carxp2lv2presets.py
# region: create_lv2_preset (lines 48-75, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, BNode, URIRef
from rdflib.namespace import Namespace, NamespaceManager, RDF, RDFS, XSD
from context_shim import NS, get_graph

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


# Demo harness (identical on both sides, see meta.json): create_lv2_preset
# returns a serialised Turtle STRING, and rdflib's serialisers are not
# byte-stable across two independently built (even if isomorphic) graphs --
# comparing the returned strings with plain equality would be comparing
# serialisation order, not RDF content, which is exactly what run_pair's
# docstring says graph comparison must not do ("never raw serialisation").
# This round-trips the string back into a fresh Graph, so the driver compares
# the two GRAPHS by isomorphism instead (same pattern as the boricles/
# ontosphere export_service region already in this corpus).
def demo(label, plugin):
    from rdflib import Graph
    serialised = create_lv2_preset(label, plugin)
    g = Graph()
    g.parse(data=serialised, format='turtle')
    return g
