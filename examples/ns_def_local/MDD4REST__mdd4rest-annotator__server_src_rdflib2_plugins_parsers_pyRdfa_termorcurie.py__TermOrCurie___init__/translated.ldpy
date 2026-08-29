# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/plugins/parsers/pyRdfa/termorcurie.py
# region: TermOrCurie.__init__ (lines 277-320, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib	import Namespace
from .utils 		import quote_URI, URIOpener
from .				import IncorrectPrefixDefinition, RDFA_VOCAB, UnresolvableReference, PrefixRedefinitionWarning
from . import err_bnode_local_prefix				
from . import err_missing_URI_prefix				
from . import err_invalid_prefix					
from . import err_no_default_prefix				
from . import err_prefix_and_xmlns				
from . import err_non_ncname_prefix				
ncname   = re.compile("^[A-Za-z][A-Za-z0-9._-]*$")

if state.rdfa_version >= "1.1" and state.node.hasAttribute("prefix") :
	pr = state.node.getAttribute("prefix")
	if pr != None :
		# separator character is whitespace
		pr_list = pr.strip().split()
		# range(0, len(pr_list), 2) 
		for i in range(len(pr_list) - 2, -1, -2) :
			prefix = pr_list[i]
			# see if there is a URI at all
			if i == len(pr_list) - 1 :
				state.options.add_warning(err_missing_URI_prefix % (prefix,pr), node=state.node.nodeName)
				break
			else :
				value = pr_list[i+1]

			# see if the value of prefix is o.k., ie, there is a ':' at the end
			if prefix[-1] != ':' :
				state.options.add_warning(err_invalid_prefix % (prefix,pr), IncorrectPrefixDefinition, node=state.node.nodeName)
				continue
			elif prefix == ":" :
				state.options.add_warning(err_no_default_prefix % pr, IncorrectPrefixDefinition, node=state.node.nodeName)
				continue						
			else :
				prefix = prefix[:-1]
				uri    = Namespace(quote_URI(value, state.options))
				if prefix == "" :
					#something to be done here
					self.default_curie_uri = uri
				elif prefix == "_" :
					state.options.add_warning(err_bnode_local_prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
				else :
					# last check: is the prefix an NCNAME?
					if ncname.match(prefix) :
						real_prefix = prefix.lower()
						dict[real_prefix] = uri
						self.graph.bind(real_prefix,uri)
						# Additional warning: is this prefix overriding an existing xmlns statement with a different URI? if
						# so, that may lead to discrepancies between an RDFa 1.0 and RDFa 1.1 run...
						if (prefix in xmlns_dict and xmlns_dict[prefix] != uri) or (real_prefix in xmlns_dict and xmlns_dict[real_prefix] != uri) :
							state.options.add_warning(err_prefix_and_xmlns % (real_prefix,real_prefix), node=state.node.nodeName)
						check_prefix(real_prefix)

					else :
						state.options.add_warning(err_non_ncname_prefix % (prefix,pr), IncorrectPrefixDefinition, node=state.node.nodeName)
