from __future__ import annotations
from pathlib import Path
from threading import Event
from collections.abc import Callable
from app.domain.models.model_package import ModelPackage
from app.infrastructure.models.resumable_downloader import ResumableModelDownloader

Progress=Callable[[int,int,str],None]
class ModelProvisioningService:
    def __init__(self,downloader:ResumableModelDownloader)->None:self.d=downloader
    def missing_required(self,catalog:tuple[ModelPackage,...],models_root:Path)->tuple[ModelPackage,...]:
        missing=[]
        for model in catalog:
            if not model.required:continue
            if any(not self.d.verify(model.base_url+f.name,models_root/model.install_subdir/f.name) for f in model.files):missing.append(model)
        return tuple(missing)
    def provision(self,models:tuple[ModelPackage,...],models_root:Path,progress:Progress,cancel:Event)->None:
        for model in models:
            for f in model.files:
                path=models_root/model.install_subdir/f.name
                if not self.d.verify(model.base_url+f.name,path):self.d.download(model.base_url+f.name,path,progress,cancel)
