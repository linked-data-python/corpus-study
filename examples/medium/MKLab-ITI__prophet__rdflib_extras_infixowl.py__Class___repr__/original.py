# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class.__repr__ (lines 1231-1294, band medium)
# licence of the source repository: see meta.json
from rdflib import (
    BNode,
    Literal,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Variable
)
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def __repr__(self, full=False, normalization=True):
    """
    Returns the Manchester Syntax equivalent for this class
    """
    exprs = []
    sc = list(self.subClassOf)
    ec = list(self.equivalentClass)
    for boolClass, p, rdfList in self.graph.triples_choices(
        (self.identifier,
         [OWL_NS.intersectionOf,
          OWL_NS.unionOf],
         None)):
        ec.append(manchesterSyntax(rdfList, self.graph, boolean=p))
    dc = list(self.disjointWith)
    c = self.complementOf
    if c:
        dc.append(c)
    klassKind = ''
    label = list(self.graph.objects(self.identifier, RDFS.label))
    label = label and '(' + label[0] + ')' or ''
    if sc:
        if full:
            scJoin = '\n                '
        else:
            scJoin = ', '
        necStatements = [
            isinstance(s, Class) and isinstance(self.identifier, BNode) and
            repr(CastClass(s, self.graph)) or
            # repr(BooleanClass(classOrIdentifier(s),
            #                  operator=None,
            #                  graph=self.graph)) or
            manchesterSyntax(classOrIdentifier(s), self.graph) for s in sc]
        if necStatements:
            klassKind = "Primitive Type %s" % label
        exprs.append("SubClassOf: %s" % scJoin.join(
            [str(n) for n in necStatements]))
        if full:
            exprs[-1] = "\n    " + exprs[-1]
    if ec:
        nec_SuffStatements = [
            isinstance(s, str) and s or
            manchesterSyntax(classOrIdentifier(s), self.graph) for s in ec]
        if nec_SuffStatements:
            klassKind = "A Defined Class %s" % label
        exprs.append("EquivalentTo: %s" % ', '.join(nec_SuffStatements))
        if full:
            exprs[-1] = "\n    " + exprs[-1]
    if dc:
        exprs.append("DisjointWith %s\n" % '\n                 '.join(
            [manchesterSyntax(classOrIdentifier(s), self.graph)
                for s in dc]))
        if full:
            exprs[-1] = "\n    " + exprs[-1]
    descr = list(self.graph.objects(self.identifier, RDFS.comment))
    if full and normalization:
        klassDescr = klassKind and '\n    ## %s ##' % klassKind +\
            (descr and "\n    %s" % descr[0] or '') + \
            ' . '.join(exprs) or ' . '.join(exprs)
    else:
        klassDescr = full and (descr and "\n    %s" %
                               descr[0] or '') or '' + ' . '.join(exprs)
    return (isinstance(self.identifier, BNode)
            and "Some Class "
            or "Class: %s " % self.qname) + klassDescr
