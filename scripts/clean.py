"""Очистка проекта от кэшей и мусорных файлов.

Использование:
    python scripts/clean.py
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

CACHE_DIRS = ("__pycache__",)
CACHE_FILES_SUFFIX = (".pyc", ".pyo")
JUNK_FILES = (
    "runserver.out",
    "runserver.err",
    "runserver.pid",
    "test_output.txt",
)


def main() -> None:
    removed_dirs = 0
    removed_files = 0

    for dirpath, dirnames, filenames in os.walk(ROOT):
        for dirname in list(dirnames):
            if dirname in CACHE_DIRS:
                shutil.rmtree(Path(dirpath) / dirname, ignore_errors=True)
                dirnames.remove(dirname)
                removed_dirs += 1
        for filename in filenames:
            if filename.endswith(CACHE_FILES_SUFFIX):
                try:
                    os.remove(Path(dirpath) / filename)
                    removed_files += 1
                except OSError:
                    pass
            elif filename in JUNK_FILES:
                try:
                    os.remove(Path(dirpath) / filename)
                    removed_files += 1
                except OSError:
                    pass
            elif (filename.startswith("test_") and filename.endswith(".py")) or filename == "test_output.txt":
                try:
                    os.remove(Path(dirpath) / filename)
                    removed_files += 1
                except OSError:
                    pass

    print(f"OK: удалено папок: {removed_dirs}, файлов: {removed_files}")


if __name__ == "__main__":
    main()
