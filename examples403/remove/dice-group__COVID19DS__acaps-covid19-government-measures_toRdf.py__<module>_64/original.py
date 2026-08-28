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
csv_data = pd.read_excel(xls, 'Dataset')
csv_data = csv_data.fillna("unknown")

for index, row in csv_data.iterrows():
     dice = str(row['ID'])+'_GovMeasure'
     print(dice)
     iso = row["ISO"]
     g.add( (cvdr[dice], cvdo.hasISO3, cvdr[iso]) )
     g.add( (cvdr[iso], RDF.type, cvdo.Iso) )
     g.add( (cvdr[iso], dowl.isoCodeRegion, Literal(row["ISO"], datatype=XSD.string)) )
     # g.add((URIRef(cvdr[str(row["ID"])]), cvdo.hasISO, Literal(row["ISO"], datatype=XSD.string)))

     g.add((URIRef(cvdr[dice]), RDF.type, cvdo.Covid19Measure))
     #g.add((cvdr.ISO, RDF.type, lgdo.Feature))

     g.add((URIRef(cvdr[dice]), cvdo.hasCountry, URIRef(cvdr[row["COUNTRY"]])))

     g.add((URIRef(cvdr[str(row["COUNTRY"])]), RDFS.label, Literal(row["COUNTRY"], lang='en')))
     g.add((URIRef(cvdr[str(row["COUNTRY"])]), RDF.type, dbpediaOwl.Country))

     g.add((URIRef(cvdr[dice]), cvdo.hasRegion, Literal(row["REGION"], datatype=XSD.string)))     

     g.add((URIRef(cvdr[dice]), cvdo.hasAdminLevelName, Literal(row['ADMIN_LEVEL_NAME'], datatype=XSD.string)))

     g.add((URIRef(cvdr[dice]),  cvdo.hasPCODE, Literal(row['PCODE'], datatype=XSD.integer)))

     g.add((URIRef(cvdr[dice]), cvdo.hasLogType, Literal(row['LOG_TYPE'], datatype=XSD.string)))

     g.add((URIRef(cvdr[dice]), dbpediaOwl.category, Literal(row['CATEGORY'], datatype=XSD.string)))

     g.add((URIRef(cvdr[dice]), cvdo.hasMeasure, Literal(row['MEASURE'], datatype=XSD.string)))

     g.add((URIRef(cvdr[dice]), cvdo.targetedPopGroup, Literal(row['TARGETED_POP_GROUP'], datatype=XSD.string)))
     g.add((URIRef(cvdr[dice]), RDFS.comment, Literal(row['COMMENTS'], datatype=XSD.string)))
     g.add((URIRef(cvdr[dice]), cvdo.nonCompliance, Literal(row['NON_COMPLIANCE'], datatype=XSD.string)))
     g.add((URIRef(cvdr[dice]), dcmi.date, Literal(row['DATE_IMPLEMENTED'], datatype=XSD.date)))

     g.add((URIRef(cvdr[dice]), cvdo.hasSource, Literal(row['SOURCE'],lang='en')))
     g.add((URIRef(cvdr[dice]), cvdo.publisher , Literal(row['SOURCE_TYPE'], datatype=XSD.string)))

     row['LINK'] = row['LINK'].strip()
     if " " in row['LINK']:
          row['LINK']=urllib.parse.quote_plus(row['LINK'])

     g.add((URIRef(cvdr[dice]), cvdo.hasSourceLink, URIRef(row['LINK'])))
     g.add((URIRef(cvdr[dice]), cvdo.entryDate, Literal(row['ENTRY_DATE'], datatype=XSD.date)))

     # row['Alternative source']=urllib.parse.quote_plus(row['Alternative source'])
     altSources = None

     altSources = re.split(';| \+| AND| and', row['Alternative source'])


     if altSources:
          for a in altSources:
               # if a != 'and' and a != 'AND' and a != '':
               g.add((URIRef(cvdr[dice]), cvdo.alternativeSource, URIRef(a.strip().replace(" ", ""))))
     else:
          if "http" in row['Alternative source']:
               g.add((URIRef(cvdr[dice]), cvdo.alternativeSource, URIRef(row['Alternative source'].strip())))
          else:
               g.add((URIRef(cvdr[dice]), cvdo.alternativeSource, Literal(row['Alternative source'], datatype=XSD.string))) 

     # the provenance
     g.add( (cvdr[dice], prov.hadPrimarySource, cvdr.GovMeasuresCovidDataset) )
     g.add( (cvdr.GovMeasuresCovidDataset, RDF.type, prov.Entity) )
     g.add( (cvdr.GovMeasuresCovidDataset, prov.generatedAtTime, Literal("2021-02-22T02:52:02Z",datatype=XSD.dateTime)) )
     g.add( (cvdr.GovMeasuresCovidDataset, prov.wasDerivedFrom, Literal("https://data.humdata.org/dataset/acaps-covid19-government-measures-dataset",datatype=XSD.string)) )


     # Remove the triples that I marked as "unknown"
     g.remove((None, None, URIRef("unknown")))
     g.remove((None, None, Literal("unknown",datatype=XSD.string)))
     g.remove((None, None, Literal("unknown",datatype=XSD.integer)))
     g.remove((None, None, Literal("unknown",datatype=XSD.date)))
