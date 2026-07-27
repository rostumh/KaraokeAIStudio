from app.ui.widgets.timeline_widget import TimelineWidget

def test_time_formatting():
    assert TimelineWidget._format_time(0) == "00:00.000"
    assert TimelineWidget._format_time(231876) == "03:51.876"
    assert TimelineWidget._format_time(3723004) == "62:03.004"
