# Context shim (see meta.json): the part of brickschema.graph.Graph that the
# region uses, transcribed from the BrickSchema/py-brickschema checkout --
# prefix binding at construction, `load_file`, and the `add` that accepts a
# list of (predicate, object) pairs as the object of a triple and substitutes
# a blank node for it.  Identical for both representations.
#
# ONE DELIBERATE DIFFERENCE, applied identically to both sides: load_file
# silently ignores a missing file.  The region loads "../../Brick.ttl", which
# is a *generated* artefact absent from the BrickSchema/Brick checkout (and
# ~10 MB when built); without it the two SPARQL queries at the end of the
# region simply return no rows on both sides.
import os

import rdflib

from . import namespaces as ns


class Graph(rdflib.Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ns.bind_prefixes(self)

    def load_file(self, filename=None, source=None, format=None):
        if filename is not None:
            if not os.path.exists(filename):
                return self          # see the note above
            fmt = format if format else rdflib.util.guess_format(filename)
            self.parse(filename, format=fmt)
        elif source is not None:
            self.parse(source=source, format=format or "ttl")
        else:
            raise Exception("Must provide either a filename or file-like source")
        return self

    def add(self, *triples):
        """Adds triples to the graph.

        If the object of a triple is a list/tuple of length-2 lists/tuples,
        a blank node is substituted as the object of the original triple and
        the items are added as predicate/object pairs on that blank node --
        i.e. `X Y [ A B ; C D ]` in Turtle.
        """
        for triple in triples:
            assert len(triple) == 3
            obj = triple[2]
            if isinstance(obj, (list, tuple)):
                for suffix in obj:
                    assert len(suffix) == 2
                bnode = rdflib.BNode()
                self.add((triple[0], triple[1], bnode))
                for (nested_pred, nested_obj) in obj:
                    self.add((bnode, nested_pred, nested_obj))
            else:
                super().add(triple)
