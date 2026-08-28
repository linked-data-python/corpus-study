# Extracted from dice-group/COVID19DS@7842845de5 : covid-19-global-travel-restrictions-and-airline-information/toRdf.py
# region: handleFile (lines 65-123, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, DCTERMS, OWL
import re
import pycountry
g = Graph()
resource = "https://covid-19ds.data.dice-research.org/resource/"
prov = Namespace("http://www.w3.org/ns/prov#")
cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")
ndice = Namespace("https://covid-19ds.data.dice-research.org/resource/") #cvdr
virtrdf = Namespace('http://www.openlinksw.com/schemas/virtrdf#')
geo = Namespace('http://www.opengis.net/ont/geosparql#')
dowl = Namespace('http://dbpedia.org/ontology/')
reader = pd.read_csv('Data WFP Coronavirus COVID-19 Travel Restrictions - COVID-19 airline restrictions information.csv', keep_default_na=False).to_dict('records', into=OrderedDict)
g = Graph()

for row in reader:
    longitude = None
    latitude = None
    for heading in row:
        heading = str(heading)

        # strName = str(row['iso3'].split(',')[0].strip())
        strName = str(row['ObjectId'])
        # snakecase to lowerCamelCase
        strCamelCase = re.sub(r"_(\w)", repl, strName)+"_AirlineRestrictions" 

        dice = URIRef(resource+strCamelCase)

        headingLower = heading.lower()
        strCamelCase = re.sub(r"_(\w)", repl, headingLower)
        metapredicate = cvdo[strCamelCase]
        metaobject = Literal(row[heading],datatype=XSD.string)

        if heading == 'X':
            longitude = row[heading]
        if heading == 'Y':
            latitude = row[heading]
        if longitude is not None and latitude is not None and longitude != '' and latitude != '':
            g.add( (dice, geo.geometry, Literal('POINT('+str(latitude)+' '+str(longitude)+')', datatype=virtrdf.Geometry)) )

        if heading == 'ObjectId':
            metaobject = Literal(row[heading],datatype=XSD.nonNegativeInteger)

        if heading == "iso3":
            iso = row[heading].split(',')
            for isoitem in iso:
                isoitem = isoitem.strip()
                g.add( (dice, cvdo.hasISO3, ndice[isoitem]) )
                g.add( (ndice[isoitem], RDF.type, cvdo.Iso) )
                g.add( (ndice[isoitem], cvdo.iso3, metaobject) )
                iso2 = pycountry.countries.get(alpha_3=row[heading])
                if iso2:
                    g.add( (ndice[isoitem], dowl.isoCodeRegion, Literal(iso2.alpha_2,datatype=XSD.string)) )

        if heading == "adm0_name":
           adm = capitalizeWords(row[heading])
           g.add( (dice, cvdo.hasCountry, ndice[adm]) )
           g.add( (ndice[adm], RDF.type, dowl.Country) )
           g.add( (ndice[adm], RDFS.label, metaobject) )

        if heading == 'source' and "http" in row[heading]:
            metaobject = URIRef(row[heading])

        if heading == "published":
            metaobject = Literal(row[heading],datatype=XSD.date)

        if row[heading] != "" and heading != "X" and heading != "Y" and heading != "iso3" and heading != "adm0_name":
            g.add( (dice, RDF.type, cvdo.AirlineRestrictions) )
            g.add( (dice, metapredicate, metaobject) )

        # the provenance
        g.add( (dice, prov.hadPrimarySource, ndice.AirlineRestrictionsCovidDataset) )
        g.add( (ndice.AirlineRestrictionsCovidDataset, RDF.type, prov.Entity) )
        g.add( (ndice.AirlineRestrictionsCovidDataset, prov.wasDerivedFrom, Literal("https://data.humdata.org/dataset/covid-19-global-travel-restrictions-and-airline-information",datatype=XSD.string)) )
