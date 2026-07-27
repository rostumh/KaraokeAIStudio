from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLabel, QSpinBox, QVBoxLayout

from app.domain.models.karaoke_effects import KaraokeEffect, KaraokeEffectSettings
from app.ui.widgets.karaoke_effect_preview import KaraokeEffectPreview


class KaraokeEffectDialog(QDialog):
    settingsApplied = Signal(object)

    def __init__(self, current: KaraokeEffectSettings, parent: object = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Karaoke Effects")
        self.setMinimumWidth(600)
        self.effect = QComboBox()
        for label, value in (
            ("Classic Fill — stepped syllable fill", KaraokeEffect.CLASSIC),
            ("Smooth Sweep — progressive fill", KaraokeEffect.SMOOTH_SWEEP),
            ("Outline Pulse — outline highlight", KaraokeEffect.OUTLINE),
            ("Word Pop — sweep with timed scale", KaraokeEffect.POP),
            ("Neon Glow — smooth fill with blur", KaraokeEffect.GLOW),
        ):
            self.effect.addItem(label, value.value)
        self.effect.setCurrentIndex(max(0, self.effect.findData(current.effect.value)))
        self.fade_in = QSpinBox(); self.fade_in.setRange(0, 2000); self.fade_in.setValue(current.fade_in_ms); self.fade_in.setSuffix(" ms")
        self.fade_out = QSpinBox(); self.fade_out.setRange(0, 2000); self.fade_out.setValue(current.fade_out_ms); self.fade_out.setSuffix(" ms")
        self.pop_scale = QSpinBox(); self.pop_scale.setRange(100, 160); self.pop_scale.setValue(current.pop_scale_percent); self.pop_scale.setSuffix(" %")
        self.glow_blur = QDoubleSpinBox(); self.glow_blur.setRange(0, 10); self.glow_blur.setValue(current.glow_blur); self.glow_blur.setSingleStep(.5)
        self.glow_outline = QDoubleSpinBox(); self.glow_outline.setRange(0, 12); self.glow_outline.setValue(current.glow_outline); self.glow_outline.setSingleStep(.5)
        self.preview = KaraokeEffectPreview()
        form = QFormLayout()
        form.addRow("Effect preset", self.effect)
        form.addRow("Line fade in", self.fade_in)
        form.addRow("Line fade out", self.fade_out)
        form.addRow("Pop maximum scale", self.pop_scale)
        form.addRow("Glow blur", self.glow_blur)
        form.addRow("Glow outline", self.glow_outline)
        note = QLabel("The preview is illustrative. Final rendering uses ASS override tags and libass in the video-rendering pipeline.")
        note.setWordWrap(True); note.setObjectName("muted")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Apply).setText("Apply Effect")
        buttons.accepted.connect(self._apply); buttons.rejected.connect(self.reject)
        for widget in (self.effect, self.fade_in, self.fade_out, self.pop_scale, self.glow_blur, self.glow_outline):
            if isinstance(widget, QComboBox): widget.currentIndexChanged.connect(self._refresh)
            else: widget.valueChanged.connect(self._refresh)
        layout = QVBoxLayout(self); layout.addLayout(form); layout.addWidget(self.preview); layout.addWidget(note); layout.addWidget(buttons)
        self._refresh()

    def _settings(self) -> KaraokeEffectSettings:
        return KaraokeEffectSettings(KaraokeEffect(str(self.effect.currentData())), self.fade_in.value(), self.fade_out.value(), self.pop_scale.value(), self.glow_blur.value(), self.glow_outline.value())

    def _refresh(self) -> None:
        self.preview.set_settings(self._settings())
        effect = KaraokeEffect(str(self.effect.currentData()))
        self.pop_scale.setEnabled(effect == KaraokeEffect.POP)
        enabled = effect == KaraokeEffect.GLOW
        self.glow_blur.setEnabled(enabled); self.glow_outline.setEnabled(enabled)

    def _apply(self) -> None:
        settings = self._settings().validate()
        self.settingsApplied.emit(settings)
        self.accept()
