# Context shim (see meta.json): the classes and the one helper that
# `_target_parse` uses, copied verbatim from MaximeJakubowski/sls_project@58f7d7840f
# (slsparser/pathls.py: POp, PANode; slsparser/shapels.py: Op, SANode,
# _extract_parameter_values), so the region executes outside the package.
# Identical bindings for both representations.
from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum, auto

from rdflib import Graph
from rdflib import SH, RDF, RDFS
from rdflib.term import URIRef, Literal, BNode, Node




class POp(Enum):  # Path Operator
    PROP = auto()
    INV = auto()
    ZEROORONE = auto()
    ALT = auto()
    KLEENE = auto()
    COMP = auto()
    ID = auto() # for EQ and DISJ, no child


class PANode:  # Path Algebra Node
    """Ordered tree representing a path expression"""

    def __init__(self, pop: POp, children: List):
        self.pop = pop
        self.children = children

    def __eq__(self, other):
        """ Overwrite the '==' operator """
        if not isinstance(other, PANode):
            return False

        if self.pop == POp.PROP:
            return self.pop == other.pop and \
              self.children[0] == other.children[0]

        if len(self.children) != len(other.children):
            return False
        same_children = True
        for child_self, child_other in zip(self.children, other.children):
            if type(child_self) == BNode and type(child_other) == BNode:
                continue
            same_children = same_children and child_self == child_other

        return self.pop == other.pop and same_children

    def __repr__(self):
        """ Pretty representation of the PANode tree """
        out = '\n('
        out += str(self.pop) + ' '
        for c in self.children:
            for line in c.__repr__().split('\n'):
                out += ' ' + line + '\n'
        out = out[:-1] + ')'
        return out



class Op(Enum):
    HASVALUE = auto() # Op.HASVALUE val
    NOT = auto() # Op.NOT SANode
    AND = auto() # Op.AND SANode SANode ...
    OR = auto() # Op.OR SANode SANode ...
    TEST = auto() # Op.TEST "testname" argument
    # possible testnames: [testname, element1, element2, ...]
    # - [sh:LanguageInConstraintComponent ...]
    # - [sh:DatatypeConstraintComponent, xsd:string] or other datatypes
    # - [sh:NodeKindConstraintComponent, sh:iri] or other: any of the six combinations
    # - [sh:PatternConstraintComponent, patternstring, flags]
    # - [numeric_range, <range_statement>, <value>]
    #   - <range_statement> is one of: sh:MinExclusiveConstraintComponent, sh:MaxExclusiveConstraintComponent,
    #       sh:MinInclusiveConstraintComponent, sh:MaxInclusiveConstraintComponent
    #   - <value> is an rdflib literal (numeric) value
    #   There is at most one of min_... and at most one of max_... followed by a value
    # - [length_range, <range_statement>, <value>]
    #   - <range_statement> is one of: sh:MinLengthConstraintComponent, sh:MaxLengthConstraintComponent
    #   - <value> is an rdflib literal (numeric) value
    #   There is at most one of min_... and at most one of max_... followed by a value
    HASSHAPE = auto() # Op.HASSHAPE iri
    FORALL = auto() # Op.FORALL PANode SANode
    EQ = auto() # Op.EQ PANode PANode
    DISJ = auto() # Op.DISJ PANode PANode
    # for eq(id,p) and disj(id,p) I add id to pathls.POp.ID
    CLOSED = auto() # Op.CLOSED iri iri ...
    LESSTHAN = auto() # Op.LESSTHAN PANode PANode
    LESSTHANEQ = auto() # Op.LESSTHANEQ PANode PANode
    UNIQUELANG = auto() # Op.UNIQUELANG PANode
    TOP = auto() # Op.TOP
    BOT = auto() # Op.BOT

    COUNTRANGE = auto() # Op.COUNTRANGE num num/None PANode SANode


class SANode:  # Shape Algebra Node
    def __init__(self, op: Op, children: List, constraintComponent: URIRef | Tuple[URIRef, ...]| None = None):
        self.op = op
        self.children = children
        self.constraintComponent = constraintComponent

    def __eq__(self, other):
        """ Overwrite the '==' operator """
        if not isinstance(other, SANode):
            return False
        
        if len(self.children) != len(other.children):
            return False

        same_children = True
        for child_self, child_other in zip(self.children, other.children):
            if type(child_self) == BNode and type(child_other) == BNode:
                continue
            same_children = same_children and child_self == child_other

        return (self.op == other.op) and same_children and\
            self.constraintComponent == other.constraintComponent

    def __repr__(self):
        """ Pretty representation of the SANode tree """
        out = '\n('
        out += str(self.op) + '  cc=' + str(self.constraintComponent) + ' '
        for c in self.children:
            for line in c.__repr__().split('\n'):
                out += ' ' + line + '\n'
        out = out[:-1] + ')'
        return out



def _extract_parameter_values(graph: Graph, shapename: Node, parameter: URIRef) -> List[Node]:
    return list(graph.objects(shapename, parameter))

