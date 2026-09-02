# Context shim (see meta.json): subset of apysource/namespaces.py and
# apysource/results.py from alganet/apysource@f800ec97c124b31eff8dfc1de8fe2
# f4f1bc7dbda, so the region executes outside its package (`apysource` is on
# PyPI but installing it -- and its own dependency tree -- into the venv
# shared by every concurrent agent, only to pin a version that may not match
# this commit, was judged out of scope; see meta.json). Identical bindings
# for both representations.
#
# SV is the project's own vocabulary namespace, copied verbatim. PROV is
# rdflib's own builtin, re-exported unchanged (apysource/namespaces.py
# imports it from rdflib.namespace, does not redefine it).
#
# CiteSite is the dataclass the region builds and returns, copied verbatim
# (docstring included -- it explains why `line` is optional, which the
# fixture exercises). CheckResult/Failure/FetcherResult/RepoResult are
# imported by the region's home module alongside CiteSite but never touched
# by the region itself; reproduced verbatim (minus TYPE_CHECKING-only
# forward references, harmless under `from __future__ import annotations`)
# only so the import line resolves.
from __future__ import annotations

from dataclasses import dataclass, field

from rdflib import Namespace
from rdflib.namespace import PROV

SV = Namespace("https://alganet.github.io/apysource/vocab.ttl#")


@dataclass
class ResolveResult:
    """Base result -- covers error cases (no_source, no_url, no_module, no_file)."""

    status: str
    label: str = ""
    url: str = ""
    source: str = ""
    anchor: str = ""


@dataclass
class RepoResult(ResolveResult):
    """Resolved via a repository module."""

    location: str = ""
    module: str = ""
    repo: BaseRepo | None = None
    key: str = ""
    cache_file: str | None = None
    format_name: str = ""
    locator: str | None = None


@dataclass
class FetcherResult(ResolveResult):
    """Resolved via HTTP fetcher (no repo needed)."""

    location: str = ""
    module: str = "http"
    fetcher: CachedFetcher | None = None
    format_name: str = ""
    locator: str | None = None
    fallback_from: str = ""
    fallback_reason: str = ""


@dataclass
class CiteSite:
    """Where a citation is made -- the other end of the citation.

    ``line`` is optional: not every citation is made at a line of a file. A
    footnote cites too.
    """

    file: str
    line: int | None = None

    def __str__(self) -> str:
        return f"{self.file}:{self.line}" if self.line is not None else self.file


@dataclass
class Failure:
    """A single verification failure."""

    group: str
    item: str
    reason: str
    hint: Diagnosis | None = None
    url: str = ""
    urn: str = ""
    cited_by: list[CiteSite] = field(default_factory=list)


@dataclass
class CheckResult:
    """Result of a verification check."""

    name: str
    ok: int
    total: int
    failures: list[Failure] = field(default_factory=list)
    warnings: list[Failure] = field(default_factory=list)
    structural: bool = False
