# Extracted from sebneu/portalwatch@a514eba7bf : converter/portal_fetch_processors.py
# region: CKANDCAT.fetchAndConvertToDCAT (lines 296-320, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from rdflib import URIRef
from rdflib.namespace import RDF
from utils.ssl_ignore import no_ssl_verification
logger = logging.getLogger(__name__)
from converter.dataset_converter import namespaces, DCAT, convert_socrata, graph_from_opendatasoft, \
    graph_from_data_gouv_fr, CKANConverter
import quality

def fetchAndConvertToDCAT(self, graph, portal_ref, portal_api, snapshot, activity, format="ttl"):

    logger.debug('Fetching CKAN portal via RDF endpoint: ' + portal_api)

    with no_ssl_verification():
        graph.parse(portal_api, format=format)
        cur = graph.value(predicate=RDF.type, object=namespaces['hydra'].PagedCollection)
        next_page = graph.value(subject=cur, predicate=namespaces['hydra'].nextPage)
        page = 0
        while next_page:
            page += 1
            if page % 10 == 0:
                logger.debug('Processed pages:' + str(page))

            p = str(next_page)
            g = rdflib.Graph()
            g.parse(p, format=format)
            next_page = g.value(subject=URIRef(next_page), predicate=namespaces['hydra'].nextPage)
            graph.parse(p, format=format)

        logger.debug('Total pages:' + str(page))
        logger.info('Fetching finished')

        for d in graph.subjects(RDF.type, DCAT.Dataset):
            quality.add_quality_measures(d, graph, activity)
