from __future__ import annotations


class MediaImportError(RuntimeError):
    """Base error for failures safe to present to an end user."""


class UnsupportedMediaError(MediaImportError):
    """The selected file is outside the supported import policy."""


class MediaProbeError(MediaImportError):
    """The selected file could not be decoded or inspected."""


class DependencyUnavailableError(MediaImportError):
    """A required external runtime dependency is unavailable."""
