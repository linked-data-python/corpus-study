# Extracted from dh-atlas/app@16f85bf793 : mapping.py
# region: inputToRDF (lines 209-245, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import URIRef , XSD, Namespace , Literal, term
from rdflib.namespace import OWL, DC , DCTERMS, RDF , RDFS, SKOS
base = conf.base

if isinstance(value,str) and len(value) >= 1: # data properties
	value = value.replace('\n','').replace('\r','')
	if 'calendar' in field:
		if field['calendar'] == 'Day':
			wd.add((URIRef(base+graph_name), URIRef(field['property']), Literal(value, datatype=XSD.date)))
		elif field['calendar'] == 'Month':
			wd.add((URIRef(base+graph_name), URIRef(field['property']), Literal(value, datatype=XSD.gYearMonth)))
		elif field['calendar'] == 'Year':
			value = value.replace(" A.D.", "") if "A.D." in value else "-"+value.replace(" B.C.", "") if "B.C." in value else value
			value = value if value.startswith("-") else "0000" + value.zfill(4)
			wd.add((URIRef(base+graph_name), URIRef(field['property']), Literal(value, datatype=XSD.gYear)))
	elif field['type'] == 'Multimedia':
		value = "http://"+value if not value.startswith("http") else value
		wd.add(( URIRef(base+graph_name), URIRef(field['property']), URIRef(value)))
	else:
		wd.add(( URIRef(base+graph_name), URIRef(field['property']), Literal(value) ))
elif isinstance(value,dict): # multiple-values fields
	if value['type'] == 'URL': #url
		for URL in value['results']:
			if URL[1] != "":
				valueURL = URL[1] if URL[1].startswith("http") else "http://" + URL[1]
				wd.add(( URIRef(base+graph_name), URIRef(field['property']), URIRef(valueURL) ))
	elif value['type'] == 'URI': #object properties
		rdf_property = SKOS.prefLabel if field['type'] == 'Skos' else RDFS.label
		for entity in value['results']:
			if entity[0] and entity[1]:
				entityURI = getRightURIbase(entity[0]) # Wikidata or new entity
				wd.add(( URIRef(base+graph_name), URIRef(field['property']), URIRef(entityURI) ))
				wd.add(( URIRef( entityURI ), rdf_property, Literal(entity[1].lstrip().rstrip(), datatype="http://www.w3.org/2001/XMLSchema#string") ))
				if field["type"] == "Subclass": # Subclass
					wd.add(( URIRef(base+graph_name), RDF.type, URIRef(entityURI) ))
	elif value['type'] == 'Literal': #multi-language Literals
		for literal in value['results']:
			val, lang = literal
			val = val.replace('\n','').replace('\r','')
			if val != "":
				wd.add(( URIRef(base+graph_name), URIRef(field['property']), Literal(val, lang=lang)))
