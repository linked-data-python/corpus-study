# Extracted from dice-group/COVID19DS@7842845de5 : decaData_product_purchasing/toRdf.py
# region: handleFile (lines 35-117, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, DCTERMS, OWL
import re
import zipcodes
# Executability: pd, OrderedDict and repl() -- defined elsewhere in the same
# source file -- restored via context_shim.py (context shim, see meta.json).
from context_shim import pd, OrderedDict, repl
g = Graph()
resource = "https://covid-19ds.data.dice-research.org/resource/"
schema = Namespace("http://schema.org/")
vcard = Namespace("http://www.w3.org/2006/vcard/ns#")
bibtex = Namespace("http://purl.org/net/nknouf/ns/bibtex#") 
swc = Namespace("http://data.semanticweb.org/ns/swc/ontology#")
prov = Namespace("http://www.w3.org/ns/prov#")
nif = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
its = Namespace("http://www.w3.org/2005/11/its/rdf#")
sdo = Namespace("http://salt.semanticauthoring.org/ontologies/sdo#")
bibo = Namespace("http://purl.org/ontology/bibo/")
fabio = Namespace("http://purl.org/spar/fabio/")
cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")
ndice = Namespace("https://covid-19ds.data.dice-research.org/resource/") #cvdr
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
virtrdf = Namespace('http://www.openlinksw.com/schemas/virtrdf#')
geo = Namespace('http://www.opengis.net/ont/geosparql#')
ctr = Namespace("https://covid-19ds.data.dice-research.org/covidProductPurchasing#")
dowl = Namespace("http://dbpedia.org/ontology/")
reader = pd.read_csv('COVID19_INDEX_SAMPLE_2020_09_07_20200907_200000_COVID19_INDEX_RDX_2020_09_07_20200907_200000.csv', delimiter="|", keep_default_na=False).to_dict('records', into=OrderedDict)
g = Graph()

def handleFile():
	prefixes = {
		"cvdr": ndice, "cvdo": cvdo, "schema": schema, "dcterms": DCTERMS, "foaf": FOAF,
		"vcard": vcard, "bibtex": bibtex, "swc": swc, "prov": prov, "nif": nif, "its": its,
		"sdo": sdo, "bibo": bibo, "fabio": fabio, "owl": OWL, "virtrdf": virtrdf, "geo": geo,
		"ctrp": ctr, "dbpediaOwl": dowl,
	}
	for prefix, namespace in prefixes.items():
		g.bind(prefix, namespace)

	# COVID19_INDEX_SAMPLE_2020_09_07_20200907_200000_COVID19_INDEX_RDX_2020_09_07_20200907_200000.csv
	datatypes = {'QTY': XSD.integer, 'UPC': XSD.integer, 'STORE_ZIP_CODE': XSD.integer,
	             'NET_SALES': XSD.float, 'GROSS_SALES': XSD.float, 'DATE': XSD.date}
	predicates = {'QTY': cvdo.quantity, 'STORE_ZIP_CODE': dowl.postalCode}
	for rowNum, row in enumerate(reader, 1):
		dice = ndice[f"{rowNum}_ProductPurchasingBehavior"]
		for heading, value in row.items():
			metaobject = Literal(value, datatype=datatypes.get(heading, XSD.string))

			if heading == 'STORE_ZIP_CODE' and value != "":
				zipcodeInfo = zipcodes.matching(str(value))[0]
				# print(zipcodeInfo[0]['country'])
				# Country
				adm = zipcodeInfo['country']
				g.add( (dice, cvdo.hasCountry, ndice[adm]) )
				g.add( (dice, cvdo.hasCity, Literal(zipcodeInfo['city'],datatype=XSD.string)) ) # city
				g.add( (dice, cvdo.hasCounty, Literal(zipcodeInfo['county'],datatype=XSD.string)) ) # county
				g.add( (dice, geo.geometry, Literal(f"POINT({zipcodeInfo['lat']} {zipcodeInfo['long']})", datatype=virtrdf.Geometry)) ) # lat lon
				g.add( (ndice[adm], RDF.type, dowl.Country) )
				g.add( (ndice[adm], RDFS.label, Literal(adm,datatype=XSD.string)) )

			if value != "":
				g.add( (dice, RDF.type, cvdo.ProductPurchasing) )
				g.add( (dice, predicates.get(heading, cvdo[re.sub(r"_(\w)", repl, heading.lower())]),
				        metaobject) )

		# the provenance
		g.add( (dice, prov.hadPrimarySource, ndice.ProductPurchasingCovidDataset) )
		g.add( (ndice.ProductPurchasingCovidDataset, RDF.type, prov.Entity) )
		g.add( (ndice.ProductPurchasingCovidDataset, prov.generatedAtTime, Literal("2021-02-22T02:52:02Z",datatype=XSD.dateTime)) )
		g.add( (ndice.ProductPurchasingCovidDataset, prov.wasDerivedFrom, Literal("http://decadata.io/",datatype=XSD.string)) )


	print('csv has finished')


# --- demo harness (added identically to both representations; see meta.json) ---
# handleFile() takes no argument and returns nothing: it mutates the
# module-level graph `g` in place, so entry=None / module-state comparison
# (which inspects every rdflib Graph in the module's globals) is the right
# oracle here, driven by calling the region's own entry point once.
handleFile()
