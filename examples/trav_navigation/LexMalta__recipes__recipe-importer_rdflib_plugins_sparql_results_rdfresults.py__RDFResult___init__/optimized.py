# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/plugins/sparql/results/rdfresults.py
# region: RDFResult.__init__ (lines 13-59, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, Namespace, Variable
from rdflib.query import Result, ResultParser
RS = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/result-set#")

def __init__(self, source, **kwargs):

    graph = source if isinstance(source, Graph) else Graph().parse(source, **kwargs)

    rs = graph.value(predicate=RDF.type, object=RS.ResultSet)
    # there better be only one :)

    if rs is None:
        Result.__init__(self, "CONSTRUCT")
        # use a new graph
        self.graph = Graph()
        self.graph += graph
        return

    askAnswer = graph.value(rs, RS.boolean)

    if askAnswer is not None:
        Result.__init__(self, "ASK")
        self.askAnswer = askAnswer.value
        if askAnswer.value is None:
            raise Exception("Malformed boolean in ask answer!")
        return

    Result.__init__(self, "SELECT")
    self.vars = [Variable(v) for v in graph.objects(rs, RS.resultVariable)]
    self.bindings = []
    for s in graph.objects(rs, RS.solution):
        self.bindings.append({Variable(graph.value(b, RS.variable)): graph.value(b, RS.value)
                              for b in graph.objects(s, RS.binding)})
