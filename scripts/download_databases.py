"""
Download database files from external URLs (e.g., Google Drive) during build.

Set COMPACT_DATABASE_URL / DATABASE_URL env vars to download the files.
Defaults to the provided Google Drive link for the compact DB.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).resolve().parents[1]
COMPACT_DB = ROOT / "comprehensive_drug_database_compact.json"
FULL_DB = ROOT / "comprehensive_drug_database.json"

# Default compact DB URL provided by user
DEFAULT_COMPACT_URL = "https://drive.google.com/file/d/12o_cdObA01lxXJMY8LjCqlPVrXF56bZF/view?usp=drive_link"


def extract_drive_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID from various URL formats."""
    patterns = [
        r"https://drive\.google\.com/file/d/([^/]+)/",
        r"id=([^&]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def build_drive_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def download_file(url: str, target: Path) -> bool:
    """Download a file, handling Google Drive confirmation tokens if needed."""
    try:
        session = requests.Session()

        file_id = extract_drive_file_id(url)
        download_url = build_drive_download_url(file_id) if file_id else url

        response = session.get(download_url, stream=True)
        token = None
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                token = value
                break

        if token:
            params = {"confirm": token}
            response = session.get(download_url, params=params, stream=True)

        response.raise_for_status()

        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            for chunk in response.iter_content(32 * 1024):
                if chunk:
                    f.write(chunk)

        size_mb = target.stat().st_size / (1024 ** 2)
        print(f"✓ Downloaded {target.name} ({size_mb:.1f} MB)")
        return True
    except Exception as exc:
        print(f"✗ Failed to download {url} -> {target}: {exc}")
        return False


def ensure_file(target: Path, url: Optional[str]) -> None:
    if target.exists():
        print(f"✓ {target.name} already present ({target.stat().st_size / (1024 ** 2):.1f} MB)")
        return
    if not url:
        print(f"⚠️  No URL provided for {target.name}; skipping download.")
        return
    download_file(url, target)


def main() -> None:
    compact_url = os.getenv("COMPACT_DATABASE_URL", DEFAULT_COMPACT_URL)
    full_url = os.getenv("DATABASE_URL")

    ensure_file(COMPACT_DB, compact_url)
    ensure_file(FULL_DB, full_url)

    if not COMPACT_DB.exists() and not FULL_DB.exists():
        print("⚠️  No database files available. The app will show an error at runtime.")


if __name__ == "__main__":
    main()