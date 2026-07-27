import json
from pathlib import Path
from app.domain.models.translation import *
from app.infrastructure.repositories.translation_repository import TranslationRepository
def test_unicode_translation_persistence(tmp_path:Path):
 d=TranslationDocument(tmp_path/"song.wav","en","ja","Test",(TranslatedLine(0,0,1,"Hello","こんにちは"),));p=TranslationRepository().save(d,tmp_path);assert json.loads(p.read_text(encoding="utf-8"))["lines"][0]["translated_text"]=="こんにちは"
