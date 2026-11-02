# Extracted from dice-group/COVID19DS@7842845de5 : acaps-covid19-government-measures/toRdf.py
# region: <module> (lines 64-135, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, FOAF, RDFS, OWL, DCTERMS, SKOS, XSD
import urllib.parse
import urllib
import re
from context_shim import pd, xls   # context shim -- see meta.json
g = Graph()
cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")  #(for Object)
cvdr = Namespace("https://covid-19ds.data.dice-research.org/resource/")  #(for Subject/Resource)
dbpediaOwl = Namespace("http://dbpedia.org/ontology/")
dcmi = Namespace("http://purl.org/dc/terms/")
prov = Namespace("http://www.w3.org/ns/prov#")
dowl = Namespace("http://dbpedia.org/ontology/")
csv_data = pd.read_excel(xls, 'Dataset').fillna("unknown")

for index, row in csv_data.iterrows():
     dice = str(row['ID'])+'_GovMeasure'
     print(dice)
     iso = row["ISO"]
     row['LINK'] = row['LINK'].strip()
     if " " in row['LINK']:
          row['LINK']=urllib.parse.quote_plus(row['LINK'])

     g.add( (cvdr[iso], RDF.type, cvdo.Iso) )
     g.add( (cvdr[iso], dowl.isoCodeRegion, Literal(iso, datatype=XSD.string)) )
     # g.add((URIRef(cvdr[str(row["ID"])]), cvdo.hasISO, Literal(row["ISO"], datatype=XSD.string)))
     #g.add((cvdr.ISO, RDF.type, lgdo.Feature))
     g.add((cvdr[row["COUNTRY"]], RDFS.label, Literal(row["COUNTRY"], lang='en')))
     g.add((cvdr[row["COUNTRY"]], RDF.type, dbpediaOwl.Country))
     for p, o in ((cvdo.hasISO3, cvdr[iso]),
                  (RDF.type, cvdo.Covid19Measure),
                  (cvdo.hasCountry, cvdr[row["COUNTRY"]]),
                  (cvdo.hasPCODE, Literal(row['PCODE'], datatype=XSD.integer)),
                  (dcmi.date, Literal(row['DATE_IMPLEMENTED'], datatype=XSD.date)),
                  (cvdo.hasSource, Literal(row['SOURCE'], lang='en')),
                  (cvdo.hasSourceLink, URIRef(row['LINK'])),
                  (cvdo.entryDate, Literal(row['ENTRY_DATE'], datatype=XSD.date)),
                  (prov.hadPrimarySource, cvdr.GovMeasuresCovidDataset)):
          g.add((cvdr[dice], p, o))
     # the provenance
     g.add( (cvdr.GovMeasuresCovidDataset, RDF.type, prov.Entity) )
     g.add( (cvdr.GovMeasuresCovidDataset, prov.generatedAtTime, Literal("2021-02-22T02:52:02Z",datatype=XSD.dateTime)) )
     g.add( (cvdr.GovMeasuresCovidDataset, prov.wasDerivedFrom, Literal("https://data.humdata.org/dataset/acaps-covid19-government-measures-dataset",datatype=XSD.string)) )

     for p, column in ((cvdo.hasRegion, 'REGION'), (cvdo.hasAdminLevelName, 'ADMIN_LEVEL_NAME'),
                       (cvdo.hasLogType, 'LOG_TYPE'), (dbpediaOwl.category, 'CATEGORY'),
                       (cvdo.hasMeasure, 'MEASURE'), (cvdo.targetedPopGroup, 'TARGETED_POP_GROUP'),
                       (RDFS.comment, 'COMMENTS'), (cvdo.nonCompliance, 'NON_COMPLIANCE'),
                       (cvdo.publisher, 'SOURCE_TYPE')):
          g.add((cvdr[dice], p, Literal(row[column], datatype=XSD.string)))

     # row['Alternative source']=urllib.parse.quote_plus(row['Alternative source'])
     for a in re.split(';| \+| AND| and', row['Alternative source']):
          # if a != 'and' and a != 'AND' and a != '':
          g.add((cvdr[dice], cvdo.alternativeSource, URIRef(a.strip().replace(" ", ""))))

     # Remove the triples that I marked as "unknown"
     g.remove((None, None, URIRef("unknown")))
     for datatype in (XSD.string, XSD.integer, XSD.date):
          g.remove((None, None, Literal("unknown", datatype=datatype)))
