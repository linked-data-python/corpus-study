# Context shim (see meta.json): a stand-in for tests/ingest_tester.py
# (tetherless-world/materialsmine), imported by the region via
# `from . import ingest_tester`. The real
# test_dielectric_real_permittivity(runner, ...) queries a live triple store
# through `runner.app.db.query(...)` and asserts against it with
# `runner.assertCountEqual(...)` -- there is no app/store to stand up for a
# pilot. This shim only needs to make what the region PASSES to it
# observable: it prints a canonical, term-by-term (value, datatype) view of
# frequency, real_permittivity and descriptions, so driver.py can compare the
# coercion this region performs by diffing stdout between original.py and
# translated.ldpy.
import types


def _test_dielectric_real_permittivity(runner, frequency, real_permittivity, descriptions):
    print("frequency:", [(str(f), str(f.datatype)) for f in frequency])
    print("real_permittivity:", [(str(p), str(p.datatype)) for p in real_permittivity])
    print("descriptions:", {k: (str(v), str(v.datatype)) for k, v in descriptions.items()})


ingest_tester = types.SimpleNamespace(
    test_dielectric_real_permittivity=_test_dielectric_real_permittivity)
