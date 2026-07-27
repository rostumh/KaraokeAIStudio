from pathlib import Path


def test_lazy_final_export_controller_is_initialized_before_close_event():
    source = Path("app/ui/main_window.py").read_text(encoding="utf-8")
    init = source.split("def __init__", 1)[1].split("def _create_actions", 1)[0]
    close = source.split("def closeEvent", 1)[1]
    assert "self._final_export_controller = None" in init
    assert "self._final_export_dialog = None" in init
    assert 'getattr(self, "_final_export_controller", None)' in close
