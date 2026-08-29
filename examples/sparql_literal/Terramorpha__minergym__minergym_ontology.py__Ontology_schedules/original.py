# Extracted from Terramorpha/minergym@1d2d586bb1 : minergym/ontology.py
# region: Ontology.schedules (lines 107-114, stratum sparql_literal)
# licence of the source repository: see meta.json
from typing import List, TypeAlias, TypeVar
from rdflib.term import Node

    def schedules(self) -> List[Node]:
        q = """# -*- mode: sparql -*-
SELECT ?name
WHERE {
  ?name a "Schedule:Compact" .
}
"""
        return [r.name for r in self.rdf.query(q)]
