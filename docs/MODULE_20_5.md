# Module 20.5 - Properties Dock Startup Fix

Fixes startup failure caused by calling QLabel-only `setTextInteractionFlags` on a `QLineEdit`. Read-only name and path fields now use QLineEdit APIs only; QLabel metadata fields remain mouse-selectable.
