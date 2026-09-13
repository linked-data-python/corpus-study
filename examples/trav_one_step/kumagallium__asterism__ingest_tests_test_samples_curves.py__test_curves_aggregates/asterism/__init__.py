# Context shim (see meta.json): extends this package's search path to the
# real `asterism.starrydata` package checked out at
# corpus/repos/kumagallium__asterism/ingest/src/asterism (kumagallium/asterism
# @f0977d4d3a), so `from asterism.starrydata import ...` in original.py and
# translated.ldpy resolves to the genuine ingester unmodified. No logic is
# reproduced here: this package is only a path redirector, identical for
# both representations.
import pathlib

_REAL_ASTERISM = (
    pathlib.Path(__file__).resolve().parents[4]
    / "corpus" / "repos" / "kumagallium__asterism" / "ingest" / "src" / "asterism"
)
__path__.append(str(_REAL_ASTERISM))
