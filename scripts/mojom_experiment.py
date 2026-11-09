"""Offline extraction and first source-bound Mojom query experiment."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from repo_proof.experiment import main

if __name__ == "__main__":
    raise SystemExit(main())
