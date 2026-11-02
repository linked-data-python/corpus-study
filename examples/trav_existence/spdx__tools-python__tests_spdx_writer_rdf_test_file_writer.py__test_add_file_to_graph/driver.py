"""Validation driver for spdx__tools-python__tests_spdx_writer_rdf_test_file_writer.py__test_add_file_to_graph.

The region is a test: it builds a graph with `add_file_to_graph(file_fixture())`
and asserts fourteen things about it. It takes no argument and returns None,
so a green call proves nothing by itself; what the original SHOWS is whether it
raises. The only thing that can make it raise is the file the fixture builds,
so the driver changes that file: before each call it replaces the defaults of
`spdx_shim.file_fixture` (the function object the region imported; the same
for both representations) with the defaults of the case. The first case is the
fixture as the repository has it and passes; each of the others takes away or
alters one thing, so that one assertion (or two) fails, and a translation that
checks something else, or less, passes where the original raises.

The asserts carry no message: a failing call raises a bare AssertionError, and
which assertion fired is not told apart, only whether the call passes. The two
`IndexError`s are raised by `file.contributors[0]` and
`file.attribution_texts[0]` evaluated inside the assertion, on an empty list.

  default              the fixture: passes.
  other_id             spdx_id "SPDXRef-Other": the subject is not
                       docNamespace#SPDXRef-File (first assertion).
  invalid_id           spdx_id "SPDXRef_invalid": left as is by the writer, so not
                       docNamespace#SPDXRef-File either.
  no_file_type         file_types=[]: no spdx:fileType.
  other_file_type      file_types=[SOURCE]: a spdx:fileType exists, with
                       another object (fileType_source, not fileType_text).
  no_license_comment   license_comment=None: nothing written, and the assertion
                       looks for Literal(None) = "None".
  no_concluded         license_concluded=None: no spdx:licenseConcluded.
  no_mit               license_info_in_file without MIT.
  no_gpl               ... without GPL-2.0-only.
  no_noassertion       ... without NOASSERTION.
  other_license        ... MIT, GPL, NOASSERTION and Apache-2.0 besides: the
                       extra licence does not matter -> passes.
  no_copyright         copyright_text=None.
  no_comment           comment=None.
  no_notice            notice=None.
  same_texts           the comment and the notice carry the text the copyright
                       one has in the default: each assertion looks at its own
                       predicate -> passes.
  no_contributor       contributors=[]: IndexError.
  no_attribution       attribution_texts=[]: IndexError.
  no_checksum          checksums=[]: no spdx:checksum.
"""
import inspect

from rdfeval.harness import run_pair
import spdx_shim

_PARAMS = list(inspect.signature(spdx_shim.file_fixture).parameters)
_DEFAULTS = spdx_shim.file_fixture.__defaults__
MIT = spdx_shim.LicenseSymbol("MIT")
GPL = spdx_shim.LicenseSymbol("GPL-2.0-only")
APACHE = spdx_shim.LicenseSymbol("Apache-2.0")
NOASSERTION = spdx_shim.SpdxNoAssertion()


def _case(**changes):
    def make():
        spdx_shim.file_fixture.__defaults__ = tuple(
            changes.get(name, default) for name, default in zip(_PARAMS, _DEFAULTS))
        return (), {}
    return make


CALLS = [
    _case(),                                                           # default
    _case(spdx_id="SPDXRef-Other"),                                    # other_id
    _case(spdx_id="SPDXRef_invalid"),                                        # invalid_id
    _case(file_types=[]),                                              # no_file_type
    _case(file_types=[spdx_shim.FileType.SOURCE]),                     # other_file_type
    _case(license_comment=None),                                       # no_license_comment
    _case(license_concluded=None),                                     # no_concluded
    _case(license_info_in_file=[GPL, NOASSERTION]),                    # no_mit
    _case(license_info_in_file=[MIT, NOASSERTION]),                    # no_gpl
    _case(license_info_in_file=[MIT, GPL]),                            # no_noassertion
    _case(license_info_in_file=[MIT, GPL, NOASSERTION, APACHE]),       # other_license
    _case(copyright_text=None),                                        # no_copyright
    _case(comment=None),                                               # no_comment
    _case(notice=None),                                                # no_notice
    _case(comment="copyrightText", notice="copyrightText"),            # same_texts
    _case(contributors=[]),                                            # no_contributor
    _case(attribution_texts=[]),                                       # no_attribution
    _case(checksums=[]),                                               # no_checksum
]

VERDICT = run_pair(
    __file__,
    entry='test_add_file_to_graph',
    calls=CALLS,
)
