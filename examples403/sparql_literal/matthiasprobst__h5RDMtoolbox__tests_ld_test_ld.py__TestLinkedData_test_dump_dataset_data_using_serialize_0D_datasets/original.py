# Extracted from matthiasprobst/h5RDMtoolbox@1baa9284dc : tests/ld/test_ld.py
# region: TestLinkedData.test_dump_dataset_data_using_serialize_0D_datasets (lines 147-172, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib
from ontolutils.namespacelib import M4I
import h5rdmtoolbox as h5tbx

    def test_dump_dataset_data_using_serialize_0D_datasets(self):
        with h5tbx.File() as h5:
            ds = h5.create_dataset('ds0', data=5.4, attrs={"units": "m/s"})
            ds.rdf.subject = M4I.NumericalVariable
            h5.create_dataset('ds_str0', data="Hello")
            h5.create_string_dataset('ds_str1', data=["Hello", "World"])
            h5.create_dataset('ds1', data=[1, 2, 3])
            h5.create_dataset('ds2', data=[[1, 2], [3, 4]])
            ttl = h5.serialize(fmt="ttl", skipND=1, file_uri="https://example.org#")
        print(ttl)
        g = rdflib.Graph().parse(data=ttl, format="ttl")
        sparql_str = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX hdf: <http://purl.allotrope.org/ontologies/hdf5/1.8#>

SELECT ?values
WHERE {
    ?id a hdf:Dataset .
    ?id hdf:name "/ds1" .
    ?id hdf:value ?values .
}
"""
        res = g.query(sparql_str)
        bindings = res.bindings
        self.assertEqual(0, len(bindings))

        _raise_on_blank_nodes(ttl)
