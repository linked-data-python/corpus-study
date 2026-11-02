# Context shim (see meta.json): the three names the one-line region reads in
# query_step_details (scripts/output_conversion_ttl_to_json/
# ontosynthesis_step_conversion.py, TheWorldAvatar/mcp-tool-layer@c440a33e08):
# the function's `graph` and `step_uri` (here: a graph parsed from
# fixture.ttl and one step of it), and the `vessel_type_query` string
# defined on the lines just above the region (copied verbatim; only the
# original representation uses it). Identical bindings for both sides.
from pathlib import Path

from rdflib import Graph

graph = Graph().parse(Path(__file__).with_name("fixture.ttl"), format="turtle")
step_uri = "https://www.theworldavatar.com/kg/OntoSyn/Step_2"

vessel_type_query = """
    PREFIX ontosyn: <https://www.theworldavatar.com/kg/OntoSyn/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?vesselTypeLabel
    WHERE {
        ?step ontosyn:hasVessel ?vessel .
        ?vessel ontosyn:hasVesselType ?vesselType .
        ?vesselType rdfs:label ?vesselTypeLabel .
    }
    """
