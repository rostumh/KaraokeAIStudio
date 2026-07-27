from app.ui.formatters import format_bytes, format_duration

def test_format_duration_includes_hours_and_milliseconds() -> None:
    assert format_duration(3661.125) == "01:01:01.125"

def test_format_bytes_uses_binary_units() -> None:
    assert format_bytes(1536) == "1.50 KiB"
