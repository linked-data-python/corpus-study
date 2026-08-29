"""Validation driver for SpotlightKid__jack-audio-tools__carla_carxp2lv2presets.py__create_lv2_preset.

Establishes semantic equivalence of original.py and translated.ldpy via the
demo(label, plugin) harness both files carry (see meta.json): create_lv2_preset
returns a serialised Turtle string, so demo() round-trips it into a fresh
Graph and hands that back -- the driver then compares graphs by isomorphism,
never the raw serialised text.

CALL_1 -- two params (walks the add-in-loop sugar over `plugin.params` with
more than one row) and two properties: one whose type is exactly
`str(NS.atom.Path)` (the URIRef-value branch) and one that is not (the
Literal-value branch) -- both branches of the ternary inside the second
add-in-loop's bindings-generator, both write into the same `state` blank
node, then the closing `pstate:state` triple.

CALL_2 -- no params (empty list: the loop must contribute nothing) and no
properties (empty dict, falsy: the whole `if plugin.properties:` block,
including the `pstate:state` triple, must be skipped entirely) -- only the
three base preset triples remain.

CALL_3 -- one param, one property (the Literal-value branch only), covering
the boundary between "several rows" (CALL_1) and "no rows" (CALL_2).
"""
from rdfeval.harness import run_pair
from context_shim import NS, Param, PluginInstance, Property

ATOM_PATH = str(NS.atom.Path)

PLUGIN_1 = PluginInstance(
    uri="http://example.org/plugins/synth1",
    params=[
        Param(symbol="cutoff", value=0.75),
        Param(symbol="resonance", value=0.2),
    ],
    properties={
        "state:sample": Property(
            type=ATOM_PATH, key="state:sample", value="file:///home/user/sample.wav"
        ),
        "state:preset-name": Property(
            type="http://lv2plug.in/ns/ext/atom#String",
            key="state:preset-name",
            value="Warm Pad",
        ),
    },
)

PLUGIN_2 = PluginInstance(uri="http://example.org/plugins/synth2", params=[], properties={})

PLUGIN_3 = PluginInstance(
    uri="http://example.org/plugins/synth3",
    params=[Param(symbol="gain", value=1.0)],
    properties={
        "state:mode": Property(
            type="http://lv2plug.in/ns/ext/atom#String", key="state:mode", value="mono"
        ),
    },
)

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        (("Warm Synth Preset", PLUGIN_1), {}),
        (("Empty Preset", PLUGIN_2), {}),
        (("Third Preset", PLUGIN_3), {}),
    ],
)
