# Context shim (see meta.json): minimal reproduction of the
# `FunctionExecution`/`FunctionInfo` namedtuples from alpaca/alpaca_types.py,
# and a stand-in for `AlpacaProvDocument` (alpaca/serialization/prov.py),
# the class `_add_function_execution` is a method of, at
# INM-6/alpaca@2b8dd34fc6. Identical bindings for both representations.
from collections import namedtuple

# Reproduced verbatim from alpaca/alpaca_types.py:29-44.
FunctionInfo = namedtuple('FunctionInfo', ('name', 'module', 'version'))

FunctionExecution = namedtuple('FunctionExecution', (
    'function', 'input', 'params', 'output', 'arg_map', 'kwarg_map',
    'call_ast', 'code_statement', 'time_stamp_start', 'time_stamp_end',
    'return_targets', 'order', 'execution_id'))


def membership_execution(container, agent_unused, child='child'):
    """A `FunctionExecution` for a subscript/attribute access -- the shape
    `Provenance._add_container_relationships` builds at
    alpaca/decorator.py:522-538: `input={0: container}`, `output={0: ...}`,
    `params={'index': ...}` -- so the region's membership branch (the only
    branch this study's one extracted operation lives in) takes the path it
    takes in the real package."""
    return FunctionExecution(
        function=FunctionInfo(name='subscript', module='', version=''),
        input={0: container}, params={'index': 0}, output={0: child},
        arg_map=None, kwarg_map=None, call_ast=None, code_statement=None,
        time_stamp_start=None, time_stamp_end=None, return_targets=[],
        order=None, execution_id=None)


class AlpacaProvDocument:
    """Stand-in for the class `_add_function_execution` is a method of. Only
    `self.graph` (the document's own rdflib Graph, see the real
    `AlpacaProvDocument.__init__`) and the helper methods the membership
    branch calls are reproduced. This region's single extracted operation
    (`rdf_ops: 1` in meta.json) is the existence read guarding the call to
    `_wasAttributedTo`; the real graph-building logic inside
    `_create_entity`/`_wasAttributedTo`/`_add_membership` is NOT part of the
    region, so calls are recorded rather than executed -- whether
    `_wasAttributedTo` is called is the one observable effect the read
    decides."""

    def __init__(self, graph):
        self.graph = graph
        self.was_attributed_to_calls = []

    def _create_entity(self, value):
        # Identity stand-in: in this shim's fixtures the argument already
        # IS the RDF term the real method would mint/look up.
        return value

    def _wasAttributedTo(self, entity, agent):
        self.was_attributed_to_calls.append((entity, agent))

    def _add_membership(self, container_entity, child_entity, params):
        pass
