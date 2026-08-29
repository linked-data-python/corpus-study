# Extracted from schemaorg/sdopythonapp@128be97d35 : lib/pyRdfa/termorcurie.py
# region: TermOrCurie.__init__ (lines 247-273, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib	import Namespace
from .utils 		import quote_URI, URIOpener
from .host 			import MediaTypes, HostLanguage, predefined_1_0_rel, warn_xmlns_usage
from .				import IncorrectPrefixDefinition, RDFA_VOCAB, UnresolvableReference, PrefixRedefinitionWarning
from . import err_xmlns_deprecated				
from . import err_bnode_local_prefix				
from . import err_col_local_prefix				

for i in range(0, state.node.attributes.length) :
	attr = state.node.attributes.item(i)
	if attr.name.find('xmlns:') == 0 :	
		# yep, there is a namespace setting
		prefix = attr.localName
		if prefix != "" : # exclude the top level xmlns setting...
			if state.rdfa_version >= "1.1" and state.options.host_language in warn_xmlns_usage :
				state.options.add_warning(err_xmlns_deprecated % prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
			if prefix == "_" :
				state.options.add_warning(err_bnode_local_prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
			elif prefix.find(':') != -1 :
				state.options.add_warning(err_col_local_prefix % prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
			else :					
				# quote the URI, ie, convert special characters into %.. This is
				# true, for example, for spaces
				uri = quote_URI(attr.value, state.options)
				# create a new RDFLib Namespace entry
				ns = Namespace(uri)
				# Add an entry to the dictionary if not already there (priority is left to right!)
				if state.rdfa_version >= "1.1" :
					pr = prefix.lower()
				else :
					pr = prefix
				dict[pr]       = ns
				xmlns_dict[pr] = ns
				self.graph.bind(pr,ns)
				check_prefix(pr)
