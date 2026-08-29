# Extracted from cltl/multilingual-wiki-event-pipeline@c390d931fd : classes.py
# region: IncidentCollection.serialize_as_participant_event (lines 167-262, stratum ns_def_local)
# licence of the source repository: see meta.json
import json
from rdflib.namespace import Namespace
from rdflib.namespace import RDF, RDFS
from rdflib import Graph
from rdflib import URIRef, BNode, Literal, XSD
eventtype2json={}

def serialize_as_participant_event(self, filename=None):
    """
    Serialize a collection of incidents to a .ttl file.
    """

    if self.incident_type in eventtype2json.keys():
         jsonfilename='wdt_fn_mappings/%s.json' % eventtype2json[self.incident_type]
    else:
         jsonfilename='wdt_fn_mappings/any.json'

    print(jsonfilename)
    with open(jsonfilename, 'rb') as f:
        wdt_fn_mappings_COL=json.load(f)

    g = Graph()

    # Namespaces definition
    SEM=Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/')
    WDT_ONT=Namespace('http://www.wikidata.org/wiki/')
    WDT_ENT=Namespace("http://www.wikidata.org/entity/")
    GRASP=Namespace('http://groundedannotationframework.org/grasp#')
    DCT=Namespace('http://purl.org/dc/elements/1.1/')
    FN=Namespace('http://premon.fbk.eu/resource/fn17-')
    PREMON=Namespace('https://premon.fbk.eu/resource/')
    g.bind('sem', SEM)
    g.bind('wdt', WDT_ONT)
    g.bind('wd', WDT_ENT)
    g.bind('grasp', GRASP)
    g.bind('dct', DCT)
    g.bind('fn17', FN)
    g.bind('pm', PREMON)

    # Some core URIs/Literals
    inc_type_literal=Literal(self.incident_type)
    inc_type_uri=URIRef(self.incident_type, WDT_ONT)

    country_literal=Literal('country')

    for incident in self.incidents:
        event_id = URIRef( incident.wdt_id, WDT_ENT)

        #### add the participant as sem:hasActor
        participant_id_uri = URIRef(incident.participant_id, WDT_ENT)
        g.add(( event_id, SEM.hasActor,participant_id_uri ))

        #### we get the direct event types
        for direct_type in incident.direct_types:
            direct_type_uri = URIRef(direct_type[3:], WDT_ONT)
            g.add((event_id, RDF.type, direct_type_uri))

        for ref_text in incident.reference_texts:
            # denotation of the event
            wikipedia_article=URIRef(ref_text.uri)
            g.add(( event_id, GRASP.denotedIn, wikipedia_article ))
            g.add(( wikipedia_article, DCT.description, Literal(ref_text.content) ))
            g.add(( wikipedia_article, DCT.title, Literal(ref_text.name) ))
            g.add(( wikipedia_article, DCT.language, Literal(ref_text.language) ))
            g.add(( wikipedia_article, DCT.type, URIRef('http://purl.org/dc/dcmitype/Text') ))
            for source in ref_text.primary_ref_texts:
                g.add(( wikipedia_article, DCT.source, URIRef(source) ))

        # event type information
        g.add((event_id, RDF.type, SEM.Event))
        g.add((event_id, SEM.eventType, inc_type_uri))
        g.add((event_id, RDFS.label, Literal(incident.participant_event_label)))

        # Linking to FN1.7 @ Premon
        # PIEK taking this out, was hardcoded. Why?
        # g.add(( event_id, RDF.type, FN.change_of_leadership ))

        # Map all roles to FN roles
        for predicate, wdt_prop_paths in wdt_fn_mappings_COL.items():
            if predicate in incident.extra_info.keys():
                vals=incident.extra_info[predicate]
                prefix, pid=predicate.split(':')
                if prefix=='sem':
                    RES=SEM
                else:
                    RES=PREMON
                for v in vals:
                    v=(v.split('|')[0]).strip()
                    if pid not in {'hasTimeStamp', 'time'}:
                        an_obj=URIRef(v)
                    else:
                        if v.endswith('-01-01T00:00:00Z'):
                            vyear=v[:4]
                            an_obj=Literal(vyear, datatype=XSD.gYear)
                        else:
                            an_obj=Literal(v,datatype=XSD.date)
                    g.add(( event_id, RES[pid], an_obj))

    # Done. Store the resulting .ttl file now...
    if filename: # if a filename was supplied, store it there
        g.serialize(format='turtle', destination=filename)
    else: # else print to the console
        print(g.serialize(format='turtle'))
