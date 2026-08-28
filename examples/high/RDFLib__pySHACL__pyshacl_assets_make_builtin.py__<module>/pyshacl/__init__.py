# Context shim (see meta.json): pySHACL is not installed in the evaluation
# environment, and the region only needs `pyshacl.monkey.apply_patches`.  This
# package stub exists so that `from pyshacl.monkey import apply_patches` in
# original.py and translated.ldpy resolves unchanged -- no import line had to
# be edited on either side.  pyshacl/monkey/__init__.py next to it is a
# verbatim copy of RDFLib/pySHACL@469cca7a22 (Apache-2.0), whose only
# dependencies are rdflib and packaging.
