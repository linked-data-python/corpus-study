# Extracted from polifonia-project/clef@6b3856022c : mapping.py
# region: inputToRDF (lines 288-389, stratum coercion_datatype)
# licence of the source repository: see meta.json
import os
import datetime
import time
import json
import urllib.parse
import rdflib
from rdflib import URIRef , XSD, Namespace , Literal, term
from rdflib.namespace import OWL, DC , DCTERMS, RDF , RDFS, SKOS
import conf , queries
import tempfile
import shutil
PROV = Namespace("http://www.w3.org/ns/prov#")
base = conf.base
server = sparql.SPARQLServer(conf.myEndpoint)
records_path = os.path.join(dir_path, 'records')

elif field['type']=="KnowledgeExtractor" and "extractions-dict" in recordData:
	# process extraction parameters
	extractions_dict = json.loads(urllib.parse.unquote(recordData["extractions-dict"]))
	extractions_array_unfiltered = extractions_dict[recordID] if recordID in extractions_dict else []
	extractions_array_by_property = extractions_array_unfiltered[field['id']] if field['id'] in extractions_array_unfiltered else {}
	extractions_array = [extraction for extraction in extractions_array_by_property if 'metadata' in extraction and 'type' in extraction['metadata']]

	for extraction in extractions_array:
		extraction_num = str(extraction['internalId'])
		extraction_type = extraction['metadata']['type']
		extraction_url = extraction['metadata']['url']
		extraction_class = extraction['metadata']['class'] if 'class' in extraction['metadata'] else "None"
		extraction_access_keys = False
		if extraction_type == 'api':
			if 'query' in extraction['metadata']:
				encoded_query = ''
				add_symbol = '?'
				for parameter_key,parameter_value in extraction['metadata']['query'].items():
					encoded_query += add_symbol + parameter_key + '=' + parameter_value
					add_symbol = '&'
				extraction_url+=encoded_query
			if 'results' in extraction['metadata']:
				extraction_access_keys = extraction['metadata']['results']
		elif extraction_type in ['sparql', 'website']:
			query = extraction['metadata']['query'].replace("'","\"")
			encoded_query = urllib.parse.quote(query)
			extraction_url+="?query="+encoded_query
		elif extraction_type == 'file':
			query = extraction['metadata']['query']
			query = query.replace("{", "{{ SERVICE <x-sparql-anything:"+extraction_url+"> {{").replace("}", "}}") if "<x-sparql-anything:" not in query else query
			query = query.replace("'","\"")
			encoded_query = urllib.parse.quote(query)
			extraction_url = conf.sparqlAnythingEndpoint+"?query="+encoded_query


		# process extracted keywords
		print("EXTRACT:", "keyword_"+recordID+"-"+field['id']+"-"+extraction_num)
		extracted_keywords = [item for item in recordData if item.startswith("keyword_"+recordID+"-"+field['id']+"-"+extraction_num)]
		print(field["id"], extracted_keywords)
		if len(extracted_keywords) > 0:
			# link the extraction graph to main Record graph
			extraction_graph_name = graph_name + "/extraction-" +field["id"]+"-"+ extraction_num
			wd.add(( URIRef(base+graph_name+'/'), URIRef(field['property']), URIRef(base+extraction_graph_name+'/') ))

			# store the extraction metadata
			queries.clearGraph(base+extraction_graph_name+'/')
			wd_extraction = rdflib.Graph(identifier=URIRef(base+extraction_graph_name+'/'))
			wd_extraction.add(( URIRef(base+extraction_graph_name+'/'), PROV.wasAttributedTo, URIRef(base+userID) ))
			wd_extraction.add(( URIRef(base+extraction_graph_name+'/'), PROV.generatedAtTime, Literal(datetime.datetime.now(),datatype=XSD.dateTime)  ))
			wd_extraction.add(( URIRef(base+extraction_graph_name+'/'), PROV.wasGeneratedBy, URIRef(base+extraction_graph_name)))
			wd_extraction.add(( URIRef(base+extraction_graph_name), PROV.used, URIRef(extraction_url)))
			if extraction_access_keys:
				wd_extraction.add(( URIRef(base+extraction_graph_name), RDFS.comment, Literal(extraction_access_keys)))

			# store the extraction output
			for keyword in extracted_keywords:
				keyword_uri = recordData[keyword] if recordData[keyword] not in ["null", ""] else base + str(time.time()).replace('.','-')
				label = keyword.replace("keyword_"+recordID+"-"+field['id']+"-"+extraction_num+"_","")
				wd_extraction.add(( URIRef(urllib.parse.unquote(keyword_uri).strip()), RDFS.label,  Literal(label, datatype="http://www.w3.org/2001/XMLSchema#string")))
				if extraction_class != "None":
					wd_extraction.add(( URIRef(urllib.parse.unquote(keyword_uri).strip()), RDF.type,  URIRef(extraction_class)))

			# DUMP TTL: prepare the records directory and filename for the extraction
			filename = f"{recordID}-extraction-{field['id']}-{extraction_num}.ttl"
			dest_file = os.path.join(records_path, filename)

			# Create a temporary file on the same filesystem
			temp_file = tempfile.NamedTemporaryFile(delete=False, dir=records_path, suffix='.ttl')
			temp_file_path = temp_file.name
			temp_file.close()

			# Serialize RDF extraction graph into the temporary file, then move it to the records directory
			wd_extraction.serialize(destination=temp_file_path, format='ttl', encoding='utf-8')
			shutil.move(temp_file_path, dest_file, copy_function=shutil.copy)
			os.chmod(dest_file, 0o664)

			# UPLOAD TO TRIPLESTORE
			server.update('load <file:///app/records/'+recordID+"-extraction-"+field["id"]+"-"+extraction_num+'.ttl> into graph <'+base+extraction_graph_name+'/>')

# SUBTEMPLATE
elif field['type']=="Subtemplate" and field['id'] in recordData:
	if type(recordData[field['id']]) != type([]) and field['id']+"-subrecords" in recordData:
		# get the list of subrecords associated to a 'Subtemplate' field
		subrecords = recordData[field['id']+"-subrecords"].split(",,") \
			if field['id']+"-subrecords" in recordData else []
		for subrecord in subrecords:
			if subrecord != "":
				if ";" in subrecord:
					subrecord_id, retrieved_label = subrecord.split(";",1)
				else:
					# process a new subrecord, send its data to the triplestore, and link it to the main record
					subrecord_id = subrecord
					allow_data_reuse = fields if 'dataReuse' in field and field['dataReuse']=='allowDataReuse' else False
					processed_subrecord = process_new_subrecord(recordData,userID,stage,subrecord,supertemplate=None,allow_data_reuse=allow_data_reuse)
					subrecord_id, retrieved_label = processed_subrecord
				wd.add(( URIRef(base+graph_name), URIRef(field['property']), URIRef(base+subrecord_id) ))
				wd.add(( URIRef(base+subrecord_id), RDFS.label, Literal(retrieved_label, datatype="http://www.w3.org/2001/XMLSchema#string")))
	elif type(recordData[field['id']]) == type([]):
		for entity in recordData[field['id']]:
			entity_URI, entity_label = entity
			wd.add(( URIRef(base+graph_name), URIRef(field['property']), URIRef(base+entity_URI) ))
			wd.add(( URIRef(base+entity_URI), RDFS.label, Literal(entity_label, datatype="http://www.w3.org/2001/XMLSchema#string")))
