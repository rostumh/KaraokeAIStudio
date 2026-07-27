from pathlib import Path
from app.infrastructure.models.model_catalog import load_model_catalog
def test_catalog_is_pinned_and_https():
 models=load_model_catalog(Path("models/model-catalog.json"));assert models and all(m.base_url.startswith("https://") and len(m.revision)==40 for m in models)
