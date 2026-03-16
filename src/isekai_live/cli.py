"""CLI entrypoint for isekai_live."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Sequence, TextIO

from .deps import ensure_dependencies, ensure_file_exists
from .live_photo import build_live_photo, extract_live_photo_pair
from .ai_cover import AIProvider, generate_cover


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="isekai-live",
        description="Build, extract, and remix Live Photo-compatible image/video pairs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    
    # build subcommand
    build_parser = subparsers.add_parser("build", help="Build a Live Photo from cover image and video.")
    build_parser.add_argument("--cover", required=True, type=Path, help="Path to the cover image.")
    build_parser.add_argument("--video", required=True, type=Path, help="Path to the source MOV video.")
    build_parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to write the generated pair into.",
    )
    build_parser.add_argument(
        "--asset-id",
        type=str,
        default=None,
        help="Optional asset ID to use (generated if not provided).",
    )
    
    # extract subcommand
    extract_parser = subparsers.add_parser("extract", help="Extract cover and video from an existing Live Photo pair.")
    extract_parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the cover image or video of an existing Live Photo pair.",
    )
    extract_parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to copy the extracted files into.",
    )
    
    # remix subcommand
    remix_parser = subparsers.add_parser(
        "remix",
        help="Extract from a Live Photo, optionally replace cover/video, and rebuild.",
    )
    remix_parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the cover image or video of an existing Live Photo pair.",
    )
    remix_parser.add_argument(
        "--new-cover",
        type=Path,
        default=None,
        help="Optional new cover image to replace the extracted one.",
    )
    remix_parser.add_argument(
        "--new-video",
        type=Path,
        default=None,
        help="Optional new video to replace the extracted one.",
    )
    remix_parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to write the remixed pair into.",
    )
    remix_parser.add_argument(
        "--keep-asset-id",
        action="store_true",
        default=False,
        help="Keep the original asset ID (default: generate new ID).",
    )
    
    # ai-cover subcommand
    ai_cover_parser = subparsers.add_parser(
        "ai-cover",
        aliases=["generate-cover"],
        help="Generate a new Live Photo cover using AI image generation.",
    )
    ai_cover_parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the input image (existing Live Photo cover).",
    )
    ai_cover_parser.add_argument(
        "--prompt",
        required=True,
        type=str,
        help="Text prompt describing the desired style (e.g., 'anime style portrait', 'oil painting', 'watercolor', 'pixel art').",
    )
    ai_cover_parser.add_argument(
        "--provider",
        required=True,
        type=str,
        choices=["qwen", "gemini"],
        help="AI provider to use for image generation.",
    )
    ai_cover_parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to save the generated cover image.",
    )
    ai_cover_parser.add_argument(
        "--qwen-key",
        type=str,
        default=None,
        help="Qwen (Alibaba DashScope) API key. Can also use QWEN_API_KEY environment variable.",
    )
    ai_cover_parser.add_argument(
        "--gemini-key",
        type=str,
        default=None,
        help="Gemini (Google Generative AI) API key. Can also use GEMINI_API_KEY environment variable.",
    )
    
    return parser


def cmd_build(args, out_stream, stream) -> int:
    """Handle the build subcommand."""
    ensure_dependencies()
    ensure_file_exists(args.cover, "Cover image")
    ensure_file_exists(args.video, "Source video")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = build_live_photo(args.cover, args.video, args.output_dir, asset_id=args.asset_id)
    out_stream.write(f"Image: {artifacts.paired_image}\n")
    out_stream.write(f"Video: {artifacts.paired_video}\n")
    out_stream.write(f"Package: {artifacts.pvt_package}\n")
    out_stream.write(f"Asset ID: {artifacts.asset_id}\n")
    return 0


def cmd_extract(args, out_stream, stream) -> int:
    """Handle the extract subcommand."""
    ensure_dependencies()
    ensure_file_exists(args.input, "Live Photo input")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    artifacts = extract_live_photo_pair(args.input)
    
    # Copy extracted files to output directory
    output_cover = args.output_dir / f"cover{artifacts.paired_image.suffix}"
    output_video = args.output_dir / f"video{artifacts.paired_video.suffix}"
    shutil.copy2(artifacts.paired_image, output_cover)
    shutil.copy2(artifacts.paired_video, output_video)
    
    out_stream.write(f"Extracted cover: {output_cover}\n")
    out_stream.write(f"Extracted video: {output_video}\n")
    out_stream.write(f"Asset ID: {artifacts.asset_id}\n")
    return 0


def cmd_remix(args, out_stream, stream) -> int:
    """Handle the remix subcommand."""
    ensure_dependencies()
    ensure_file_exists(args.input, "Live Photo input")
    
    if args.new_cover:
        ensure_file_exists(args.new_cover, "New cover image")
    if args.new_video:
        ensure_file_exists(args.new_video, "New video")
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract the original Live Photo pair
    artifacts = extract_live_photo_pair(args.input)
    
    # Determine which files to use for rebuilding
    final_cover = args.new_cover if args.new_cover else artifacts.paired_image
    final_video = args.new_video if args.new_video else artifacts.paired_video
    
    # Determine asset ID
    asset_id = artifacts.asset_id if args.keep_asset_id else None
    
    # Build the new Live Photo
    new_artifacts = build_live_photo(final_cover, final_video, args.output_dir, asset_id=asset_id)
    
    out_stream.write(f"Remixed Image: {new_artifacts.paired_image}\n")
    out_stream.write(f"Remixed Video: {new_artifacts.paired_video}\n")
    out_stream.write(f"Package: {new_artifacts.pvt_package}\n")
    out_stream.write(f"Asset ID: {new_artifacts.asset_id}\n")
    return 0


def cmd_ai_cover(args, out_stream, stream) -> int:
    """Handle the ai-cover subcommand."""
    ensure_dependencies()
    ensure_file_exists(args.input, "Input image")
    
    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Map provider string to enum
    provider = AIProvider(args.provider)
    
    try:
        generated_path = generate_cover(
            input_image=args.input,
            prompt=args.prompt,
            output_path=args.output,
            provider=provider,
            qwen_key=args.qwen_key,
            gemini_key=args.gemini_key,
        )
        out_stream.write(f"Generated AI cover: {generated_path}\n")
        out_stream.write(f"Provider: {provider.value}\n")
        out_stream.write(f"Prompt: {args.prompt}\n")
        return 0
    except NotImplementedError as exc:
        stream.write(f"{exc}\n")
        stream.write(
            "\nTo use this feature, please implement the API integration in src/isekai_live/ai_cover.py\n"
            "See the TODO comments in the source code for guidance on Qwen/Gemini API usage.\n"
        )
        return 1
    except RuntimeError as exc:
        stream.write(f"{exc}\n")
        return 1


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
        if args.command == "build":
            return cmd_build(args, out_stream, stream)
        elif args.command == "extract":
            return cmd_extract(args, out_stream, stream)
        elif args.command == "remix":
            return cmd_remix(args, out_stream, stream)
        elif args.command in ("ai-cover", "generate-cover"):
            return cmd_ai_cover(args, out_stream, stream)
        else:
            stream.write(f"Unknown command: {args.command}\n")
            return 1
    except RuntimeError as exc:
        stream.write(f"{exc}\n")
        return 1
    except OSError as exc:
        stream.write(f"Command execution failed: {exc}\n")
        return 1
    except FileNotFoundError as exc:
        stream.write(f"{exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
