# Extracted from dice-group/COVID19DS@7842845de5 : covid-19-global-travel-restrictions-and-airline-information/toRdf.py
# region: handleFile (lines 65-123, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, DCTERMS, OWL
import re
import pycountry
from _context import repl, capitalizeWords, reader
g = Graph()
resource = "https://covid-19ds.data.dice-research.org/resource/"
prov = Namespace("http://www.w3.org/ns/prov#")
cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")
ndice = Namespace("https://covid-19ds.data.dice-research.org/resource/") #cvdr
virtrdf = Namespace('http://www.openlinksw.com/schemas/virtrdf#')
geo = Namespace('http://www.opengis.net/ont/geosparql#')
dowl = Namespace('http://dbpedia.org/ontology/')
# reader restored from the context shim: no pandas in the study venv, and the
# source CSV is not committed to the repository at the pinned commit either
# (see _context.py) -- reader is not the mechanical `pd.read_csv(...)` line
# from the pipeline draft, it is the missing binding itself.
g = Graph()

datatypes = {'ObjectId': XSD.nonNegativeInteger, 'published': XSD.date}
for row in reader:
    # snakecase to lowerCamelCase
    dice = ndice[re.sub(r"_(\w)", repl, str(row['ObjectId'])) + "_AirlineRestrictions"]
    if row.get('X') not in (None, '') and row.get('Y') not in (None, ''):
        g.add((dice, geo.geometry,
               Literal(f"POINT({row['Y']} {row['X']})", datatype=virtrdf.Geometry)))

    for heading, value in row.items():
        metaobject = Literal(value, datatype=datatypes.get(heading, XSD.string))
        if heading == 'source' and "http" in value:
            metaobject = URIRef(value)

        if heading == "iso3":
            iso2 = pycountry.countries.get(alpha_3=value)
            for isoitem in value.split(','):
                isoitem = isoitem.strip()
                g += [(dice, cvdo.hasISO3, ndice[isoitem]),
                      (ndice[isoitem], RDF.type, cvdo.Iso),
                      (ndice[isoitem], cvdo.iso3, metaobject)]
                if iso2:
                    g.add((ndice[isoitem], dowl.isoCodeRegion,
                           Literal(iso2.alpha_2, datatype=XSD.string)))
        elif heading == "adm0_name":
            adm = capitalizeWords(value)
            g += [(dice, cvdo.hasCountry, ndice[adm]),
                  (ndice[adm], RDF.type, dowl.Country),
                  (ndice[adm], RDFS.label, metaobject)]
        elif heading not in ('X', 'Y') and value != "":
            g += [(dice, RDF.type, cvdo.AirlineRestrictions),
                  (dice, cvdo[re.sub(r"_(\w)", repl, heading.lower())], metaobject)]

    # the provenance
    g += [(dice, prov.hadPrimarySource, ndice.AirlineRestrictionsCovidDataset),
          (ndice.AirlineRestrictionsCovidDataset, RDF.type, prov.Entity),
          (ndice.AirlineRestrictionsCovidDataset, prov.wasDerivedFrom, Literal(
              "https://data.humdata.org/dataset/covid-19-global-travel-restrictions-and-airline-information",
              datatype=XSD.string))]
