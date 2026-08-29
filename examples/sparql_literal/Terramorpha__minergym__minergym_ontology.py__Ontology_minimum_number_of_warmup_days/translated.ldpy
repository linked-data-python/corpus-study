# Extracted from Terramorpha/minergym@1d2d586bb1 : minergym/ontology.py
# region: Ontology.minimum_number_of_warmup_days (lines 220-239, stratum sparql_literal)
# licence of the source repository: see meta.json
    def minimum_number_of_warmup_days(self) -> int:
        """Look for the `Building` section and return its
        `minimum_number_of_warmup_days` attribute.

        Useful to correctly set the `warmup_phases` parameter of the simulator.

        """

        q = """# -*- mode: sparql -*-
SELECT ?warmupDays
WHERE {
  ?building a "Building" .
  ?building idf:minimum_number_of_warmup_days ?warmupDays .
}"""

        for r in self.rdf.query(q):
            n = r.warmupDays.toPython()
            assert isinstance(n, int)
            return n
        raise Exception("Could not find anything.")
