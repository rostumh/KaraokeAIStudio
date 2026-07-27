from pathlib import Path
from app.domain.models.batch import *
from app.infrastructure.repositories.batch_queue_repository import BatchQueueRepository
def test_round_trip_and_recovers_running_as_queued(tmp_path:Path):
 j=BatchJob.create(BatchOperation.EXTRACT_WAV24,tmp_path/"a",tmp_path/"b").update(status=BatchStatus.RUNNING);p=tmp_path/"q.json";r=BatchQueueRepository();r.save((j,),p);loaded=r.load(p);assert loaded[0].status==BatchStatus.QUEUED and loaded[0].job_id==j.job_id
