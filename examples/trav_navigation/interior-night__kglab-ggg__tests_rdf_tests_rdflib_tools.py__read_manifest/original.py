# Extracted from interior-night/kglab-ggg@735ae3c49c : tests/rdf_tests/rdflib_tools.py
# region: read_manifest (lines 66-181, stratum trav_navigation)
# licence of the source repository: see meta.json
from typing import Iterable, List, NamedTuple, Optional, Tuple, Union, cast
from rdflib import RDF, RDFS, Graph, Namespace, BNode
from rdflib.term import Identifier, Node, URIRef
MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")
QT = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-query#")
UP = Namespace("http://www.w3.org/2009/sparql/tests/test-update#")
ResultType = Union[Identifier, Tuple[Identifier, List[Tuple[Identifier, Identifier]]]]
GraphDataType = Union[List[Identifier], List[Tuple[Identifier, Identifier]]]

def read_manifest(f, base=None, legacy=False) -> Iterable[Tuple[Node, URIRef, RDFTest]]:
    def _str(x):
        if x is not None:
            return str(x)
        return None

    g = Graph()
    g.parse(f, publicID=base, format="turtle")

    for m in g.subjects(RDF.type, MF.Manifest):

        for col in g.objects(m, MF.include):
            for i in g.items(col):
                for x in read_manifest(i):
                    yield x

        for col in g.objects(m, MF.entries):
            e: URIRef
            for e in g.items(col):

                _type = g.value(e, RDF.type)

                # if _type in (MF.ServiceDescriptionTest, MF.ProtocolTest):
                #     continue  # skip tests we do not know

                name = g.value(e, MF.name)
                comment = g.value(e, RDFS.comment)
                data = None
                graphdata: Optional[GraphDataType] = None
                res: Optional[ResultType] = None
                syntax = True

                if _type in (MF.QueryEvaluationTest, MF.CSVResultFormatTest):
                    a = g.value(e, MF.action)
                    query = g.value(a, QT.query)
                    data = g.value(a, QT.data)
                    # NOTE: Casting to identifier because g.objects return Node
                    # but should probably return identifier instead.
                    graphdata = list(
                        cast(Iterable[Identifier], g.objects(a, QT.graphData))
                    )
                    res = g.value(e, MF.result)
                elif _type in (MF.UpdateEvaluationTest, UP.UpdateEvaluationTest):
                    a = g.value(e, MF.action)
                    query = g.value(a, UP.request)
                    data = g.value(a, UP.data)
                    graphdata = cast(List[Tuple[Identifier, Identifier]], [])
                    for gd in g.objects(a, UP.graphData):
                        graphdata.append(
                            (g.value(gd, UP.graph), g.value(gd, RDFS.label))
                        )

                    r = g.value(e, MF.result)
                    resdata: Identifier = g.value(r, UP.data)
                    resgraphdata: List[Tuple[Identifier, Identifier]] = []
                    for gd in g.objects(r, UP.graphData):
                        resgraphdata.append(
                            (g.value(gd, UP.graph), g.value(gd, RDFS.label))
                        )

                    res = resdata, resgraphdata

                elif _type in (MF.NegativeSyntaxTest11, MF.PositiveSyntaxTest11):
                    query = g.value(e, MF.action)
                    syntax = _type == MF.PositiveSyntaxTest11

                elif _type in (
                    MF.PositiveUpdateSyntaxTest11,
                    MF.NegativeUpdateSyntaxTest11,
                ):
                    query = g.value(e, MF.action)
                    syntax = _type == MF.PositiveUpdateSyntaxTest11

                elif _type in (
                    RDFT.TestNQuadsPositiveSyntax,
                    RDFT.TestNQuadsNegativeSyntax,
                    RDFT.TestTrigPositiveSyntax,
                    RDFT.TestTrigNegativeSyntax,
                    RDFT.TestNTriplesPositiveSyntax,
                    RDFT.TestNTriplesNegativeSyntax,
                    RDFT.TestTurtlePositiveSyntax,
                    RDFT.TestTurtleNegativeSyntax,
                ):
                    query = g.value(e, MF.action)
                    syntax = _type in (
                        RDFT.TestNQuadsPositiveSyntax,
                        RDFT.TestNTriplesPositiveSyntax,
                        RDFT.TestTrigPositiveSyntax,
                        RDFT.TestTurtlePositiveSyntax,
                    )

                elif _type in (
                    RDFT.TestTurtleEval,
                    RDFT.TestTurtleNegativeEval,
                    RDFT.TestTrigEval,
                    RDFT.TestTrigNegativeEval,
                ):
                    query = g.value(e, MF.action)
                    res = g.value(e, MF.result)
                    syntax = _type in (RDFT.TestTurtleEval, RDFT.TestTrigEval)

                else:
                    pass
                    print("I dont know DAWG Test Type %s" % _type)
                    continue

                yield e, _type, RDFTest(
                    e,
                    _str(name),
                    _str(comment),
                    _str(data),
                    graphdata,
                    _str(query),
                    res,
                    syntax,
                )
