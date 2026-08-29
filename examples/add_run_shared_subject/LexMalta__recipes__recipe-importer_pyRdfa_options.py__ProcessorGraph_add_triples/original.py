# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/pyRdfa/options.py
# region: ProcessorGraph.add_triples (lines 48-99, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import sys, datetime
from rdflib	import URIRef
from rdflib	import Literal
from rdflib	import BNode
from .		import ns_xsd, ns_distill, ns_rdfa
ns_dc = Namespace("http://purl.org/dc/terms/")
ns_ht = Namespace("http://www.w3.org/2006/http#")

def add_triples(self, msg, top_class, info_class, context, node) :
	"""
	Add an error structure to the processor graph: a bnode with a number of predicates. The structure
	follows U{the processor graph vocabulary<http://www.w3.org/2010/02/rdfa/wiki/Processor_Graph_Vocabulary>} as described
	on the RDFa WG Wiki page.

	@param msg: the core error message, added as an object to a dc:description
	@param top_class: Error, Warning, or Info; an explicit rdf:type added to the bnode
	@type top_class: URIRef
	@param info_class: An additional error class, added as an rdf:type to the bnode in case it is not None
	@type info_class: URIRef
	@param context: An additional information added, if not None, as an object with rdfa:context as a predicate
	@type context: either an URIRef or a URI String (an URIRef will be created in the second case)
	@param node: The node's element name that contains the error
	@type node: string
	@return: the bnode that serves as a subject for the errors. The caller may add additional information
	@rtype: BNode
	"""
	# Lazy binding of relevant prefixes
	self.graph.bind("dcterms", ns_dc)
	self.graph.bind("pyrdfa",  ns_distill)
	self.graph.bind("rdf",     ns_rdf)
	self.graph.bind("rdfa",    ns_rdfa)
	self.graph.bind("ht",      ns_ht)
	self.graph.bind("xsd",     ns_xsd)
	# Python 3 foolproof way
	try :
		is_context_string = isinstance(context, basestring)
	except :
		is_context_string = isinstance(context, str)

	bnode = BNode()

	if node != None:
		try :
			full_msg = "[In element '%s'] %s" % (node.nodeName, msg)
		except :
			full_msg = "[In element '%s'] %s" % (node, msg)
	else :
		full_msg = msg

	self.graph.add((bnode, ns_rdf["type"], top_class))
	if info_class :
		self.graph.add((bnode, ns_rdf["type"], info_class))
	self.graph.add((bnode, ns_dc["description"], Literal(full_msg)))
	self.graph.add((bnode, ns_dc["date"], Literal(datetime.datetime.utcnow().isoformat(),datatype=ns_xsd["dateTime"])))
	if context and (isinstance(context,URIRef) or is_context_string):
		htbnode = BNode()
		self.graph.add( (bnode,   ns_rdfa["context"],htbnode) )
		self.graph.add( (htbnode, ns_rdf["type"], ns_ht["Request"]) )
		self.graph.add( (htbnode, ns_ht["requestURI"], Literal("%s" % context)) )
	return bnode
