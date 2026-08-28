# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/api/base.py
# region: BaseMixin.create_method (lines 202-251, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, RDF, URIRef
from rdfrest.exceptions import InvalidDataError
from rdfrest.util import coerce_to_node, coerce_to_uri, parent_uri
from ..namespace import KTBS
from ..utils import extend_api, SKOS

def create_method(self, id=None, parent=None, parameters=None, label=None,
                  graph=None):
    """Create a new computed trace in this trace base.

    :param id: see :ref:`ktbs-resource-creation`
    :param parent: parent method (required)
    :param parameters: method parameters
    :param label: explain.
    :param graph: see :ref:`ktbs-resource-creation`

    :rtype: `~.method.MethodMixin`:class:
    """
    # redefining built-in 'id' #pylint: disable-msg=W0622

    # We somehow duplicate Method.check_new_graph here, but this is
    # required if we want to be able to set _trust=True below.
    # Furthermore, the signature of this method makes it significantly
    # easier to produce a valid graph, so there is a benefit to this
    # duplication.

    if parent is None:
        raise ValueError("parent is mandatory")
    trust = graph is None  and  id is None
    node = coerce_to_node(id, self.uri)
    parent = coerce_to_uri(parent, self.uri)
    if parameters is None:
        parameters = {}

    if trust:
        if parent.startswith(self.uri):
            if not (parent, RDF.type, KTBS.Method) in self.state:
                raise InvalidDataError("Parent <%s> is not a Method"
                                       % parent)
        else:
            trust = False # could be built-in, let impl/server check
    if graph is None:
        graph = Graph()
    graph.add((self.uri, KTBS.contains, node))
    graph.add((node, RDF.type, KTBS.Method))
    graph.add((node, KTBS.hasParentMethod, parent))
    for key, value in parameters.items():
        if "=" in key:
            raise ValueError("Parameter name can not contain '=': %s", key)
        graph.add((node, KTBS.hasParameter,
                   Literal("%s=%s" % (key, value))))
    if label:
        graph.add((node, SKOS.prefLabel, Literal(label)))
    uris = self.post_graph(graph, None, trust, node, KTBS.Method)
    assert len(uris) == 1
    return self.factory(uris[0], [KTBS.Method])
