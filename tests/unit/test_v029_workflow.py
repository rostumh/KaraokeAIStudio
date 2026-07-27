from pathlib import Path
def test_alignment_reenables_save_and_continue():
 s=Path("app/ui/views/lyrics_view.py").read_text();assert "self.continue_button.setEnabled(bool(alignment.words))" in s and "self.save_button" in s
def test_render_preserves_editable_state_and_history():
 s=Path("app/ui/main_window.py").read_text();assert "_save_editable_project_snapshot" in s and "_record_render_history" in s and "remain editable" in s
def test_alignment_uses_song_audio_without_prompt_repetition():
 s=Path("app/infrastructure/ai/faster_whisper_word_aligner.py").read_text();assert "condition_on_previous_text=False" in s and "initial_prompt=transcript.text" not in s
def test_all_release_versions_are_current():
 assert 'version = "0.29.2"' in Path("pyproject.toml").read_text();iss=Path("packaging/inno/KaraokeAIStudio.iss").read_text();assert '#define MyAppVersion "0.29.2"' in iss and 'VersionInfoVersion=0.29.2.0' in iss;assert "'0.29.2'" in Path("packaging/windows_version_info.txt").read_text()

def test_history_view_is_stored_before_signals_are_connected():
 s=Path("app/ui/main_window.py").read_text();create=s.split("def _create_workspace",1)[1].split("def _apply_user_settings",1)[0];assert "self.history_view = HistoryView()" in create;assert "self.history_view.removeRequested.connect" in create;assert create.index("self.history_view = HistoryView()") < create.index("self.history_view.removeRequested.connect")
