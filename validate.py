#!/usr/bin/env python3
"""
Simple validation script to catch syntax/indentation errors before committing.

Usage:
  python3 validate.py

It will attempt to compile key project Python files and report any failures
with clear, clickable paths in many editors/CI systems.
"""
import os
import sys
import py_compile


PROJECT_FILES = [
    "championship_dashboard.py",
    "club_championships_scoreboard.py",
    "swim_event_extractor.py",
    "example_usage.py",
    "update_year.py",
]


def discover_existing(files):
    return [f for f in files if os.path.exists(f)]


def main() -> int:
    to_check = discover_existing(PROJECT_FILES)
    # Include any additional .py files in root (excluding hidden/venv/git)
    for name in os.listdir("."):
        if name.endswith(".py") and name not in to_check and not name.startswith("."):
            to_check.append(name)

    print("Validating Python syntax (py_compile):")
    failures = 0
    for path in to_check:
        try:
            py_compile.compile(path, doraise=True)
            print(f"✓ {path}")
        except py_compile.PyCompileError as e:
            failures += 1
            print(f"✗ {path}\n{e}")

    if failures:
        print(f"\nValidation failed: {failures} file(s) with syntax/indentation errors.")
        return 1

    print("\nAll checked files compiled successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


