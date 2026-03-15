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
