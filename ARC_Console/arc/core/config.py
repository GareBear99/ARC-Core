"""Configuration surface for ARC-Core.

All tunable settings live here. Values come from either compile-time constants
(e.g. ``APP_NAME``, ``APP_VERSION``) or environment variables with safe demo
defaults. Every cap is env-overridable so ARC-Core can ride on everything from
a 2012 Intel MacBook (Catalina) up to a modern server, without code changes.

See ``docs/ARCHITECTURE.md`` §3 for a complete rundown of every constant and
env var, including security-sensitive defaults that must be changed before
production deploy. See ``docs/HARDWARE_FLOOR.md`` for the low-resource
deployment playbook.

Low-resource mode
-----------------
Set ``ARC_LOW_RESOURCE_MODE=1`` to activate a preset optimized for a 2012-era
Intel laptop (2-4 cores, 4-8 GB RAM, HDD-or-SSD, macOS Catalina or Linux of
similar vintage). The preset tightens query caps, heatmap grid size, receipt
verification span, and session TTL so a single ARC-Core process stays well
below 256 MB RSS under normal analyst load.

Individual caps can also be set explicitly via their own env vars; explicit
env vars always win over the preset.
"""
from __future__ import annotations
import os
from pathlib import Path

APP_NAME = "ARC-Core"
APP_VERSION = "6.0.0"


def _env_int(name: str, default: int) -> int:
    """Read an integer env var, falling back to ``default`` on unset/empty/invalid."""
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


#: When set to a truthy value, ARC-Core tightens every query/resource cap to
#: the low-resource preset documented in ``docs/HARDWARE_FLOOR.md``.
LOW_RESOURCE_MODE = os.getenv("ARC_LOW_RESOURCE_MODE", "0").strip() not in ("", "0", "false", "False", "no", "off")

DEMO_MODE = os.getenv("ARC_DEMO_MODE", "1") != "0"
SHARED_TOKEN = os.getenv("ARC_SHARED_TOKEN", "").strip()

# Low-resource preset vs. default. Explicit env vars override the preset.
_DEFAULT_LIMIT_PRESET = 50 if LOW_RESOURCE_MODE else 100
_MAX_LIMIT_PRESET = 200 if LOW_RESOURCE_MODE else 500
_MAX_GRID_SIZE_PRESET = 16 if LOW_RESOURCE_MODE else 64
_RECEIPT_VERIFY_MAX_PRESET = 1000 if LOW_RESOURCE_MODE else 5000
_SESSION_TTL_HOURS_PRESET = 4 if LOW_RESOURCE_MODE else 12
_NOTEBOOK_EXPORT_LIMIT_PRESET = 100 if LOW_RESOURCE_MODE else 250

DEFAULT_LIMIT = _env_int("ARC_DEFAULT_LIMIT", _DEFAULT_LIMIT_PRESET)
MAX_LIMIT = _env_int("ARC_MAX_LIMIT", _MAX_LIMIT_PRESET)
MAX_GRID_SIZE = _env_int("ARC_MAX_GRID_SIZE", _MAX_GRID_SIZE_PRESET)
RECEIPT_VERIFY_MAX = _env_int("ARC_RECEIPT_VERIFY_MAX", _RECEIPT_VERIFY_MAX_PRESET)
SESSION_TTL_HOURS = _env_int("ARC_SESSION_TTL_HOURS", _SESSION_TTL_HOURS_PRESET)
NOTEBOOK_EXPORT_LIMIT = _env_int("ARC_NOTEBOOK_EXPORT_LIMIT", _NOTEBOOK_EXPORT_LIMIT_PRESET)

#: Optional soft disk-footprint advisory. When set (non-zero MB), operators
#: can query the effective cap via ``/api/manifest`` for their own monitoring
#: scripts; ARC-Core does not enforce it — SQLite will keep accepting writes
#: past the cap. Use it as a trigger for archival to Arc-RAR bundles.
MAX_DB_SIZE_MB = _env_int("ARC_MAX_DB_SIZE_MB", 0)

AUTH_BOOTSTRAP_PASSWORD = os.getenv("ARC_BOOTSTRAP_PASSWORD", "arc-demo-admin")
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
KEY_DIR = DATA_DIR / "keys"
CONNECTOR_INBOX_DIR = DATA_DIR / "connectors"
