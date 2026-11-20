from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Dict


class PbitPackage:
    """Read and write a PBIT without embedding a report-specific filename."""

    def __init__(self, path: Path, files: Dict[str, bytes]) -> None:
        self.path = Path(path)
        self.files = files

    @classmethod
    def open(cls, path: str | Path) -> "PbitPackage":
        source = Path(path)
        with zipfile.ZipFile(source, "r") as archive:
            return cls(source, {name: archive.read(name) for name in archive.namelist()})

    @property
    def sha256(self) -> str:
        digest = hashlib.sha256()
        with self.path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def has(self, name: str) -> bool:
        return name in self.files

    def json(self, name: str, encoding: str = "utf-16") -> dict:
        return json.loads(self.files[name].decode(encoding))

    def write(self, destination: str | Path) -> Path:
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in self.files.items():
                archive.writestr(name, data)
        return target
