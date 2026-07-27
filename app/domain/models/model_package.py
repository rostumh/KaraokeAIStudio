from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ModelFile:
    name: str

@dataclass(frozen=True, slots=True)
class ModelPackage:
    model_id: str
    name: str
    required: bool
    license: str
    revision: str
    install_subdir: str
    base_url: str
    files: tuple[ModelFile, ...]
