from __future__ import annotations

from enum import IntEnum


class WorkspacePage(IntEnum):
    """Stable indexes for the primary workspace stack."""

    STUDIO = 0
    LYRICS = 1
    BATCH = 2
    HISTORY = 3
    SETTINGS = 4
    PLUGINS = 5
    RENDER_SETTINGS = 6
    VISUAL_STYLE = 7
