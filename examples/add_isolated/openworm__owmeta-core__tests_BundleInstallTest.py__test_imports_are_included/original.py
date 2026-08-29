# Extracted from openworm/owmeta-core@cd69d77ad0 : tests/BundleInstallTest.py
# region: test_imports_are_included (lines 217-245, stratum add_isolated)
# licence of the source repository: see meta.json
import transaction
import rdflib
from rdflib.term import URIRef
from owmeta_core.bundle import (Installer, Descriptor, make_include_func, FilesDescriptor,
                                UncoveredImports, DependencyDescriptor, TargetIsNotEmpty,
                                Remote, Bundle, BUNDLE_MANIFEST_FILE_NAME)
from owmeta_core.context import IMPORTS_CONTEXT_KEY
from owmeta_core.context_common import CONTEXT_IMPORTS

def test_imports_are_included(dirs):
    '''
    If we have imports and no dependencies, then thrown an exception if we have not
    included them in the bundle
    '''
    imports_ctxid = 'http://example.org/imports'
    ctxid_1 = 'http://example.org/ctx1'
    ctxid_2 = 'http://example.org/ctx2'

    # Make a descriptor that includes ctx1 and the imports, but not ctx2
    d = Descriptor('test')
    d.includes.add(make_include_func(ctxid_1))
    d.includes.add(make_include_func(ctxid_2))

    # Add some triples so the contexts aren't empty -- we can't save an empty context
    g = rdflib.ConjunctiveGraph()
    cg_1 = g.get_context(ctxid_1)
    cg_2 = g.get_context(ctxid_2)
    cg_imp = g.get_context(imports_ctxid)
    with transaction.manager:
        cg_1.add((aURI('a'), aURI('b'), aURI('c')))
        cg_2.add((aURI('d'), aURI('e'), aURI('f')))
        cg_imp.add((URIRef(ctxid_1), CONTEXT_IMPORTS, URIRef(ctxid_2)))

    bi = Installer(*dirs, imports_ctx=imports_ctxid, graph=g)
    bi.install(d)
    with Bundle(d.id, dirs.bundles_directory) as bnd:
        g = bnd.rdf.get_context(bnd.conf[IMPORTS_CONTEXT_KEY])
        assert (URIRef(ctxid_1), CONTEXT_IMPORTS, URIRef(ctxid_2)) in g
