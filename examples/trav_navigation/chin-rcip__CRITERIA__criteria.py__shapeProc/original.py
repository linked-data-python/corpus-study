# Extracted from chin-rcip/CRITERIA@dfc7e5b74e : criteria.py
# region: shapeProc (lines 195-228, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Namespace, util
from rdflib.namespace import NamespaceManager, RDFS, RDF, XSD, SKOS, SH
nodeLabels = {} # URI: {Property, Node Label} for node 
nodeLink = {} # Node Label and URL link to node documentation

def shapeProc(dataGraph,shapeInput):
	shapeFormat = util.guess_format(shapeInput)
	shape = Graph()
	shape.parse(shapeInput, format=shapeFormat)

	for s,p,o in shape.triples((None, SKOS.example, None)):
		if (s,RDF.type,SH.NodeShape) in shape:
			inst = "(["+o.n3(shape.namespace_manager)+"])"
			inst = inst.replace('<','').replace('>','')
			nodeLb =''
			for propShape in shape.objects(s,SH.property):
				for path in shape.objects(propShape,SH.path):
					path = path.n3(shape.namespace_manager)
				for nodeLb in shape.objects(propShape,SH.name):
					nodeLb = nodeLb.n3(shape.namespace_manager).replace('"','')
				for nodeURL in shape.objects(propShape,SH.description):
					nodeURL = nodeURL.n3(shape.namespace_manager).replace('"','')
				if nodeURL:
					nodeLink[nodeLb] = nodeURL
				for nodeVal in shape.objects(propShape,SH.defaultValue):
					nodeLb = nodeLb+'|||'+nodeVal.n3(shape.namespace_manager)
					nodeValURL = nodeVal
					nodeVal = nodeVal.n3(shape.namespace_manager)
					for nodeValLb in dataGraph.objects(nodeValURL,RDFS.label):
						nodeValLb = nodeValLb.n3(shape.namespace_manager).replace('"',"''").replace('^^xsd:string','')
						nodeLb = nodeLb+'<br><em>'+str(nodeValLb)+'</em>'
						nodeVal = nodeVal+'<br><em>'+str(nodeValLb)+'</em>'
					if nodeValURL:
						nodeLink[nodeVal] = nodeValURL

				if not inst in nodeLabels:
					nodeLabels[inst] = {path: nodeLb}
				else:
					nodeLabels[inst][path] = nodeLb		
