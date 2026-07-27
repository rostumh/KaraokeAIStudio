# Module 20.3 - Git Blob Checksum Fix

Regular Hugging Face Git files use a Git blob SHA-1 object ID: SHA-1 over `blob <size>\0` plus content. LFS files continue to use raw SHA-256. HTTP 416 recovery is retained.
