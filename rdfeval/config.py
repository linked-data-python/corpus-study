"""Configuration loading and provenance stamping."""

from __future__ import annotations

import datetime
import subprocess
import tomllib
from pathlib import Path

# Repository root = the evaluation folder (parent of the package).
ROOT = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT / "config" / "evaluation.toml"
MANIFEST_DIR = ROOT / "manifest"
RESULTS_RAW = ROOT / "results" / "raw"
RESULTS_SUMMARY = ROOT / "results" / "summary"
EXAMPLES_DIR = ROOT / "examples"
# The 403 study's own example tree: a different question, a different
# oracle, and aggregates that must never mix with the 401 study's.
EXAMPLES_403_DIR = ROOT / "examples403"


def load_config(path: Path | None = None) -> dict:
    with open(path or CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def provenance(config: dict) -> dict:
    """Stamp attached to every generated result file."""
    try:
        code_rev = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        code_rev = "unknown"
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pipeline_revision": code_rev,
        "config_version": config["meta"]["config_version"],
        "metrics_version": config["meta"]["metrics_version"],
    }
