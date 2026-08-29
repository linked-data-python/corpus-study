# Extracted from dice-group/COVID19DS@7842845de5 : unified_covid19/toRdf.py
# region: handleFile (lines 140-156, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, DCTERMS, OWL
g = Graph()
resourse = "https://covid-19ds.data.dice-research.org/resource/"
cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")
ndice = Namespace("https://covid-19ds.data.dice-research.org/resource/") #cvdr
g = Graph()

for i in range(0, len(covid19data['ID'])):
    dice = URIRef(resourse+str(covid19data['ID'][i]))
    pol = 'Covid19Data_'+str(covid19data['ID'][i])+'_'+ covid19data['Type'][i]+'_'+str(covid19data['Date'][i])
    g.add( (dice, cvdo.hasCasesPerAgeRecord, ndice[pol]) )
    g.add( (ndice[pol], RDF.type, cvdo.CasesPerAgeRecord) )
    g.add( (ndice[pol], cvdo.date, Literal(covid19data['Date'][i],datatype=XSD.date)) )
    g.add( (ndice[pol], cvdo.type, Literal(covid19data['Type'][i],datatype=XSD.string)) )
    if not isnan(covid19data['Cases'][i]):
        g.add( (ndice[pol], cvdo.cases, Literal(covid19data['Cases'][i],datatype=XSD.nonNegativeInteger)) )
    if not isnan(covid19data['Cases_New'][i]):
        g.add( (ndice[pol], cvdo.casesNew, Literal(covid19data['Cases_New'][i],datatype=XSD.nonNegativeInteger)) )
    if not isnan(covid19data['Age'][i]):
        g.add( (ndice[pol], cvdo.age, Literal(covid19data['Age'][i],datatype=XSD.string)) )
    if not isnan(covid19data['Sex'][i]):
        g.add( (ndice[pol], cvdo.sex, Literal(covid19data['Sex'][i],datatype=XSD.string)) )
    if not isnan(covid19data['Source'][i]):
        g.add( (ndice[pol], cvdo.source, Literal(covid19data['Source'][i],datatype=XSD.string)) )
