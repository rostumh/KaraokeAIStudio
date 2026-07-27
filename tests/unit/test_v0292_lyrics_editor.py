from pathlib import Path
from app.application.services.lyrics_realign_service import karaoke_lines, parse_lyrics_file, realign_document
from app.domain.models.lyrics_document import EditableWord, LyricsDocument


def document(words):
    timed=tuple(EditableWord(i, i//7, w, 20+i*.5, 20+(i+1)*.5, .9) for i,w in enumerate(words.split()))
    return LyricsDocument(Path('song.wav'),'en',100,timed,0)


def test_phrase_lines_define_segments_and_fix_reported_boundary_problem():
    old=document("I realize the best part of love is the thinnest slice And it don't count for much But I'm not letting go I believe")
    fixed=realign_document(old,"""I realize the best part of love
is the thinnest slice And it don't count for much
but I'm not letting go
I believe""")
    phrases=[]
    for sid in range(4): phrases.append(' '.join(w.text for w in fixed.words if w.segment_id==sid))
    assert phrases == ["I realize the best part of love", "is the thinnest slice and it don't count for much", "but I'm not letting go", "I believe"]
    # Existing exact words retain acoustic timestamps rather than uniform full-range redistribution.
    assert fixed.words[7].text == 'is' and fixed.words[7].start_seconds == old.words[7].start_seconds


def test_karaoke_normalization_removes_prose_punctuation_and_random_caps():
    assert karaoke_lines("And It DON'T count, for much.\nBut I'M not letting go!") == [["and","it","don't","count","for","much"],["but","I'm","not","letting","go"]]


def test_import_txt_and_lrc_preserve_phrases(tmp_path):
    txt=tmp_path/'lyrics.txt'; txt.write_text('First line.\nSecond line,', encoding='utf-8')
    assert parse_lyrics_file(txt) == 'first line\nsecond line'
    lrc=tmp_path/'lyrics.lrc'; lrc.write_text('[00:01.00]First line\n[00:03.20]Second line', encoding='utf-8')
    assert parse_lyrics_file(lrc) == 'first line\nsecond line'


def test_ui_routes_all_document_edits_through_shared_undo_stack():
    view=Path('app/ui/views/lyrics_view.py').read_text()
    main=Path('app/ui/main_window.py').read_text()
    assert 'ReplaceLyricsDocumentCommand' in view
    assert 'editRequested.connect(self._push_document_edit)' in view
    assert 'canUndoChanged.connect(self.undo_action.setEnabled)' in main
    assert 'canRedoChanged.connect(self.redo_action.setEnabled)' in main
