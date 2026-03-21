#!/usr/bin/env python
"""
Lightweight development runner: watches Python files and restarts `main.py`

Usage:
    python dev_run.py

No external dependencies — uses polling to detect changed file mtimes.
"""
import subprocess
import sys
import time
from pathlib import Path


def find_py_files(root: Path):
    return [p for p in root.rglob("*.py") if p.is_file()]


def mtimes(files):
    d = {}
    for f in files:
        try:
            d[str(f)] = f.stat().st_mtime
        except Exception:
            d[str(f)] = None
    return d


def run():
    root = Path(__file__).resolve().parent
    watched = find_py_files(root)
    last = mtimes(watched)

    print("Starting dev runner — launching main.py")
    proc = subprocess.Popen([sys.executable, "main.py"])  # launch the app

    try:
        while True:
            time.sleep(1.0)
            watched = find_py_files(root)
            current = mtimes(watched)
            if current != last:
                print("Change detected — restarting application...")
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
                proc = subprocess.Popen([sys.executable, "main.py"])
                last = current
    except KeyboardInterrupt:
        print("Stopping dev runner — terminating application")
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    run()
