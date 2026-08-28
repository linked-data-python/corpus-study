# Context shim (see meta.json): stand-in for the third-party `pycountry`
# package, which is not installed in the study venv. `original.py` does
# `import pycountry` unmodified; this file sits next to it on sys.path (the
# driver runs with cwd=<region dir>) and is picked up by that same bare
# import, for both representations.
#
# Only the single call the region makes is covered:
#   pycountry.countries.get(alpha_3=<code>)
# returning an object with an `.alpha_2` attribute, or None when the code is
# not a real ISO 3166-1 alpha-3 code. The two entries below are real ISO
# 3166-1 codes (not invented), enough to exercise both branches against the
# `reader` fixture in _context.py.

from collections import namedtuple

_Country = namedtuple("_Country", ["alpha_2", "alpha_3"])

_BY_ALPHA_3 = {
    "MEX": _Country("MX", "MEX"),
    "FRA": _Country("FR", "FRA"),
}


class _Countries:
    def get(self, alpha_3=None, **kwargs):
        if alpha_3 is None:
            return None
        return _BY_ALPHA_3.get(alpha_3)


countries = _Countries()
