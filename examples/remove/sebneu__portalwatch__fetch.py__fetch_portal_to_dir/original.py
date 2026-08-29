# Extracted from sebneu/portalwatch@a514eba7bf : fetch.py
# region: fetch_portal_to_dir (lines 28-75, stratum remove)
# licence of the source repository: see meta.json
import os
from datetime import datetime
logger = logging.getLogger(__name__)
import rdflib
from rdflib import URIRef, RDF, Namespace, Literal
from converter import portal_fetch_processors
from db import ODPW_GRAPH
from converter.portal_fetch_processors import PROV_ACTIVITY
PROV = Namespace('http://www.w3.org/ns/prov#')
LOCN = Namespace("http://www.w3.org/ns/locn#")
ODPW = Namespace('http://data.wu.ac.at/ns/odpw#')
PW_AGENT = URIRef("https://data.wu.ac.at/portalwatch")

def fetch_portal_to_dir(p, snapshot, path, format='nt', skip_portal=False, remove_geometries=False):
    try:
        logger.info("FETCH: " + p['id'])
        portal_ref = rdflib.URIRef(p['uri'])
        portal_api = p['apiuri']
        portal_id = p['id']
        software = p['software']
        fp = os.path.join(path, portal_id) + '.' + format
        # skip portal if exists
        if skip_portal and os.path.exists(fp):
            logger.info("File exists, skip portal: " + p['id'])
            return

        # log execution time
        start_time = datetime.now()
        portal_activity = URIRef("https://data.wu.ac.at/portalwatch/portal/" + portal_id + '/' + str(snapshot))

        proc = portal_fetch_processors.getPortalProcessor(software)
        g = rdflib.Graph()
        proc.fetchAndConvertToDCAT(g, portal_ref, portal_api, snapshot, portal_activity)

        end_time = datetime.now()

        # prov information
        g.add((portal_activity, RDF.type, PROV.Activity))
        g.add((portal_activity, PROV.startedAtTime, Literal(start_time)))
        g.add((portal_activity, PROV.endedAtTime, Literal(end_time)))
        g.add((portal_activity, PROV.wasAssociatedWith, PW_AGENT))
        g.add((portal_activity, ODPW.snapshot, Literal(int(snapshot))))

        sn_graph = URIRef(ODPW_GRAPH + '/' + str(snapshot))
        sn_activity = rdflib.URIRef(PROV_ACTIVITY + str(snapshot))
        g.add((sn_activity, RDF.type, PROV.Activity))
        g.add((sn_activity, PROV.generated, sn_graph))

        g.add((portal_activity, ODPW.fetched, portal_ref))
        g.add((portal_ref, ODPW.wasFetchedBy, portal_activity))
        g.add((portal_activity, PROV.wasStartedBy, sn_activity))

        # remove GeoSPARQL geometries
        if remove_geometries:
            for s, p, o in g.triples((None, LOCN.geometry, None)):
                g.remove((s, p, o))

        # serialize
        g.serialize(fp, format=format)
    except Exception as e:
        logger.exception("Portal fetch error: " + p['id'] + ', ' + str(e))
