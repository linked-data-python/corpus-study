# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/pipelines/utils/ttl_publisher.py
# region: _build_composite_entity_graph (lines 646-649, stratum add_isolated)
# licence of the source repository: see meta.json
for s, p, o in entity_g:
    new_s = remap_to if (remap_from is not None and s == remap_from) else s
    new_o = remap_to if (remap_from is not None and o == remap_from) else o
    g.add((new_s, p, new_o))
