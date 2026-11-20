"""Run test_decoder.py against decoder.py and every module in variants/."""

import os
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).parent
targets = ["decoder"] + [
    f"variants.{p.stem}" for p in sorted((root / "variants").glob("v*.py"))
]

failed = []
for target in targets:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_decoder.py"],
        cwd=root,
        env={**os.environ, "DECODER": target, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
    )
    summary = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr
    print(f"{target:32} {summary}")
    if proc.returncode:
        failed.append(target)
        print(proc.stdout)

sys.exit(1 if failed else 0)
