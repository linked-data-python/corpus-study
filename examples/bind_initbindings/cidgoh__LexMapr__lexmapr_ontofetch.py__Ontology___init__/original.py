# Extracted from cidgoh/LexMapr@999b11e44d : lexmapr/ontofetch.py
# region: Ontology.__init__ (lines 80-156, stratum bind_initbindings)
# licence of the source repository: see meta.json
import lexmapr.ontohelper as oh
from rdflib.plugins.sparql import prepareQuery

def __init__(self):

	self.onto_helper = oh.OntoHelper()
	# ADDITIONAL FIELDS THAT WOULD BE MANAGED IN SYNCHRONIZATION of TARGET
	# LOOKUP TABLE: 'updated','preferred'
	self.fields = self.FIELDS + self.onto_helper.SYNONYM_FIELDS

	""" 
	Add these PREFIXES to Sparql query window if you want to test a query there:

	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl: <http://www.w3.org/2002/07/owl#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX OBO: <http://purl.obolibrary.org/obo/>
	PREFIX xmls: <http://www.w3.org/2001/XMLSchema#>
	""" 

	self.queries = {
		##################################################################
		# Generic TREE "is a" hierarchy from given root.
		#
		'tree': prepareQuery("""
			SELECT DISTINCT ?id ?label ?parent_id ?deprecated ?replaced_by 
			WHERE {	
				?parent_id rdfs:subClassOf* ?root.
				?id rdfs:subClassOf ?parent_id.
				OPTIONAL {?id rdfs:label ?label}.
 				OPTIONAL {?id GENEPIO:0000006 ?ui_label}. # for ordering
				OPTIONAL {?id owl:deprecated ?deprecatedAnnot.
					BIND(xmls:string(?deprecatedAnnot) As ?deprecated).
				}.
				OPTIONAL {?id IAO:0100001 ?replaced_byAnnot.
					BIND(xmls:string(?replaced_byAnnot) As ?replaced_by).
				}.	
			}
			ORDER BY ?parent_id ?ui_label ?label 
		""", initNs = self.onto_helper.namespace),


		# ################################################################
		# UI LABELS 
		# These are annotations directly on an entity.  This is the only place
		# that ui_label and ui_definition should really operate. Every entity
		# in OWL file is retrieved for their rdfs:label, IAO definition etc.
		# FUTURE: ADD SORTING OPTIONS, CUSTOM ORDER.
		'entity_text': prepareQuery("""

			SELECT DISTINCT ?label ?definition ?ui_label ?ui_definition
			WHERE {  
				{?datum rdf:type owl:Class} 
				UNION {?datum rdf:type owl:NamedIndividual} 
				UNION {?datum rdf:type rdf:Description}.
				OPTIONAL {?datum rdfs:label ?label.} 
				OPTIONAL {?datum IAO:0000115 ?definition.}
				OPTIONAL {?datum GENEPIO:0000006 ?ui_label.} 
				OPTIONAL {?datum GENEPIO:0000162 ?ui_definition.}
			} ORDER BY ?label
		""", initNs = self.onto_helper.namespace),




		# ################################################################
		# Fetch parent IDs of given entity. with respect to class-subclass
		# relations.
		# STATUS: UNTESTED, UNUSED
		# INPUT
		# 	?datum_id : id of term to get parents for
		# OUTPUT
		#   ?parent_ids
		#
		#'entity_parents': prepareQuery("""
		#	SELECT DISTINCT ?datum_id (group_concat(distinct ?parent_id;separator=",") as ?parent_ids)
		#	WHERE {
		#		?datum_id rdfs:subClassOf ?parent_id.
		#		?parent_id rdfs:label ?label # to ensure parent_id entity is in graph as well.
		#	}
		#""", initNs = self.onto_helper.namespace),
	}
