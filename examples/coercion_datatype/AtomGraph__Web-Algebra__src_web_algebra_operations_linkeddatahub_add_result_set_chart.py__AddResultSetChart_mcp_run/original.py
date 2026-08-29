# Extracted from AtomGraph/Web-Algebra@128e184aa8 : src/web_algebra/operations/linkeddatahub/add_result_set_chart.py
# region: AddResultSetChart.mcp_run (lines 259-295, stratum coercion_datatype)
# licence of the source repository: see meta.json
from typing import Any, Optional
from rdflib import Literal, URIRef
from rdflib.namespace import XSD

def mcp_run(self, arguments: dict, context: Any = None) -> Any:
    """MCP execution: plain args → plain results"""
    from mcp import types

    # Convert plain arguments to RDFLib terms
    url = URIRef(arguments["url"])
    query = URIRef(arguments["query"])
    title = Literal(arguments["title"], datatype=XSD.string)
    chart_type = URIRef(arguments["chart_type"])
    category_var_name = Literal(arguments["category_var_name"], datatype=XSD.string)
    series_var_name = Literal(arguments["series_var_name"], datatype=XSD.string)

    description = None
    if "description" in arguments:
        description = Literal(arguments["description"], datatype=XSD.string)

    fragment = None
    if "fragment" in arguments:
        fragment = Literal(arguments["fragment"], datatype=XSD.string)

    # Call pure function
    result = self.execute(
        url,
        query,
        title,
        chart_type,
        category_var_name,
        series_var_name,
        description,
        fragment,
    )

    # Return status for MCP response
    status_binding = result.bindings[0]["status"]
    return [
        types.TextContent(type="text", text=f"Result set chart added - status: {status_binding}")
    ]
