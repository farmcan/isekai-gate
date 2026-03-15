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
    def test_parser_requires_cover_and_video(self) -> None:
        parser = build_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_main_reports_missing_dependency(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "cover.jpg"
            video = Path(tmpdir) / "clip.mov"
            cover.write_bytes(b"cover")
            video.write_bytes(b"video")
            stderr = StringIO()

            with patch("isekai_live.cli.ensure_dependencies", side_effect=RuntimeError("missing exiftool")):
                exit_code = main(
                    [
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

    def test_main_prints_generated_paths_on_success(self) -> None:
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
