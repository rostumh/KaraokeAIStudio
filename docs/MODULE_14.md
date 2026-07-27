# Module 14 — Batch Processing

Module 14 adds a persistent serial job queue. It currently supports reliable 24-bit/48 kHz WAV extraction and complete final-video quality validation for multiple files. Jobs survive application restart, interrupted RUNNING jobs recover as QUEUED, duplicate active jobs are suppressed, terminal failures can be retried, the current job can be cancelled, and successful/failed history remains visible.

The queue is serial by design to avoid oversubscribing disk, CPU, GPU, FFmpeg decoders, and model memory. Queue state is atomically stored under the application data directory. Output files go to `exports/batch/audio` and `exports/batch/quality`.

Use the **Batch Queue** workspace, select an operation, add files, and start the queue. New jobs appended while the queue is active are processed automatically.
