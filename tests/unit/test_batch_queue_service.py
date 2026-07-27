from pathlib import Path
import pytest
from app.application.errors import MediaImportError
from app.application.services.batch_queue_service import BatchQueueService
from app.domain.models.batch import *
def test_add_deduplicates_active_jobs(tmp_path):
 s=tmp_path/"a.mp4";s.write_bytes(b"x");jobs=BatchQueueService.add_jobs((),(s,s),BatchOperation.EXTRACT_WAV24,tmp_path/"out");assert len(jobs)==1 and jobs[0].output_path.name=="a_audio.wav"
def test_retry_only_terminal_failure(tmp_path):
 j=BatchJob.create(BatchOperation.VALIDATE_FINAL,tmp_path/"a",tmp_path/"b")
 with pytest.raises(MediaImportError):BatchQueueService.retry(j)
