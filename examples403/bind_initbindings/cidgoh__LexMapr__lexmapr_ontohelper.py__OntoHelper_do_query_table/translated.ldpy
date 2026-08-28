# Extracted from cidgoh/LexMapr@999b11e44d : lexmapr/ontohelper.py
# region: OntoHelper.do_query_table (lines 391-477, stratum bind_initbindings)
# licence of the source repository: see meta.json
import rdflib

	def do_query_table(self, query, initBinds = {}):
		"""
		Given a sparql 1.1 query, returns a list of objects, one for each row.
		For each object key/value, simplifies any URI reference (http://...) 
		into namespace prefix:identifier as in @context. 

		INPUT
		initBinds:	To provide parameters to the query, supply it with initBindings 
					containing a dictionary of bindings in format "term: value".

		"""

		#query = self.queries[query_name]

		try:
			result = self.graph.query(query, initBindings=initBinds)
		except Exception as e:
			print ("\nSparql query [%s] parsing problem: %s \n" % (query, str(e) ))
			return None

		# Can't get columns by row.asdict().keys() because columns with null results won't be included in a row.
		# Handles "... SELECT DISTINCT (?something as ?somethingelse) ?this ?and ?that WHERE ....""
		#columns = re.search(r"(?mi)\s*SELECT(\s+DISTINCT)?\s+((\?\w+\s+|\(\??\w+\s+as\s+\?\w+\)\s*)+)\s*WHERE", query)
		#columns = re.findall(r"\s+\?(?P<name>\w+)\)?", columns.group(2))

		STRING_DATATYPE = rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')
		table = []
		for ptr, row in enumerate(result):
			rowdict = row.asdict()
			newrowdict = {}

			for column in rowdict:

				# Each value has a datatype defined by RDF Parser: URIRef, Literal, BNode
				value = rowdict[column]
				valType = type(value) 
				if valType is rdflib.term.URIRef : 
					newrowdict[column] = self.get_entity_id(value)  # a plain string

				elif valType is rdflib.term.Literal :
					# Text may include carriage returns; escape to json
					literal = {'value': value.replace('\n', r'\n')} 
					#_invalid_uri_chars = '<>" {}|\\^`'

					if hasattr(value, 'datatype'): #rdf:datatype
						#Convert literal back to straight string if its datatype is simply xmls:string
						if value.datatype == None or value.datatype == STRING_DATATYPE:
							literal = literal['value']
						else:
							literal['datatype'] = self.get_entity_id(value.datatype)															

					elif hasattr(value, 'language'): # e.g.  xml:lang="en"
						#A query Literal won't have a language if its the result of str(?whatever) !
						literal['language'] = self.get_entity_id(value.language)

					else: # WHAT OTHER OPTIONS?
						literal = literal['value']

					newrowdict[column] = literal

				elif valType is rdflib.term.BNode:
					"""
					Convert a variety of BNode structures into something simple.
					E.g. "(province or state or territory)" is a BNode structure coded like
					 	<owl:someValuesFrom> 
							<owl:Class>
								<owl:unionOf rdf:parseType="Collection">
                    			   <rdf:Description rdf:about="&resource;SIO_000661"/> 
                    			   <rdf:Description rdf:about="&resource;SIO_000662"/>
                    			   ...
                    """
                    # Here we fetch list of items in disjunction
					disjunction = self.graph.query(
						"SELECT ?id WHERE {?datum owl:unionOf/rdf:rest*/rdf:first ?id}", 
						initBindings={'datum': value} )		
					results = [self.get_entity_id(item[0]) for item in disjunction] 
					newrowdict['expression'] = {'datatype':'disjunction', 'data':results}

					newrowdict[column] = value

				else:

					newrowdict[column] = {'value': 'unrecognized column [%s] type %s for value %s' % (column, type(value), value)}

			table.append(newrowdict)

		return table
