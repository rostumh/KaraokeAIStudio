from __future__ import annotations
import json
from pathlib import Path
from app.application.errors import MediaImportError
from app.domain.models.model_package import ModelFile,ModelPackage

def load_model_catalog(path:Path)->tuple[ModelPackage,...]:
    try: payload=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: raise MediaImportError(f"Unable to read model catalog: {exc}") from exc
    if payload.get("schema_version")!=1: raise MediaImportError("Unsupported model catalog version.")
    result=[]
    for item in payload.get("models",[]):
        if not str(item.get("base_url","")).startswith("https://"): raise MediaImportError("Model downloads must use HTTPS.")
        result.append(ModelPackage(str(item["model_id"]),str(item["name"]),bool(item["required"]),str(item["license"]),str(item["revision"]),str(item["install_subdir"]),str(item["base_url"]),tuple(ModelFile(str(x["name"])) for x in item["files"])))
    return tuple(result)
