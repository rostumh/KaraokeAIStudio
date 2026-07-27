from pathlib import Path
import pytest
from app.application.errors import MediaImportError
from app.infrastructure.packaging.windows_package import msix_version,sha256_file
def test_msix_version_has_four_numeric_parts():assert msix_version("0.19.0")=="0.19.0.0"
def test_prerelease_is_rejected():
 with pytest.raises(MediaImportError):msix_version("0.19.0rc1")
def test_sha256_file(tmp_path:Path):
 p=tmp_path/"x";p.write_bytes(b"abc");assert sha256_file(p)=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
