# Extracted from AKSW/QuitStore@7567c25da5 : quit/conf.py
# region: QuitGraphConfiguration.__init_graph_conf_from_configuration (lines 222-263, stratum sparql_literal)
# licence of the source repository: see meta.json
from quit.exceptions import InvalidConfigurationError
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.util import guess_format

def __init_graph_conf_from_configuration(self, configfileId, known_blobs):
    """Init graphs with setting from config.ttl."""
    try:
        configfile = self.repository.get(configfileId)
    except Exception as e:
        raise InvalidConfigurationError(
            "Blob for configfile with id {} not found in repository {}".format(configfileId, e))

    content = configfile.read_raw()

    try:
        self.graphconf.parse(data=content, format='turtle')
    except Exception as e:
        raise InvalidConfigurationError(
            "Configfile could not be parsed {} {}".format(configfileId, e)
        )
    nsQuit = 'http://quit.aksw.org/vocab/'
    query = 'SELECT DISTINCT ?graphuri ?filename ?format WHERE { '
    query += '  ?graph a <' + nsQuit + 'Graph> . '
    query += '  ?graph <' + nsQuit + 'graphUri> ?graphuri . '
    query += '  ?graph <' + nsQuit + 'graphFile> ?filename . '
    query += '  OPTIONAL { ?graph <' + nsQuit + 'hasFormat> ?format .} '
    query += '}'
    result = self.graphconf.query(query)

    for row in result:
        filename = str(row['filename'])
        if row['format'] is None:
            format = guess_format(filename)
        else:
            format = str(row['format'])
        if format != 'nt':
            break
        if filename not in known_blobs.keys():
            break

        graphuri = URIRef(str(row['graphuri']))

        # we store which named graph is serialized in which file
        self.graphs[graphuri] = filename
        self.files[filename] = {
            'serialization': format, 'graph': graphuri, 'oid': known_blobs[filename]}
