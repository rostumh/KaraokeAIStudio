from pathlib import Path

from app.domain.models.subtitles import (
    SubtitleCue,
    SubtitleDocument,
    SubtitleFormat,
    SubtitleOptions,
    SubtitleStyle,
    SubtitleWord,
)
from app.infrastructure.subtitles.ass_exporter import AssSubtitleExporter
from app.infrastructure.subtitles.lrc_exporter import LrcSubtitleExporter
from app.infrastructure.subtitles.srt_exporter import SrtSubtitleExporter


def document(tmp_path: Path) -> SubtitleDocument:
    words = (SubtitleWord("Hello", 1, 1.5), SubtitleWord("world", 1.5, 2))
    cue = SubtitleCue(1, 1, 2, words)
    options = SubtitleOptions(
        (SubtitleFormat.ASS, SubtitleFormat.SRT, SubtitleFormat.LRC),
        7,
        5,
        0.8,
        0.1,
        0.2,
        1920,
        1080,
        SubtitleStyle(),
    )
    return SubtitleDocument(tmp_path / "song.wav", "en", 10, (cue,), options)


def test_ass_contains_karaoke_tags_and_style(tmp_path: Path) -> None:
    text = AssSubtitleExporter().export(document(tmp_path), tmp_path).read_text()
    assert r"{\kf50}Hello" in text
    assert "Style: Karaoke" in text


def test_srt_uses_millisecond_timestamp(tmp_path: Path) -> None:
    text = SrtSubtitleExporter().export(document(tmp_path), tmp_path).read_text()
    assert "00:00:01,000 --> 00:00:02,000" in text


def test_lrc_uses_centisecond_timestamp(tmp_path: Path) -> None:
    text = LrcSubtitleExporter().export(document(tmp_path), tmp_path).read_text()
    assert "[00:01.00]Hello world" in text
