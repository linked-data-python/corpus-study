# Extracted from dice-group/RELD@7ca93acbb6 : V1/NYT_New.py
# region: create_rdf (lines 215-306, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD
from rdflib import Graph, URIRef, Literal, Namespace # here is some error
from  validate import containsNumber , returnValue, check_type, remove_alphaNumeric, is_date, clean_sentences ,wikidata_id_toText
subject_dict = {}
object_dict = {}
g = Graph()
prop = Namespace("https://reld.dice-research.org/schema/")
res = Namespace("https://reld.dice-research.org/resource/")
dbo = Namespace("http://dbpedia.org/ontology/")

for index, val in enumerate(info): # Code for Sentence and relevant info

    g.add((URIRef(relation),
           URIRef(prop+'distribution'), 
           Literal(val[4],datatype=XSD.string)
           ))

    for ind, v in enumerate(val[2]):
        sent_id = res+"S_"+dsName+"_"+ str(sent_counter) # will go to all code
        sent_counter = sent_counter + 1
        g.add((URIRef(relation),
           URIRef(prop+'hasSentence'), 
           URIRef(sent_id)
        ))
        g.add((URIRef(sent_id),
               URIRef(prop+'hasText'), 
               Literal(v[0],lang='en')
               ))
        for key , value in v[1].items(): # code for named entities
            if key == "listOfNamedEntities":
                for nam_e in value:
                    ne_id = res+'ne_n' + str(ne_counter)
                    #ne_id = res+ str(nam_e[0]).strip().replace(' ','_')+str(ne_counter)
                    ne_counter = ne_counter + 1
                    g.add((URIRef(sent_id),
                            URIRef(prop+'hasNamedEntity'), 
                            URIRef(ne_id)
                    ))
                    g.add((URIRef(ne_id),
                           RDF.type,
                           URIRef(dbo+remove_alphaNumeric(nam_e[1]))
                           ))
                    g.add((URIRef(ne_id),
                           RDFS.label,
                           Literal(nam_e[0],lang='en')
                           ))
            else:
                g.add((URIRef(sent_id),
                       URIRef(prop+key), 
                       Literal(value,datatype=XSD.integer)
                       ))
    ################ Subject Object Code ##################
    g.add((URIRef(sent_id),
           URIRef(prop+'numOfRelation'), 
           Literal(val[3],datatype=XSD.integer) 
           )) 
    subject_string = returnValue(subject_dict,val[0])
    sub_id = res+'sub_'+dsName+str(val[0])
    g.add((URIRef(sent_id),
           URIRef(prop+'hasSubject'), 
           URIRef(sub_id) 
           ))
    if containsNumber(str(subject_string)):
        g.add((URIRef(sub_id),
               RDFS.label, 
               Literal(subject_string,datatype=XSD.string) 
               ))


    elif check_type(str(subject_string)):
        g.add((URIRef(sub_id),
               RDFS.label, 
               Literal(subject_string,datatype=XSD.string))) 

    else:
        g.add((URIRef(sub_id),
               RDFS.label, 
               Literal(remove_alphaNumeric(subject_string),datatype=XSD.string)))


    object_string = returnValue(object_dict,val[1])#remove_alphaNumeric(val[1]) 
    obj_id = res + 'obj_'+dsName+str(val[1])
    g.add((URIRef(sent_id),
           URIRef(prop+'hasObject'), 
           URIRef(obj_id) 
           ))
    if containsNumber(str(object_string)):
        g.add((URIRef(obj_id),
               RDFS.label, 
               Literal(object_string,datatype=XSD.string) # debatable because the entities might be same
               ))

    elif check_type(str(object_string)):
        g.add((URIRef(obj_id),
            RDFS.label, 
            Literal(object_string,datatype=XSD.string) 
            ))
    else:
        g.add((URIRef(obj_id),
               RDFS.label, 
               Literal(remove_alphaNumeric(object_string),datatype=XSD.string) # debatable because the entities might be same
               ))
