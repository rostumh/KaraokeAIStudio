import pytest
from app.application.errors import MediaImportError
from app.domain.models.update import *
from app.infrastructure.update.https_update_client import HttpsUpdateClient
def test_invalid_hash_rejected():
 r=UpdateRelease("1.0",UpdateChannel.STABLE,"now","https://x/a.zip","bad",10,"https://x/notes")
 with pytest.raises(MediaImportError):HttpsUpdateClient()._validate_release(r)
