from pathlib import Path
import pytest
from app.application.errors import MediaImportError
from app.infrastructure.translation.argos_translator import ArgosTextTranslator
def test_model_extension_validation(tmp_path):
 a=object.__new__(ArgosTextTranslator);p=tmp_path/"model.zip";p.write_bytes(b"x")
 with pytest.raises(MediaImportError):a.install_model(p)
