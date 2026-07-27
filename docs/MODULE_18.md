# Module 18 — Updater

Module 18 adds an opt-in updater that checks a configured HTTPS JSON manifest, compares PEP 440 versions, downloads a release package to the application update directory, and verifies exact size plus SHA-256 before atomically publishing the file. It never launches installers, modifies the application, or requests elevation.

Set `KAS_UPDATE_MANIFEST_URL` to the release manifest URL and choose **Help > Check for Updates…**. Downloads use `.part` files, support progress and cancellation, enforce a 2 GiB limit, and delete incomplete or mismatched packages. Before manual installation, users should inspect the Windows publisher signature. Production Windows packages should be Authenticode-signed or distributed as signed MSIX packages.
