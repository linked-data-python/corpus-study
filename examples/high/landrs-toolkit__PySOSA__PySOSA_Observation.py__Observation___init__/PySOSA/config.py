"""Context shim: the namespace bindings of PySOSA/config.py.

Copied verbatim from landrs-toolkit/PySOSA@1993668bd7 : PySOSA/config.py
(only the `#Ontology namespaces` block; the rest of that file is a JSON-LD
`context` dict and a second `obsgraph`, neither of which the region uses).

Imported IDENTICALLY by original.py and translated.ldpy.
"""

from rdflib import Namespace

#Ontology namespaces
ssnext = Namespace("http://www.w3.org/ns/ssn/ext/")
sosa = Namespace("http://www.w3.org/ns/sosa/")
prov = Namespace("http://www.w3.org/ns/prov#")
qudt = Namespace("http://qudt.org/1.1/schema/qudt#")
owltime = Namespace("ttp://www.w3.org/2006/time#")
owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://purl.org/dc/terms/")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
ssn = Namespace("http://www.w3.org/ns/ssn/")
