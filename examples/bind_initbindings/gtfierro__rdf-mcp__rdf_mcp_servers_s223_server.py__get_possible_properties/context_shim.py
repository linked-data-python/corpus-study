# Context shim (see meta.json): the real file does `from mcp.server.fastmcp
# import FastMCP` and decorates `get_possible_properties` with `@mcp.tool()`.
# The `mcp` package (the Model Context Protocol SDK, an optional dependency
# of gtfierro/rdf-mcp) is not installed in the pinned study venv.
#
# `@mcp.tool()` only registers the function's metadata with the server; it
# does not change how the function behaves when called directly. Checked
# against the real package (mcp 2.1.1, downloaded to inspect --
# `mcp/server/mcpserver/server.py`, `FastMCP.tool`): its decorator body is
# `def decorator(fn): self.add_tool(fn, ...); return fn`, i.e. it returns
# `fn` unchanged after registering it. This shim reproduces exactly that
# pass-through -- no logic invented. Identical for both representations.
class FastMCP:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self, *args, **kwargs):
        def _decorator(fn):
            return fn
        return _decorator
