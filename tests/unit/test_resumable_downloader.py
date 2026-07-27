from io import BytesIO
from pathlib import Path
from threading import Event
from urllib.error import HTTPError
import hashlib

import app.infrastructure.models.resumable_downloader as module
from app.infrastructure.models.resumable_downloader import RemoteFileMetadata, ResumableModelDownloader

class Response:
    def __init__(self, data: bytes, status: int = 200):
        self.stream = BytesIO(data); self.status = status
    def read(self, n: int) -> bytes: return self.stream.read(n)
    def getcode(self) -> int: return self.status
    def __enter__(self): return self
    def __exit__(self, *args): return False

def test_sha256(tmp_path: Path):
    path=tmp_path/'x'; path.write_bytes(b'abc')
    assert ResumableModelDownloader.sha256(path)=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'

def test_git_blob_sha1_for_git_managed_model_file(tmp_path: Path):
    path=tmp_path/'x'; path.write_bytes(b'abc')
    assert ResumableModelDownloader.digest_file(path,'git-sha1')=='f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f'

def test_verified_marker_supports_offline_reuse(tmp_path: Path):
    path=tmp_path/'model.bin'; path.write_bytes(b'abc')
    metadata=RemoteFileMetadata('sha256',ResumableModelDownloader.sha256(path),3)
    ResumableModelDownloader._write_marker(path,metadata)
    assert ResumableModelDownloader().verify('https://invalid.example/not-contacted',path)

def test_complete_partial_is_verified_without_range_request(tmp_path: Path,monkeypatch):
    data=b'abcdef'; destination=tmp_path/'model.bin'; destination.with_name('model.bin.part').write_bytes(data)
    metadata=RemoteFileMetadata('sha256',hashlib.sha256(data).hexdigest(),len(data))
    monkeypatch.setattr(ResumableModelDownloader,'_metadata',staticmethod(lambda url:metadata))
    monkeypatch.setattr(module,'urlopen',lambda *a,**k:(_ for _ in ()).throw(AssertionError('network GET not expected')))
    ResumableModelDownloader().download('https://example.test/model.bin',destination,lambda *x:None,Event())
    assert destination.read_bytes()==data

def test_http_416_discards_stale_partial_and_retries_clean_get(tmp_path: Path,monkeypatch):
    data=b'abcdef'; destination=tmp_path/'model.bin'; destination.with_name('model.bin.part').write_bytes(b'abc')
    metadata=RemoteFileMetadata('sha256',hashlib.sha256(data).hexdigest(),len(data))
    monkeypatch.setattr(ResumableModelDownloader,'_metadata',staticmethod(lambda url:metadata)); calls=[]
    def fake_urlopen(request,timeout):
        calls.append(request.headers.get('Range'))
        if len(calls)==1: raise HTTPError(request.full_url,416,'Range Not Satisfiable',{'Content-Range':'bytes */6'},None)
        return Response(data,200)
    monkeypatch.setattr(module,'urlopen',fake_urlopen)
    ResumableModelDownloader().download('https://example.test/model.bin',destination,lambda *x:None,Event())
    assert calls==['bytes=3-',None] and destination.read_bytes()==data

def test_server_ignores_range_full_response_replaces_partial(tmp_path: Path,monkeypatch):
    data=b'abcdef'; destination=tmp_path/'model.bin'; destination.with_name('model.bin.part').write_bytes(b'abc')
    metadata=RemoteFileMetadata('sha256',hashlib.sha256(data).hexdigest(),len(data))
    monkeypatch.setattr(ResumableModelDownloader,'_metadata',staticmethod(lambda url:metadata))
    monkeypatch.setattr(module,'urlopen',lambda request,timeout:Response(data,200))
    ResumableModelDownloader().download('https://example.test/model.bin',destination,lambda *x:None,Event())
    assert destination.read_bytes()==data

def test_official_hf_metadata_location_and_lfs_sha256(monkeypatch):
    class Metadata:
        etag = "a" * 64
        size = 123
        location = "https://cdn.example.test/signed-model"
    monkeypatch.setattr(module, "get_hf_file_metadata", lambda url, timeout: Metadata())
    result = ResumableModelDownloader._metadata("https://huggingface.co/repo/resolve/rev/model.bin")
    assert result.algorithm == "sha256"
    assert result.digest == "a" * 64
    assert result.size == 123
    assert result.location == "https://cdn.example.test/signed-model"
