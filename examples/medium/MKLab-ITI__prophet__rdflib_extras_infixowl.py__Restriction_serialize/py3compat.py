# Context shim (see meta.json): the region is decorated with
# `@py3compat.format_doctest_out`, from rdflib/py3compat.py at
# MKLab-ITI/prophet@eee2ab51de (lines 28-43 and 60-74) -- a Python-2/3
# helper that rdflib dropped long ago, so `from rdflib import py3compat`
# cannot resolve against the installed rdflib.  The two functions below are
# copied verbatim, keeping the Python-3 branch only.
# Imported IDENTICALLY by original.py and translated.ldpy.
from functools import wraps


def _modify_str_or_docstring(str_change_func):
    @wraps(str_change_func)
    def wrapper(func_or_str):
        if isinstance(func_or_str, str):
            func = None
            doc = func_or_str
        else:
            func = func_or_str
            doc = func.__doc__

        doc = str_change_func(doc)

        if func:
            func.__doc__ = doc
            return func
        return doc
    return wrapper


# Abstract u'abc' syntax:
@_modify_str_or_docstring
def format_doctest_out(s):
    """Python 2 version
    "%(u)s'abc'" --> "'abc'"
    "%(b)s'abc'" --> "b'abc'"
    "55%(L)s"    --> "55"
    "unicode(x)" --> "str(x)"

    Accepts a string or a function, so it can be used as a decorator."""
    # s may be None if processed by Py2exe
    if s is None:
        return ''
    return s % {'u': '', 'b': 'b', 'L': '', 'unicode': 'str'}
