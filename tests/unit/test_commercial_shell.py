from pathlib import Path

def test_toolbar_contains_only_core_actions():
    source=Path('app/ui/main_window.py').read_text(encoding='utf-8')
    body=source.split('def _create_toolbar',1)[1].split('def _create_workspace',1)[0]
    for name in ('new_action','open_action','save_action','undo_action','redo_action','settings_action','about_action'):
        assert name in body
    for name in ('separate_action','extract_action','subtitle_action','render_video_action','publishing_action'):
        assert name not in body

def test_auto_and_professional_modes_exist():
    source=Path('app/ui/widgets/creation_wizard.py').read_text(encoding='utf-8')
    assert 'Auto Mode — recommended' in source
    assert 'Professional Mode' in source
    assert 'Create Karaoke Video' in source

def test_seven_step_workflow_is_complete():
    source=Path('app/domain/models/workflow.py').read_text(encoding='utf-8')
    for step in ('IMPORT','SEPARATE','LYRICS','REVIEW','STYLE','RENDER','EXPORT'):
        assert step in source

def test_no_placeholders_in_new_refactor_files():
    for name in ('app/domain/models/workflow.py','app/ui/widgets/workflow_header.py','app/ui/widgets/creation_wizard.py','app/ui/views/studio_view.py'):
        source=Path(name).read_text(encoding='utf-8')
        assert 'TODO' not in source
        assert 'NotImplemented' not in source
        assert ':pass' not in source.replace(' ','')
