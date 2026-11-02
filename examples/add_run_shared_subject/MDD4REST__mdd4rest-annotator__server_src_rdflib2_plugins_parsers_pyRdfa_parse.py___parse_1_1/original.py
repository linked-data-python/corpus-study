# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/plugins/parsers/pyRdfa/parse.py
# region: _parse_1_1 (lines 303-316, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib	import BNode

if state.new_list and not state.list_empty() :
	for prop in state.get_list_props() :
		vals  = state.get_list_value(prop)
		if vals == None :
			# This was an empty list, in fact, ie, the list has been initiated by a <xxx rel="prop" inlist>
			# but no list content has ever been added
			graph.add( (state.get_list_origin(), prop, ns_rdf["nil"]) )
		else :
			heads = [ BNode() for r in vals ] + [ ns_rdf["nil"] ]
			for i in range(0, len(vals)) :
				graph.add( (heads[i], ns_rdf["first"], vals[i]) )
				graph.add( (heads[i], ns_rdf["rest"],  heads[i+1]) )
			# Anchor the list
			graph.add( (state.get_list_origin(), prop, heads[0]) )
