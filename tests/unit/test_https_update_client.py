import pytest
from app.application.errors import MediaImportError
from app.infrastructure.update.https_update_client import HttpsUpdateClient
def test_rejects_http_url():
 with pytest.raises(MediaImportError):HttpsUpdateClient._require_https("http://example.com/update.json","manifest")
def test_rejects_embedded_credentials():
 with pytest.raises(MediaImportError):HttpsUpdateClient._require_https("https://user:pass@example.com/u","manifest")
