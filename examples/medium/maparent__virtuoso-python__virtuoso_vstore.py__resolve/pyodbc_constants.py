# Context shim (see meta.json): the Virtuoso data-value type codes that the
# region reads off the `pyodbc` module.  virtuoso-python does not use the
# stock pyodbc: it ships pyodbc-2.1.12.patch, which exports Virtuoso's DV_*
# and DT_* codes as module constants.  The values below are transcribed from
# that patch (maparent/virtuoso-python@eba377e1fa, pyodbc-2.1.12.patch), so
# no patched ODBC driver is needed to exercise the region's dispatch.
# Imported identically by original.py and translated.ldpy as `pyodbc`.

# box types (DV_*)
VIRTUOSO_DV_STRING = 182
VIRTUOSO_DV_LONG_INT = 189
VIRTUOSO_DV_SINGLE_FLOAT = 190
VIRTUOSO_DV_DOUBLE_FLOAT = 191
VIRTUOSO_DV_DB_NULL = 204
VIRTUOSO_DV_NUMERIC = 219
VIRTUOSO_DV_WIDE = 225
VIRTUOSO_DV_BLOB_WIDE_HANDLE = 133
VIRTUOSO_DV_DATE = 129
VIRTUOSO_DV_TIME = 210
VIRTUOSO_DV_DATETIME = 211
VIRTUOSO_DV_TIMESTAMP = 128
VIRTUOSO_DV_IRI_ID = 243
VIRTUOSO_DV_RDF = 246

# date/time sub-types (DT_TYPE_*)
VIRTUOSO_DT_TYPE_DATETIME = 1
VIRTUOSO_DT_TYPE_DATE = 2
VIRTUOSO_DT_TYPE_TIME = 3
