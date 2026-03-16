import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from isekai_live.live_photo import (
    LivePhotoArtifacts,
    build_live_photo,
    extract_live_photo_pair,
    generate_asset_id,
    write_live_photo_pair,
)


class LivePhotoTests(unittest.TestCase):
    def test_generate_asset_id_returns_uuid_text(self) -> None:
        asset_id = generate_asset_id()

        self.assertEqual(len(asset_id), 36)
        self.assertEqual(asset_id.count("-"), 4)

    def test_build_live_photo_uses_expected_output_paths(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            with patch("isekai_live.live_photo.write_live_photo_pair") as writer:
                artifacts = build_live_photo(
                    cover_image=Path(tmpdir) / "cover.jpg",
                    source_video=Path(tmpdir) / "source.mov",
                    output_dir=output_dir,
                    asset_id="12345678-1234-1234-1234-123456789abc",
                )

        self.assertEqual(artifacts.asset_id, "12345678-1234-1234-1234-123456789abc")
        self.assertEqual(artifacts.paired_image, output_dir / "livephoto.jpg")
        self.assertEqual(artifacts.paired_video, output_dir / "livephoto.mov")
        self.assertEqual(artifacts.pvt_package, output_dir / "livephoto.pvt")
        writer.assert_called_once()

    def test_build_live_photo_converts_png_cover_to_jpeg_output(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            with patch("isekai_live.live_photo.write_live_photo_pair") as writer:
                artifacts = build_live_photo(
                    cover_image=Path(tmpdir) / "cover.png",
                    source_video=Path(tmpdir) / "source.mov",
                    output_dir=output_dir,
                    asset_id="12345678-1234-1234-1234-123456789abc",
                )

        self.assertEqual(artifacts.paired_image, output_dir / "livephoto.jpg")
        writer.assert_called_once()

    def test_write_live_photo_pair_copies_inputs_and_calls_makelive(self) -> None:
        plan = LivePhotoArtifacts(
            source_image=Path("cover.jpg"),
            source_video=Path("source.mov"),
            asset_id="id",
            paired_image=Path("image.jpg"),
            paired_video=Path("video.mov"),
            pvt_package=Path("livephoto.pvt"),
        )

        with patch("isekai_live.live_photo.shutil.copy2") as copy_mock:
            with patch("isekai_live.live_photo.makelive.make_live_photo") as make_mock:
                with patch("isekai_live.live_photo.makelive.save_live_photo_pair_as_pvt") as pvt_mock:
                    write_live_photo_pair(plan)

        self.assertEqual(copy_mock.call_count, 2)
        make_mock.assert_called_once_with(plan.paired_image, plan.paired_video, asset_id="id")
        pvt_mock.assert_called_once_with(plan.paired_image, plan.paired_video, plan.pvt_package.parent, "id")

    def test_write_live_photo_pair_converts_png_cover_before_makelive(self) -> None:
        plan = LivePhotoArtifacts(
            source_image=Path("cover.png"),
            source_video=Path("source.mov"),
            asset_id="id",
            paired_image=Path("image.jpg"),
            paired_video=Path("video.mov"),
            pvt_package=Path("livephoto.pvt"),
        )

        with patch("isekai_live.live_photo._copy_or_convert_cover_image") as cover_mock:
            with patch("isekai_live.live_photo.shutil.copy2") as copy_mock:
                with patch("isekai_live.live_photo.makelive.make_live_photo") as make_mock:
                    with patch("isekai_live.live_photo.makelive.save_live_photo_pair_as_pvt") as pvt_mock:
                        write_live_photo_pair(plan)

        cover_mock.assert_called_once_with(Path("cover.png"), Path("image.jpg"))
        copy_mock.assert_called_once_with(Path("source.mov"), Path("video.mov"))
        make_mock.assert_called_once_with(Path("image.jpg"), Path("video.mov"), asset_id="id")
        pvt_mock.assert_called_once_with(Path("image.jpg"), Path("video.mov"), Path("."), "id")

    def test_extract_live_photo_pair_raises_on_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            extract_live_photo_pair(Path("/nonexistent/file.jpg"))

    def test_extract_live_photo_pair_raises_on_unsupported_extension(self) -> None:
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            with self.assertRaises(ValueError):
                extract_live_photo_pair(test_file)

    def test_extract_live_photo_pair_raises_when_no_paired_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "photo.jpg"
            cover.write_bytes(b"fake image")

            with self.assertRaises(RuntimeError):
                extract_live_photo_pair(cover)

    def test_extract_live_photo_pair_finds_pair_from_image(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "photo.jpg"
            video = Path(tmpdir) / "photo.mov"
            cover.write_bytes(b"fake image")
            video.write_bytes(b"fake video")

            with patch("isekai_live.live_photo.is_live_photo_pair", return_value="test-asset-id"):
                artifacts = extract_live_photo_pair(cover)

            self.assertEqual(artifacts.paired_image, cover)
            self.assertEqual(artifacts.paired_video, video)
            self.assertEqual(artifacts.asset_id, "test-asset-id")

    def test_extract_live_photo_pair_finds_pair_from_video(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cover = Path(tmpdir) / "photo.jpg"
            video = Path(tmpdir) / "photo.mov"
            cover.write_bytes(b"fake image")
            video.write_bytes(b"fake video")

            with patch("isekai_live.live_photo.is_live_photo_pair", return_value="test-asset-id"):
                artifacts = extract_live_photo_pair(video)

            self.assertEqual(artifacts.paired_image, cover)
            self.assertEqual(artifacts.paired_video, video)
            self.assertEqual(artifacts.asset_id, "test-asset-id")
