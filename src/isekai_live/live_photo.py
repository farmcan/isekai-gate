"""Live Photo asset generation helpers."""

from dataclasses import dataclass
from pathlib import Path
import shutil
import uuid

from makelive import makelive


@dataclass(frozen=True)
class LivePhotoArtifacts:
    """Paths and identifiers for a generated Live Photo pair."""

    source_image: Path
    source_video: Path
    asset_id: str
    paired_image: Path
    paired_video: Path
    pvt_package: Path


def generate_asset_id() -> str:
    """Generate a stable text identifier for the image/video pair."""
    return str(uuid.uuid4())


def build_live_photo(
    cover_image: Path,
    source_video: Path,
    output_dir: Path,
    asset_id: str | None = None,
) -> LivePhotoArtifacts:
    """Create the output layout and build a Live Photo pair."""
    resolved_asset_id = asset_id or generate_asset_id()
    paired_image = output_dir / f"livephoto{cover_image.suffix.lower()}"
    paired_video = output_dir / f"livephoto{source_video.suffix.lower()}"
    artifacts = LivePhotoArtifacts(
        source_image=cover_image,
        source_video=source_video,
        asset_id=resolved_asset_id,
        paired_image=paired_image,
        paired_video=paired_video,
        pvt_package=output_dir / "livephoto.pvt",
    )
    write_live_photo_pair(artifacts)
    return artifacts


def write_live_photo_pair(artifacts: LivePhotoArtifacts) -> None:
    """Copy source assets, add Live Photo metadata, and create a Photos package."""
    artifacts.paired_image.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(artifacts.source_image, artifacts.paired_image)
    shutil.copy2(artifacts.source_video, artifacts.paired_video)
    makelive.make_live_photo(artifacts.paired_image, artifacts.paired_video, asset_id=artifacts.asset_id)
    makelive.save_live_photo_pair_as_pvt(
        artifacts.paired_image,
        artifacts.paired_video,
        artifacts.pvt_package.parent,
        artifacts.asset_id,
    )
