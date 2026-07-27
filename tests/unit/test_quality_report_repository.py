import json
from pathlib import Path
from app.domain.models.quality_validation import *
from app.infrastructure.repositories.quality_report_repository import QualityReportRepository
def test_report_persists_status(tmp_path:Path):
 r=MediaQualityReport(tmp_path/"x.mp4","now",1,2000,"MP4","h264","aac",1920,1080,30,48000,2,(QualityCheck("decode",CheckSeverity.PASS,"Decode","ok"),));p=QualityReportRepository().save(r,tmp_path);data=json.loads(p.read_text());assert data["passed"] is True and data["checks"][0]["severity"]=="pass"
