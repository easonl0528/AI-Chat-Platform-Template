"""Helper script to generate a Windows EXE with PyInstaller.

Usage (on Windows):
    python -m installer.build_exe
Optionally pass a custom output directory:
    python -m installer.build_exe --dist-path dist
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC_PATH = HERE / "geo_optimizer.spec"


def run_pyinstaller(dist_path: Path | None = None) -> None:
    command = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--specpath",
        str(HERE),
        str(SPEC_PATH),
    ]
    if dist_path:
        command.extend(["--distpath", str(dist_path)])

    print("Running:", " ".join(command))
    subprocess.check_call(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build EXE for the GEO optimizer")
    parser.add_argument("--dist-path", type=Path, default=None, help="Override dist output directory")
    args = parser.parse_args()

    run_pyinstaller(args.dist_path)
