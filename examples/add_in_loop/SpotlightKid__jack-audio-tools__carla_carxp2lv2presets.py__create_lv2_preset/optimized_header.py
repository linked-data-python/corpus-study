# Extracted from SpotlightKid/jack-audio-tools@a64f1f86ba : carla/carxp2lv2presets.py
# region: create_lv2_preset (lines 48-75, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import BNode, Literal, URIRef, RDF, RDFS
from context_shim import NS, get_graph

def create_lv2_preset(label, plugin):
    graph = get_graph()
    preset = URIRef('')
    graph += [(preset, RDF.type, NS.pset.Preset),
              (preset, NS.lv2.appliesTo, URIRef(plugin.uri)),
              (preset, RDFS.label, Literal(label))]

    for param in plugin.params:
        port = BNode()
        graph += [(port, NS.lv2.symbol, Literal(param.symbol)),
                  (port, NS.pset.value, Literal(param.value)),
                  (preset, NS.lv2.port, port)]

    if plugin.properties:
        state = BNode()
        graph.add((preset, NS.state.state, state))
        for prop in plugin.properties.values():
            # XXX: handle other Atom types?
            value = URIRef(prop.value) if prop.type == str(NS.atom.Path) else Literal(prop.value)
            graph.add((state, URIRef(prop.key), value))

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
