# Extracted from DerwenAI/kglab@68466f3792 : kglab/gpviz.py
# region: GPViz.__init__ (lines 65-88, stratum bind_initbindings)
# licence of the source repository: see meta.json
import collections
import copy
import typing
import rdflib.paths  # type: ignore # pylint: disable=E0401
import rdflib.plugins.sparql  # type: ignore # pylint: disable=E0401
import rdflib.term  # type: ignore # pylint: disable=E0401

    def __init__ (
        self,
        sparql: str,
        namespaces: typing.Dict[str, str],
        ) -> None:
        """
Constructor for GPViz, to visualize the given SPARQL query as a [`pyvis.network.Network`](https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network)

    sparql:
input SPARQL query to be visualized

    namespaces:
the namespaces for the corresponding RDF graph
        """
        self.namespaces: typing.Dict[str, str] = copy.deepcopy(namespaces)
        pq = rdflib.plugins.sparql.prepareQuery(sparql, initNs=self.namespaces)

        for prefix, uri in pq.prologue.namespace_manager.namespaces():
            if prefix not in self.namespaces:
                self.namespaces[prefix] = str(uri)

        self.blank_nodes: typing.List[str] = []
        self.values: typing.Dict[str, list] = collections.defaultdict(list)
        self.triples: list = self._find_triples(pq.algebra)
