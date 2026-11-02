# Context shim (see meta.json): CSV2RDF, column and csv_reader, which main()
# takes from the module it was extracted from (lib/rdflib/tools/csv2rdf.py of
# schemaorg/sdopythonapp@128be97d35, a vendored rdflib 4.x).
#
# That file is Python 2 code (`csvreader.next()`, `text_type(cell, 'utf-8')`,
# `str.encode(...).replace(" ", "_")`): its CSV2RDF.convert() fails on its
# first line under Python 3, so it would never reach the point where the
# Namespaces main() builds are used. The installed rdflib (7.2.1) ships the
# same tool, same class and attributes (BASE, PROPBASE, CLASS, IDENT, LABEL,
# DEFINECLASS, SKIP, DELIM, DEFAULT, COLUMNS, PROPS, OUT), ported to
# Python 3: its classes are used, unmodified.
# Identical bindings for both representations.
from rdflib.tools.csv2rdf import CSV2RDF, column, csv_reader  # noqa: F401
