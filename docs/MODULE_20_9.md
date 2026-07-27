# Module 20.9 - HTDemucs Segment Compatibility Fix

HTDemucs transformer models support a maximum segment duration of 7.8 seconds. The separation dialog now defaults to and enforces a safe 7-second segment. The controller and runtime independently clamp legacy or external HTDemucs requests, preventing the prior 10-second configuration from reaching Demucs.
