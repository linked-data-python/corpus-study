# Extracted from RDFLib/pySHACL@469cca7a22 : pyshacl/graph_abstraction.py
# region: RdfLibDataGraph.remove (lines 310-324, stratum remove)
# licence of the source repository: see meta.json
from typing import Any, Callable, Dict, Generator, Iterable, Mapping, Sequence, Tuple, Type, Union
from rdflib import Dataset as rdf_Dataset
from rdflib.term import (
    IdentifiedNode as rdf_IdentifiedNode,
)
from rdflib.term import (
    Literal as rdf_Literal,
)

def remove(
    self,
    triple: Tuple[
        Union[rdf_IdentifiedNode, rdf_Literal],
        rdf_IdentifiedNode,
        Union[rdf_Literal, rdf_IdentifiedNode],
    ],
):
    if self.locked_context is not None:
        if isinstance(self.impl, rdf_Dataset):
            return self.impl.remove((triple[0], triple[1], triple[2], self.locked_context))
        else:
            return self.locked_context.remove((triple[0], triple[1], triple[2]))
    else:
        return self.impl.remove((triple[0], triple[1], triple[2]))
