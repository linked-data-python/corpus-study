# Extracted from matthiasprobst/h5RDMtoolbox@1baa9284dc : tests/ld/test_ld.py
# region: TestLinkedData.test_rdf_mappings_callable_none_does_not_abort (lines 1222-1258, stratum sparql_literal)
# licence of the source repository: see meta.json
import pathlib
import rdflib
import ssnolib
from ontolutils.namespacelib import M4I
import h5rdmtoolbox as h5tbx

    def test_rdf_mappings_callable_none_does_not_abort(self):
        filename = pathlib.Path("rdf_mapping_none.hdf")
        with h5tbx.File(filename, mode="w") as h5:
            ds = h5.create_dataset("u", data=[1, 2, 3])
            ds.attrs["units"] = "m/s"
            ds.attrs["standard_name"] = "x_velocity"

        rdf_mappings = {
            "units": {
                "predicate": M4I.hasUnit,
                "object": lambda *_: None,
            },
            "standard_name": {
                "predicate": ssnolib.SSNO.hasStandardName,
                "object": lambda value, _: f"https://example.org/standard-name/{value}",
            },
        }
        ttl = h5tbx.serialize(
            filename,
            fmt="ttl",
            rdf_mappings=rdf_mappings,
            file_uri="https://example.org#",
        )
        graph = rdflib.Graph().parse(data=ttl, format="ttl")
        has_standard_name = graph.query(
            """PREFIX ssno: <https://matthiasprobst.github.io/ssno#>
SELECT ?o WHERE {
    ?s ssno:hasStandardName ?o .
}"""
        )
        self.assertEqual(len(has_standard_name.bindings), 1)
        self.assertEqual(
            str(has_standard_name.bindings[0][rdflib.Variable("o")]),
            "https://example.org/standard-name/x_velocity",
        )
        self.assertNotIn("None", ttl)
        filename.unlink(missing_ok=True)
