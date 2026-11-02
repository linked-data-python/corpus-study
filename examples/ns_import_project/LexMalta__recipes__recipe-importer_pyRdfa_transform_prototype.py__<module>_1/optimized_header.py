# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/pyRdfa/transform/prototype.py
# region: <module> (lines 1-37, stratum ns_import_project)
# licence of the source repository: see meta.json
# -*- coding: utf-8 -*-
"""
Encoding of the RDFa prototype vocabulary behavior. This means processing the graph by adding and removing triples
based on triples using the rdfa:Prototype and rdfa:ref class and property, respectively. For details, see the HTML5+RDFa document.


@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
@version: $Id: prototype.py,v 1.1 2013-01-18 09:41:49 ivan Exp $
$Date: 2013-01-18 09:41:49 $
"""
import rdflib
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import RDF  as ns_rdf
else :
	from rdflib.RDF	import RDFNS  as ns_rdf

from pyrdfa_context import ns_rdfa

Prototype = ns_rdfa["Pattern"]
pref      = ns_rdfa["copy"]

def handle_prototypes(graph) :
	to_remove = set()
	for (x,PR) in graph.subject_objects(pref) :
		if (PR,ns_rdf.type,Prototype) in graph :
			to_remove.add((x,pref,PR))
			# there is a reference to a prototype here
			for (p,y) in graph.predicate_objects(PR) :
				to_remove.add((PR,p,y))
				if (p,y) != (ns_rdf.type,Prototype) : graph.add((x,p,y))
	graph -= to_remove
