# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/plugins/parsers/pyRdfa/state.py
# region: ExecutionContext._CURIEorURI (lines 341-386, band low)
# licence of the source repository: see meta.json
from rdflib	import URIRef
from rdflib	import BNode
from urllib.parse import urlsplit
from pyrdfa_context	import UnresolvablePrefix, UnresolvableTerm
from pyrdfa_context import err_illegal_safe_CURIE				
from pyrdfa_context import err_no_CURIE_in_safe_CURIE			

def _CURIEorURI(self, val) :
	"""Returns a URI for a (safe or not safe) CURIE. In case it is a safe CURIE but the CURIE itself
	is not defined, an error message is issued. Otherwise, if it is not a CURIE, it is taken to be a URI
	@param val: attribute value to be interpreted
	@type val: string
	@return: an RDFLib URIRef instance or None
	"""
	if val == "" :
		return URIRef(self.base)

	safe_curie = False
	if val[0] == '[' :
		# If a safe CURIE is asked for, a pure URI is not acceptable.
		# Is checked below, and that is why the safe_curie flag is necessary
		if val[-1] != ']' :
			# that is certainly forbidden: an incomplete safe CURIE
			self.options.add_warning(err_illegal_safe_CURIE % val, UnresolvablePrefix, node=self.node.nodeName)
			return None
		else :
			val = val[1:-1]
			safe_curie = True
	# There is a branch here depending on whether we are in 1.1 or 1.0 mode
	if self.rdfa_version >= "1.1" :
		retval = self.term_or_curie.CURIE_to_URI(val)
		if retval == None :
			# the value could not be interpreted as a CURIE, ie, it did not produce any valid URI.
			# The rule says that then the whole value should be considered as a URI
			# except if it was part of a safe CURIE. In that case it should be ignored...
			if safe_curie :
				self.options.add_warning(err_no_CURIE_in_safe_CURIE % val, UnresolvablePrefix, node=self.node.nodeName)
				return None
			else :
				return self._URI(val)
		else :
			# there is an unlikely case where the retval is actually a URIRef with a relative URI. Better filter that one out
			if isinstance(retval, BNode) == False and urlsplit(str(retval))[0] == "" :
				# yep, there is something wrong, a new URIRef has to be created:
				return URIRef(self.base+str(retval))
			else :
				return retval
	else :
		# in 1.0 mode a CURIE can be considered only in case of a safe CURIE
		if safe_curie :
			return self.term_or_curie.CURIE_to_URI(val)
		else :
			return self._URI(val)
