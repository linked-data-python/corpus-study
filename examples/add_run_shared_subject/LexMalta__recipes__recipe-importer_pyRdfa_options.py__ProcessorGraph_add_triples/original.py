# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/pyRdfa/options.py
# region: ProcessorGraph.add_triples (lines 48-99, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import sys, datetime
from rdflib	import URIRef
from rdflib	import Literal
from rdflib	import BNode
from rdflib	import Namespace
from processor_context import ns_xsd, ns_distill, ns_rdfa, ns_rdf
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

# Demo harness (identical on both sides, see meta.json): `add_triples` is a
# plain method that reads `self.graph` -- ProcessorGraph.__init__ (options.py
# line 46-47) sets it, and this extraction's context window does not carry
# the class, only the function body (AGENT_BATCH's "163 regions" case). Two
# calls exercise both branches of `if info_class:` and of the
# `if context and (...)` guard, so every triple the region can add is
# covered. `datetime.datetime.utcnow()` is frozen the same way as
# ns_import_project/johnjung.../mepa_edm's own demo harness, so the
# `nsdc:date`/`dcterms:date` literal does not make the two graphs
# non-isomorphic by a live wall-clock difference that has nothing to do with
# whether the translation is correct.
from processor_context import ProcessorGraph


def demo():
	pg = ProcessorGraph()
	add_triples(pg, "boom", ns_rdfa["Error"], ns_rdfa["Warning"],
	            "http://example.org/ctx", None)
	add_triples(pg, "ok", ns_rdfa["Info"], None, None, None)
	return pg.graph
