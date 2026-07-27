from pathlib import Path
from threading import Event
import pytest
from app.application.errors import MediaImportError
from app.application.services.final_export_service import FinalExportService
from app.domain.models.quality_validation import *
class Validator:
 def validate(self,s,p,c):return MediaQualityReport(s,"now",1,1,"mp4","h264","aac",1920,1080,30,48000,2,(QualityCheck("x",CheckSeverity.PASS,"x","ok"),))
class Repo:
 def save(self,r,d):return d/"r.json"
def test_validates_and_saves_report(tmp_path):
 source=tmp_path/"out.mp4";source.write_bytes(b"video");report,path=FinalExportService(Validator(),Repo()).validate(source,tmp_path,lambda a,b:None,Event());assert report.passed and path.name=="r.json"
def test_rejects_non_video(tmp_path):
 p=tmp_path/"x.txt";p.write_text("x")
 with pytest.raises(MediaImportError):FinalExportService(Validator(),Repo()).validate(p,tmp_path,lambda a,b:None,Event())
