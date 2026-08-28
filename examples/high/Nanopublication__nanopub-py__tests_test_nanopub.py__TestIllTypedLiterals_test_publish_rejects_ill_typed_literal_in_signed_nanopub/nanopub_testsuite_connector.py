# Offline context shim (see meta.json) standing in for the
# nanopub-testsuite-connector package (v1.0.0).  The real
# NanopubTestSuite.get_latest() downloads
# https://github.com/Nanopublication/nanopub-testsuite/archive/main.tar.gz,
# so it cannot be used in an offline, reproducible evaluation.  This
# stand-in keeps the API the region uses and indexes the handful of files
# vendored next to it in ./testsuite/ (from the nanopub-testsuite
# repository, MIT, Copyright (c) 2022 Tobias Kuhn - see testsuite/LICENSE).
# TestSuiteSubfolder, TestSuiteEntry and SigningKeyPair are verbatim from
# nanopub_testsuite_connector/models.py; the indexing follows
# connector.py's _index_entries / _nanopub_uri_from_nanopub.
# Used IDENTICALLY by original.py and translated.ldpy.
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from rdflib import RDF, Dataset, URIRef

_HERE = Path(__file__).resolve().parent / "testsuite"
_NANOPUB_TYPE = URIRef("http://www.nanopub.org/nschema#Nanopublication")


class TestSuiteSubfolder(str, Enum):
    """Subfolder categories within valid/invalid test entries."""
    __test__ = False

    PLAIN = "plain"
    SIGNED = "signed"
    TRUSTY = "trusty"


@dataclass(frozen=True)
class TestSuiteEntry:
    """Represents a single nanopublication test file in the test suite."""
    __test__ = False

    name: str
    path: Path
    subfolder: TestSuiteSubfolder
    valid: bool

    def read_text(self, encoding: str = "utf-8") -> str:
        return self.path.read_text(encoding=encoding)

    def read_bytes(self) -> bytes:
        return self.path.read_bytes()


@dataclass(frozen=True)
class SigningKeyPair:
    """Paths to a private/public RSA key pair."""

    name: str
    private_key: Path
    public_key: Path


def _nanopub_uri_from_nanopub(path: Path) -> str | None:
    try:
        ds = Dataset()
        ds.parse(path, format="trig")
        for subject, _, _, _ in ds.quads((None, RDF.type, _NANOPUB_TYPE, None)):
            if isinstance(subject, URIRef):
                return str(subject)
    except Exception:
        pass
    return None


class NanopubTestSuite:
    """Accessor over the vendored subset of the Nanopublication Test Suite."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._valid: list[TestSuiteEntry] = []
        valid_dir = root / "valid"
        for sub_path in (sorted(valid_dir.iterdir())
                         if valid_dir.exists() else []):
            if not sub_path.is_dir():
                continue
            try:
                sf = TestSuiteSubfolder(sub_path.name)
            except ValueError:
                continue
            for file_path in sorted(sub_path.glob("*.trig")):
                self._valid.append(TestSuiteEntry(
                    name=file_path.name, path=file_path,
                    subfolder=sf, valid=True))
        self._by_nanopub_uri: dict[str, TestSuiteEntry] = {}
        for entry in self._valid:
            uri = _nanopub_uri_from_nanopub(entry.path)
            if uri:
                self._by_nanopub_uri[uri] = entry
        self._signing_keys: dict[str, SigningKeyPair] = {}
        signed_dir = root / "transform" / "signed"
        if signed_dir.exists():
            for key_dir in sorted(signed_dir.iterdir()):
                priv = key_dir / "key" / "id_rsa"
                pub = key_dir / "key" / "id_rsa.pub"
                if priv.exists() and pub.exists():
                    self._signing_keys[key_dir.name] = SigningKeyPair(
                        name=key_dir.name, private_key=priv, public_key=pub)

    @classmethod
    def get_local(cls) -> "NanopubTestSuite":
        """Offline replacement for the connector's get_latest()."""
        return cls(_HERE)

    @property
    def root(self) -> Path:
        return self._root

    def get_valid(self, subfolder: TestSuiteSubfolder | None = None) \
            -> list[TestSuiteEntry]:
        if subfolder is None:
            return list(self._valid)
        return [e for e in self._valid if e.subfolder == subfolder]

    def get_by_nanopub_uri(self, uri: str) -> TestSuiteEntry:
        try:
            return self._by_nanopub_uri[uri]
        except KeyError:
            raise KeyError(f"No entry found for nanopub URI {uri!r}") from None

    def get_signing_key(self, key_name: str) -> SigningKeyPair:
        try:
            return self._signing_keys[key_name]
        except KeyError:
            available = ", ".join(sorted(self._signing_keys))
            raise KeyError(
                f"Signing key {key_name!r} not found. Available: {available}"
            ) from None
