"""Live Photo asset generation helpers."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import shutil
import uuid

from makelive import makelive, live_id, is_live_photo_pair


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
    paired_image = output_dir / f"livephoto{_paired_image_suffix(cover_image)}"
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
    _copy_or_convert_cover_image(artifacts.source_image, artifacts.paired_image)
    shutil.copy2(artifacts.source_video, artifacts.paired_video)
    makelive.make_live_photo(artifacts.paired_image, artifacts.paired_video, asset_id=artifacts.asset_id)
    makelive.save_live_photo_pair_as_pvt(
        artifacts.paired_image,
        artifacts.paired_video,
        artifacts.pvt_package.parent,
        artifacts.asset_id,
    )


def extract_live_photo_pair(live_photo_path: Path) -> LivePhotoArtifacts:
    """Extract cover image and video from an existing Live Photo pair.
    
    Args:
        live_photo_path: Path to the cover image or video of an existing Live Photo pair.
        
    Returns:
        LivePhotoArtifacts with paths to the extracted cover and video.
        
    Raises:
        RuntimeError: If the file is not part of a valid Live Photo pair.
        FileNotFoundError: If the specified file does not exist.
    """
    if not live_photo_path.is_file():
        raise FileNotFoundError(f"Live Photo file not found: {live_photo_path}")
    
    # Determine the paired file based on the input file extension
    stem = live_photo_path.stem
    parent = live_photo_path.parent
    suffix = live_photo_path.suffix.lower()
    
    # Check if input is image or video
    is_image = suffix in (".jpg", ".jpeg", ".heic", ".heif")
    is_video = suffix in (".mov", ".mp4", ".m4v")
    
    if not is_image and not is_video:
        raise ValueError(f"Unsupported file type: {suffix}. Expected image (jpg/jpeg/heic/heif) or video (mov/mp4/m4v)")
    
    # Find the paired file
    if is_image:
        cover_path = live_photo_path
        # Look for video with same stem but video extension
        video_extensions = (".mov", ".mp4", ".m4v")
        video_path = None
        for ext in video_extensions:
            candidate = parent / f"{stem}{ext}"
            if candidate.is_file():
                video_path = candidate
                break
        if video_path is None:
            raise RuntimeError(f"No paired video found for {live_photo_path}")
    else:
        video_path = live_photo_path
        # Look for image with same stem but image extension
        image_extensions = (".jpg", ".jpeg", ".heic", ".heif")
        cover_path = None
        for ext in image_extensions:
            candidate = parent / f"{stem}{ext}"
            if candidate.is_file():
                cover_path = candidate
                break
        if cover_path is None:
            raise RuntimeError(f"No paired cover image found for {live_photo_path}")
    
    # Verify it's a valid Live Photo pair and extract asset ID
    asset_id = is_live_photo_pair(cover_path, video_path)
    if not asset_id:
        raise RuntimeError(f"File pair is not a valid Live Photo: {cover_path}, {video_path}")
    
    # Extract asset ID from the file if is_live_photo_pair returns True but no ID
    if asset_id is True:
        asset_id = live_id(cover_path) or live_id(video_path)
        if not asset_id:
            raise RuntimeError("Could not extract asset ID from Live Photo pair")
    
    return LivePhotoArtifacts(
        source_image=cover_path,
        source_video=video_path,
        asset_id=asset_id,
        paired_image=cover_path,
        paired_video=video_path,
        pvt_package=parent / "livephoto.pvt",
    )


def _paired_image_suffix(source_image: Path) -> str:
    suffix = source_image.suffix.lower()
    if suffix == ".png":
        return ".jpg"
    return suffix


def _copy_or_convert_cover_image(source_image: Path, target_image: Path) -> None:
    if source_image.suffix.lower() == ".png":
        _convert_png_to_jpeg(source_image, target_image)
        return
    shutil.copy2(source_image, target_image)


def _convert_png_to_jpeg(source_image: Path, target_image: Path) -> None:
    if shutil.which("sips") is None:
        raise RuntimeError("PNG cover conversion requires the macOS 'sips' command.")
    try:
        subprocess.run(
            ["sips", "-s", "format", "jpeg", str(source_image), "--out", str(target_image)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Failed to convert PNG cover to JPEG: {exc.stderr.strip()}") from exc
