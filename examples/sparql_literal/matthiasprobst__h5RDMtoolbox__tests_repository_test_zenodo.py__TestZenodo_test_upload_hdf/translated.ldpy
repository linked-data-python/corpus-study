# Extracted from matthiasprobst/h5RDMtoolbox@1baa9284dc : tests/repository/test_zenodo.py
# region: TestZenodo.test_upload_hdf (lines 405-461, stratum sparql_literal)
# licence of the source repository: see meta.json
import pathlib
import unittest
import rdflib
import h5rdmtoolbox as h5tbx
from h5rdmtoolbox.repository import zenodo
TESTING_VERSIONS = (14,)

    @unittest.skipUnless(get_python_version()[1] in TESTING_VERSIONS,
                         reason=f"Nur auf Python {TESTING_VERSIONS} testen")
    def test_upload_hdf(self):
        z = zenodo.ZenodoRecord(None, sandbox=True)

        with h5tbx.File() as h5:
            h5.attrs['long_name'] = 'root'
            h5.create_dataset('test', data=1, attrs={'units': 'm/s', 'long_name': 'dataset 1'})
            h5.create_dataset('grp1/test2', data=2, attrs={'test': 1, 'long_name': 'dataset 2'})

            orig_hdf_filename = h5.hdf_filename

        hdf_file_name = orig_hdf_filename.name
        json_name = hdf_file_name.replace('.hdf', '.jsonld')

        z.upload_file(orig_hdf_filename)  # metamapper per default converts to JSONLD file
        filenames = list(z.files.keys())
        self.assertIn(hdf_file_name, filenames)
        self.assertIn(json_name, filenames)

        self.assertEqual(z.files.get('invalid.hdf'), None)

        hdf_filenames = [f for f in z.files.keys() if pathlib.Path(f).suffix == '.hdf']
        self.assertEqual(len(hdf_filenames), 1)

        hdf_filename = z.files.get(hdf_file_name).download()

        self.assertTrue(hdf_filename.exists())

        with h5tbx.File(hdf_filename) as h5:
            self.assertEqual(h5.attrs['long_name'], 'root')
            self.assertEqual(h5['test'].attrs['units'], 'm/s')
            self.assertEqual(h5['test'].attrs['long_name'], 'dataset 1')
            self.assertEqual(h5['grp1/test2'].attrs['test'], 1)
            self.assertEqual(h5['grp1/test2'].attrs['long_name'], 'dataset 2')

        self.assertEqual(z.files.get(json_name).suffix, '.jsonld')
        json_filename = z.files.get(json_name).download()
        self.assertTrue(json_filename.exists())

        graph = rdflib.Graph().parse(source=json_filename, format='json-ld')
        query = """
        PREFIX schema: <http://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX hdf: <http://purl.allotrope.org/ontologies/hdf5/1.8#>

        SELECT ?name
        WHERE {
            ?s rdf:type hdf:Group .
            ?s hdf:name ?name .
}"""
        res = graph.query(query)
        group_names = [str(row[rdflib.Variable("name")]) for row in res.bindings]
        self.assertEqual(
            sorted(["/", "/grp1"]),
            sorted(group_names)
        )
