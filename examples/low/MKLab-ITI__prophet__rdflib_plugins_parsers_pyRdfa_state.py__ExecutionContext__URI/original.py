# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/plugins/parsers/pyRdfa/state.py
# region: ExecutionContext._URI (lines 269-338, band low)
# licence of the source repository: see meta.json
# context shim (see meta.json): module-level bindings of state.py and of
# the pyRdfa package, made importable from a local module.
from context import py_v_major, py_v_minor
from rdflib	import URIRef
if py_v_major >= 3 :
	from urllib.parse import urlsplit, urljoin
else :
	from urlparse import urlsplit, urljoin
from context import err_URI_scheme

def _URI(self, val) :
	"""Returns a URI for a 'pure' URI (ie, not a CURIE). The method resolves possible relative URI-s. It also
	checks whether the URI uses an unusual URI scheme (and issues a warning); this may be the result of an
	uninterpreted CURIE...
	@param val: attribute value to be interpreted
	@type val: string
	@return: an RDFLib URIRef instance
	"""
	def create_URIRef(uri, check = True) :
		"""
		Mini helping function: it checks whether a uri is using a usual scheme before a URIRef is created. In case
		there is something unusual, a warning is generated (though the URIRef is created nevertheless)
		@param uri: (absolute) URI string
		@return: an RDFLib URIRef instance
		"""
		from context import uri_schemes
		val = uri.strip()
		if check and urlsplit(val)[0] not in uri_schemes :
			self.options.add_warning(err_URI_scheme % val.strip(), node=self.node.nodeName)
		return URIRef(val)

	def join(base, v, check = True) :
		"""
		Mini helping function: it makes a urljoin for the paths. Based on the python library, but
		that one has a bug: in some cases it
		swallows the '#' or '?' character at the end. This is clearly a problem with
		Semantic Web URI-s, so this is checked, too
		@param base: base URI string
		@param v: local part
		@param check: whether the URI should be checked against the list of 'existing' URI schemes
		@return: an RDFLib URIRef instance
		"""
		# UGLY!!! There is a bug for a corner case in python version <= 2.5.X
		if len(v) > 0 and v[0] == '?' and (py_v_major < 3 and py_v_minor <= 5) :
			return create_URIRef(base+v, check)
		####

		joined = urljoin(base, v)
		try :
			if v[-1] != joined[-1] and (v[-1] == "#" or v[-1] == "?") :
				return create_URIRef(joined + v[-1], check)
			else :
				return create_URIRef(joined, check)
		except :
			return create_URIRef(joined, check)

	if val == "" :
		# The fragment ID must be removed...
		return URIRef(self.base)

	# fall back on good old traditional URI-s.
	# To be on the safe side, let us use the Python libraries
	if self.parsedBase[0] == "" :
		# base is, in fact, a local file name
		# The following call is just to be sure that some pathological cases when
		# the ':' _does_ appear in the URI but not in a scheme position is taken
		# care of properly...

		key = urlsplit(val)[0]
		if key == "" :
			# relative URI, to be combined with local file name:
			return join(self.base, val, check = False)
		else :
			return create_URIRef(val)
	else :
		# Trust the python library...
		# Well, not quite:-) there is what is, in my view, a bug in the urljoin; in some cases it
		# swallows the '#' or '?' character at the end. This is clearly a problem with
		# Semantic Web URI-s			
		return join(self.base, val)
