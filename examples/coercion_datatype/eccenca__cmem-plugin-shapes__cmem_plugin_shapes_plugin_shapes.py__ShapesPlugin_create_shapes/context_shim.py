# Context shim (see meta.json): restores `format_namespace`, a module-level
# helper used but not defined in the extracted region, from
# eccenca/cmem-plugin-shapes@52d5b16c0550 (cmem_plugin_shapes/plugin_shapes.py,
# verified against the source repository at that commit).
#
# Copied VERBATIM from plugin_shapes.py:50-52.
def format_namespace(iri: str) -> str:
    """Ensure namespace ends with '/' or '#'"""
    return iri if iri.endswith(("/", "#")) else iri + "/"
