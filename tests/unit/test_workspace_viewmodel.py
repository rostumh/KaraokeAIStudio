from app.ui.constants import WorkspacePage
from app.ui.viewmodels.workspace_viewmodel import WorkspaceViewModel


def test_navigation_changes_page() -> None:
    view_model = WorkspaceViewModel()
    emitted: list[int] = []
    view_model.pageChanged.connect(emitted.append)
    view_model.select_page(int(WorkspacePage.SETTINGS))
    assert view_model.page == int(WorkspacePage.SETTINGS)
    assert emitted == [int(WorkspacePage.SETTINGS)]


def test_transport_state_is_bounded_and_stoppable() -> None:
    view_model = WorkspaceViewModel()
    view_model.toggle_playback()
    view_model.seek(5000)
    assert view_model.playing is True
    assert view_model.position == 1000
    view_model.stop_playback()
    assert view_model.playing is False
    assert view_model.position == 0
