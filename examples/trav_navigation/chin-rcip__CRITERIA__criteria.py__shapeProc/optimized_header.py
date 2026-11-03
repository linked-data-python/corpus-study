# Extracted from chin-rcip/CRITERIA@dfc7e5b74e : criteria.py
# region: shapeProc (lines 195-228, stratum trav_navigation)
# licence of the source repository: see meta.json
import json
from pathlib import Path

from rdflib import Graph, util
from rdflib.namespace import RDF, RDFS, SH, SKOS
nodeLabels = {} # URI: {Property, Node Label} for node
nodeLink = {} # Node Label and URL link to node documentation

def shapeProc(dataGraph,shapeInput):
	shape = Graph().parse(shapeInput, format=util.guess_format(shapeInput))
	ns_manager = shape.namespace_manager

	for s, o in shape.subject_objects(SKOS.example):
		if (s, RDF.type, SH.NodeShape) in shape:
			inst = "([" + o.n3(ns_manager).replace('<', '').replace('>', '') + "])"
			nodeLb = ''
			for propShape in shape.objects(s, SH.property):
				for path in shape.objects(propShape, SH.path):
					path = path.n3(ns_manager)
				for nodeLb in shape.objects(propShape, SH.name):
					nodeLb = nodeLb.n3(ns_manager).replace('"', '')
				for nodeURL in shape.objects(propShape, SH.description):
					nodeURL = nodeURL.n3(ns_manager).replace('"', '')
				if nodeURL:
					nodeLink[nodeLb] = nodeURL
				for nodeValURL in shape.objects(propShape, SH.defaultValue):
					nodeVal = nodeValURL.n3(ns_manager)
					nodeLb += '|||' + nodeVal
					for nodeValLb in dataGraph.objects(nodeValURL, RDFS.label):
						nodeValLb = nodeValLb.n3(ns_manager).replace('"', "''").replace('^^xsd:string', '')
						nodeLb += '<br><em>' + nodeValLb + '</em>'
						nodeVal += '<br><em>' + nodeValLb + '</em>'
					if nodeValURL:
						nodeLink[nodeVal] = nodeValURL

				if inst in nodeLabels:
					nodeLabels[inst][path] = nodeLb
				else:
					nodeLabels[inst] = {path: nodeLb}

# Driving code (not part of the extracted region): the region mutates the
# module-level nodeLabels/nodeLink dicts and returns nothing, so we call it
# against the fixture graphs and print the mutated dicts, sorted, to make the
# region's effect observable to the driver.
_HERE = Path(__file__).resolve().parent
_data_graph = Graph().parse(str(_HERE / "fixture.ttl"), format="turtle")
shapeProc(_data_graph, str(_HERE / "shape.ttl"))
print(json.dumps({"nodeLabels": nodeLabels, "nodeLink": nodeLink},
                  sort_keys=True, default=str))
