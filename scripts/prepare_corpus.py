"""Pinned, resumable Chromium metadata + selected original Git blobs (no checkout)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from repo_proof.corpus import main

if __name__ == "__main__":
    raise SystemExit(main())
