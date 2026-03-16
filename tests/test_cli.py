import sys
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from isekai_live.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_parser_requires_command(self) -> None:
        parser = build_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_build_requires_cover_and_video(self) -> None:
        parser = build_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(["build"])

    def test_main_build_reports_missing_dependency(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "cover.jpg"
            video = Path(tmpdir) / "clip.mov"
            cover.write_bytes(b"cover")
            video.write_bytes(b"video")
            stderr = StringIO()

            with patch("isekai_live.cli.ensure_dependencies", side_effect=RuntimeError("missing exiftool")):
                exit_code = main(
                    [
                        "build",
                        "--cover",
                        str(cover),
                        "--video",
                        str(video),
                        "--output-dir",
                        str(Path(tmpdir) / "out"),
                    ],
                    stderr=stderr,
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("missing exiftool", stderr.getvalue())

    def test_main_build_prints_generated_paths_on_success(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "cover.jpg"
            video = Path(tmpdir) / "clip.mov"
            output_dir = Path(tmpdir) / "out"
            cover.write_bytes(b"cover")
            video.write_bytes(b"video")
            stdout = StringIO()

            artifacts = SimpleNamespace(
                paired_image=output_dir / "livephoto.jpg",
                paired_video=output_dir / "livephoto.mov",
                asset_id="asset-id",
                pvt_package=output_dir / "livephoto.pvt",
            )

            with patch("isekai_live.cli.ensure_dependencies"):
                with patch("isekai_live.cli.build_live_photo", return_value=artifacts):
                    exit_code = main(
                        [
                            "build",
                            "--cover",
                            str(cover),
                            "--video",
                            str(video),
                            "--output-dir",
                            str(output_dir),
                        ],
                        stdout=stdout,
                    )

        self.assertEqual(exit_code, 0)
        self.assertIn("livephoto.jpg", stdout.getvalue())
        self.assertIn("livephoto.mov", stdout.getvalue())
        self.assertIn("livephoto.pvt", stdout.getvalue())

    def test_main_extract_reports_missing_input(self) -> None:
        stderr = StringIO()

        exit_code = main(
            ["extract", "--input", "/nonexistent.jpg", "--output-dir", "/tmp/out"],
            stderr=stderr,
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("not found", stderr.getvalue())

    def test_main_extract_prints_extracted_paths_on_success(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "photo.jpg"
            paired_video = Path(tmpdir) / "photo.mov"
            output_dir = Path(tmpdir) / "out"
            input_file.write_bytes(b"fake image")
            paired_video.write_bytes(b"fake video")
            stdout = StringIO()

            artifacts = SimpleNamespace(
                paired_image=input_file,
                paired_video=paired_video,
                asset_id="extracted-asset-id",
            )

            with patch("isekai_live.cli.ensure_dependencies"):
                with patch("isekai_live.cli.extract_live_photo_pair", return_value=artifacts):
                    exit_code = main(
                        ["extract", "--input", str(input_file), "--output-dir", str(output_dir)],
                        stdout=stdout,
                    )

        self.assertEqual(exit_code, 0)
        self.assertIn("cover", stdout.getvalue())
        self.assertIn("video", stdout.getvalue())
        self.assertIn("extracted-asset-id", stdout.getvalue())

    def test_main_remix_prints_remixed_paths_on_success(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "photo.jpg"
            paired_video = Path(tmpdir) / "photo.mov"
            output_dir = Path(tmpdir) / "out"
            input_file.write_bytes(b"fake image")
            paired_video.write_bytes(b"fake video")
            stdout = StringIO()

            extract_artifacts = SimpleNamespace(
                paired_image=input_file,
                paired_video=paired_video,
                asset_id="original-asset-id",
            )
            remix_artifacts = SimpleNamespace(
                paired_image=output_dir / "livephoto.jpg",
                paired_video=output_dir / "livephoto.mov",
                asset_id="new-asset-id",
                pvt_package=output_dir / "livephoto.pvt",
            )

            with patch("isekai_live.cli.ensure_dependencies"):
                with patch("isekai_live.cli.extract_live_photo_pair", return_value=extract_artifacts):
                    with patch("isekai_live.cli.build_live_photo", return_value=remix_artifacts):
                        exit_code = main(
                            [
                                "remix",
                                "--input",
                                str(input_file),
                                "--output-dir",
                                str(output_dir),
                            ],
                            stdout=stdout,
                        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Remixed Image", stdout.getvalue())
        self.assertIn("Remixed Video", stdout.getvalue())
        self.assertIn("new-asset-id", stdout.getvalue())

    def test_main_remix_keeps_asset_id_when_requested(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "photo.jpg"
            paired_video = Path(tmpdir) / "photo.mov"
            output_dir = Path(tmpdir) / "out"
            input_file.write_bytes(b"fake image")
            paired_video.write_bytes(b"fake video")
            stdout = StringIO()

            extract_artifacts = SimpleNamespace(
                paired_image=input_file,
                paired_video=paired_video,
                asset_id="original-asset-id",
            )
            remix_artifacts = SimpleNamespace(
                paired_image=output_dir / "livephoto.jpg",
                paired_video=output_dir / "livephoto.mov",
                asset_id="original-asset-id",
                pvt_package=output_dir / "livephoto.pvt",
            )

            with patch("isekai_live.cli.ensure_dependencies"):
                with patch("isekai_live.cli.extract_live_photo_pair", return_value=extract_artifacts):
                    with patch("isekai_live.cli.build_live_photo", return_value=remix_artifacts) as build_mock:
                        exit_code = main(
                            [
                                "remix",
                                "--input",
                                str(input_file),
                                "--output-dir",
                                str(output_dir),
                                "--keep-asset-id",
                            ],
                            stdout=stdout,
                        )

            build_mock.assert_called_once()
            call_args = build_mock.call_args
            self.assertEqual(call_args.kwargs.get("asset_id"), "original-asset-id")
        self.assertEqual(exit_code, 0)

    def test_main_ai_cover_reports_generated_output_on_success(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "photo.jpg"
            output_file = Path(tmpdir) / "generated.png"
            input_file.write_bytes(b"fake image")
            stdout = StringIO()

            with patch("isekai_live.cli.ensure_dependencies"):
                with patch("isekai_live.cli.generate_cover", return_value=output_file):
                    exit_code = main(
                        [
                            "ai-cover",
                            "--input",
                            str(input_file),
                            "--prompt",
                            "cartoon portrait",
                            "--provider",
                            "qwen",
                            "--output",
                            str(output_file),
                            "--qwen-key",
                            "sk-test",
                        ],
                        stdout=stdout,
                    )

        self.assertEqual(exit_code, 0)
        self.assertIn("Generated AI cover", stdout.getvalue())
        self.assertIn("Provider: qwen", stdout.getvalue())
