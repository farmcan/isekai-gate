import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from isekai_live.demo_media import export_demo_media


class DemoMediaTests(unittest.TestCase):
    def test_export_demo_media_runs_ffprobe_then_ffmpeg_for_mp4_and_gif(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "cover.jpg"
            video = Path(tmpdir) / "video.mp4"
            output_mp4 = Path(tmpdir) / "demo.mp4"
            output_gif = Path(tmpdir) / "demo.gif"
            cover.write_bytes(b"cover")
            video.write_bytes(b"video")

            commands: list[list[str]] = []

            def fake_run(cmd, **kwargs):
                commands.append(cmd)

                class Result:
                    stdout = "width=704\nheight=536\n"
                    stderr = ""

                return Result()

            with patch("isekai_live.demo_media.shutil.which", return_value="/opt/homebrew/bin/ffmpeg"):
                with patch("isekai_live.demo_media.subprocess.run", side_effect=fake_run):
                    export_demo_media(
                        cover_image=cover,
                        source_video=video,
                        output_mp4=output_mp4,
                        output_gif=output_gif,
                    )

        self.assertEqual(commands[0][0], "ffprobe")
        self.assertEqual(commands[1][0], "ffmpeg")
        self.assertIn(str(output_mp4), commands[1])
        self.assertEqual(commands[2][0], "ffmpeg")
        self.assertIn(str(output_gif), commands[2])

    def test_export_demo_media_raises_when_ffmpeg_missing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "cover.jpg"
            video = Path(tmpdir) / "video.mp4"
            output_mp4 = Path(tmpdir) / "demo.mp4"
            cover.write_bytes(b"cover")
            video.write_bytes(b"video")

            with patch("isekai_live.demo_media.shutil.which", return_value=None):
                with self.assertRaises(RuntimeError) as exc:
                    export_demo_media(
                        cover_image=cover,
                        source_video=video,
                        output_mp4=output_mp4,
                    )

        self.assertIn("ffmpeg", str(exc.exception))
