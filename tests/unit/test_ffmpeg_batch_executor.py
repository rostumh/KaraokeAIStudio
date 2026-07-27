from pathlib import Path
from app.domain.models.batch import *
from app.infrastructure.batch.ffmpeg_batch_executor import FFmpegBatchJobExecutor
def test_job_output_naming(tmp_path):
 from app.application.services.batch_queue_service import BatchQueueService
 assert BatchQueueService.output_for(tmp_path/"song.mp4",BatchOperation.EXTRACT_WAV24,tmp_path).name=="song_audio.wav"
