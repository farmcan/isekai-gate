"""Helpers for exporting short demo media from a cover image and video."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def export_demo_media(
    cover_image: Path,
    source_video: Path,
    output_mp4: Path,
    output_gif: Path | None = None,
    hold_seconds: float = 1.2,
    gif_width: int = 480,
) -> tuple[Path, Path | None]:
    """Export a demo MP4 and optional GIF that previews the cover before playing the video."""
    _require_media_tools()
    width, height = _probe_video_size(source_video)
    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    _render_demo_mp4(cover_image, source_video, output_mp4, hold_seconds, width, height)
    if output_gif is not None:
        output_gif.parent.mkdir(parents=True, exist_ok=True)
        _render_demo_gif(output_mp4, output_gif, gif_width)
    return output_mp4, output_gif


def _require_media_tools() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("export-demo requires both 'ffmpeg' and 'ffprobe' to be installed.")


def _probe_video_size(source_video: Path) -> tuple[int, int]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=width,height",
            "-of",
            "default=noprint_wrappers=1",
            str(source_video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = dict(line.split("=", 1) for line in result.stdout.strip().splitlines() if "=" in line)
    return int(lines["width"]), int(lines["height"])


def _render_demo_mp4(
    cover_image: Path,
    source_video: Path,
    output_mp4: Path,
    hold_seconds: float,
    width: int,
    height: int,
) -> None:
    filter_complex = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1,format=yuv420p[v0];"
        f"[1:v]fps=15,scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1,format=yuv420p[v1];"
        f"[v0][v1]concat=n=2:v=1:a=0[v]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            str(hold_seconds),
            "-i",
            str(cover_image),
            "-i",
            str(source_video),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            str(output_mp4),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _render_demo_gif(source_mp4: Path, output_gif: Path, gif_width: int) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source_mp4),
            "-vf",
            f"fps=10,scale={gif_width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(output_gif),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
