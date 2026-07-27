# Module 20.4 - Official Hugging Face Metadata

Model metadata is now resolved with the official `huggingface_hub.get_hf_file_metadata` implementation. This preserves the original `X-Linked-Etag`, size, and signed download location before redirects to CDN/Xet storage. Regular Git files are verified with Git blob SHA-1; LFS/Xet files are verified with raw SHA-256. HTTP 416 recovery remains enabled.
