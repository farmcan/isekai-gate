"""CLI entrypoint for isekai_live."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO

from .deps import ensure_dependencies, ensure_file_exists
from .live_photo import build_live_photo


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="isekai-live",
        description="Build a Live Photo-compatible image/video pair.",
    )
    parser.add_argument("--cover", required=True, type=Path, help="Path to the cover image.")
    parser.add_argument("--video", required=True, type=Path, help="Path to the source MOV video.")
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to write the generated pair into.",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    out_stream = stdout or sys.stdout
    stream = stderr or sys.stderr

    try:
        ensure_dependencies()
        ensure_file_exists(args.cover, "Cover image")
        ensure_file_exists(args.video, "Source video")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        artifacts = build_live_photo(args.cover, args.video, args.output_dir)
    except RuntimeError as exc:
        stream.write(f"{exc}\n")
        return 1
    except OSError as exc:
        stream.write(f"Command execution failed: {exc}\n")
        return 1
    out_stream.write(f"Image: {artifacts.paired_image}\n")
    out_stream.write(f"Video: {artifacts.paired_video}\n")
    out_stream.write(f"Package: {artifacts.pvt_package}\n")
    out_stream.write(f"Asset ID: {artifacts.asset_id}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
