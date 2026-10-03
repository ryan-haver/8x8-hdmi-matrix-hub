"""Apply a profile's desired state for recall and scene steps (DI-11).

Macros belong to the caller's sequence. A scene override skips a write and
leaves that setting unchanged; disabled outputs still receive their state.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from config import Profile

_LOG = logging.getLogger("profile_execution")


@dataclass
class ProfileStateResult:
    applied: list[str] = field(default_factory=list)
    failed_outputs: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


async def apply_profile_state(
    profile: Profile, matrix_device: Any, skip: dict[int, set[str]] | None = None,
) -> ProfileStateResult:
    """Apply exactly the stored output state, checking each device answer."""
    result = ProfileStateResult()
    for output_num, cfg in sorted(profile.outputs.items()):
        skipped = (skip or {}).get(output_num, set())
        writes = [
            ("input", f"route input {cfg.input}", matrix_device.switch_input, (cfg.input, output_num)),
            ("enabled", "stream on" if cfg.enabled else "stream off",
             matrix_device.set_output_enable, (output_num, cfg.enabled)),
            ("audio_mute", "mute" if cfg.audio_mute else "unmute",
             matrix_device.set_output_audio_mute, (output_num, cfg.audio_mute)),
        ]
        if cfg.hdr_mode is not None:
            writes.append(("hdr", f"HDR {cfg.hdr_mode}", matrix_device.set_output_hdr, (output_num, cfg.hdr_mode)))
        if cfg.hdcp_mode is not None:
            writes.append(("hdcp", f"HDCP {cfg.hdcp_mode}", matrix_device.set_output_hdcp, (output_num, cfg.hdcp_mode)))
        failed = []
        for key, what, setter, args in writes:
            if key in skipped:
                continue
            try:
                ok = await setter(*args)
            except Exception as exc:
                _LOG.error("Profile %s output %d %s failed: %s", profile.id, output_num, what, exc)
                ok = False
            if not ok:
                failed.append(what)
        if failed:
            result.failed_outputs.append(output_num)
            result.errors.append(f"output {output_num}: {', '.join(failed)} not applied")
        else:
            result.applied.append(f"Output {output_num} → Input {cfg.input}")
    return result
