from pathlib import Path


def test_qlineedit_does_not_receive_qlabel_only_interaction_api():
    source = Path("app/ui/widgets/properties_dock.py").read_text(encoding="utf-8")
    line_edit_branch = source.split("if isinstance(value, QLineEdit):", 1)[1].split("else:", 1)[0]
    assert "setReadOnly(True)" in line_edit_branch
    assert "setTextInteractionFlags" not in line_edit_branch


def test_qlabel_remains_mouse_selectable():
    source = Path("app/ui/widgets/properties_dock.py").read_text(encoding="utf-8")
    label_branch = source.split("if isinstance(value, QLineEdit):", 1)[1].split("else:", 1)[1]
    assert "setTextInteractionFlags" in label_branch
    assert "TextSelectableByMouse" in label_branch
