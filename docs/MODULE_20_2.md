# Module 20.2 - HTTP 416 Resume Recovery

A complete partial file is verified without an invalid Range request. HTTP 416 deletes only the stale partial file and retries once as a clean full download. A server that ignores Range and sends HTTP 200 replaces rather than appends the partial file.
