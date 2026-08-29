# Extracted from ktbs/ktbs@4f9f50c770 : utest/example2.py
# region: Item2Implementation.ack_edit (lines 130-137, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Literal, Graph, URIRef, XSD
from .example1 import do_tests, EXAMPLE, GroupImplementation, GroupMixin, \
    ItemImplementation, ItemMixin

def ack_edit(self, parameters, prepared):
    """I override :meth:`rdfrest.cores.local.EditableMixin.ack_edit`

    I update the special property number_of_tags"""
    super(Item2Implementation, self).ack_edit(parameters, prepared)
    with self.edit(_trust=True) as graph:
        graph.set((self.uri, EXAMPLE.number_of_tags,
                   Literal(len(self.tags))))
