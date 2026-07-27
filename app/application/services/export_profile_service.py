from __future__ import annotations

from app.application.errors import MediaImportError
from app.domain.models.export_profile import BUILTIN_EXPORT_PROFILES, ExportProfile
from app.domain.models.video_render import RenderEncoder, VideoCodec, VideoContainer


class ExportProfileService:
    """Validates, merges, and resolves built-in, user, and plugin render profiles."""

    @staticmethod
    def validate(profile: ExportProfile) -> ExportProfile:
        if not profile.profile_id or not profile.name.strip():
            raise MediaImportError("Export profile ID and name are required.")
        if (profile.width, profile.height) not in {(1280, 720), (1920, 1080), (3840, 2160)}:
            raise MediaImportError("Export profile uses an unsupported resolution.")
        if profile.frame_rate not in {24, 25, 30, 50, 60}:
            raise MediaImportError("Export profile uses an unsupported frame rate.")
        if not 0 <= profile.quality <= 51:
            raise MediaImportError("Export profile quality must be between 0 and 51.")
        if not 96 <= profile.audio_bitrate_kbps <= 512:
            raise MediaImportError("Export profile audio bitrate must be between 96 and 512 kbps.")
        return profile

    @staticmethod
    def merge(user_profiles: tuple[ExportProfile, ...], plugin_profiles: dict[str, tuple[str, dict[str, object]]]) -> tuple[ExportProfile, ...]:
        merged = list(BUILTIN_EXPORT_PROFILES)
        seen = {profile.profile_id for profile in merged}
        for profile in user_profiles:
            ExportProfileService.validate(profile)
            if profile.profile_id in seen:
                raise MediaImportError(f"Duplicate export profile ID: {profile.profile_id}")
            merged.append(profile); seen.add(profile.profile_id)
        for profile_id, (label, values) in sorted(plugin_profiles.items()):
            if profile_id in seen:
                continue
            try:
                profile = ExportProfile(
                    profile_id, label, "Provided by an enabled plugin.",
                    VideoCodec(str(values.get("codec", "h264"))),
                    VideoContainer(str(values.get("container", "mp4"))),
                    RenderEncoder.SOFTWARE,
                    int(values.get("width", 1920)), int(values.get("height", 1080)),
                    int(values.get("frame_rate", 30)), int(values.get("quality", 20)),
                    int(values.get("audio_bitrate_kbps", 320)), False,
                )
                merged.append(ExportProfileService.validate(profile)); seen.add(profile_id)
            except (ValueError, TypeError, MediaImportError):
                continue
        return tuple(merged)
