# Extracted from openphacts/ops-search@170caa5881 : src/app.py
# region: render_rdf (lines 78-80, band low)
# licence of the source repository: see meta.json
from web_context import hook, route, run, Bottle, get, post, request, response, static_file, url
import json
from rdflib import Graph, plugin

def render_rdf(doc, format):
    g = Graph().parse(data=json.dumps(doc), format="json-ld", publicID=request.url)
    return g.serialize(format=format)
