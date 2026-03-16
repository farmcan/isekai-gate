"""AI video stylization using Qwen video-style-transform."""

from __future__ import annotations

import json
import time
from enum import Enum
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


QWEN_VIDEO_MODEL = "video-style-transform"
QWEN_VIDEO_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
QWEN_UPLOAD_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/uploads"
QWEN_TASK_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
QWEN_TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELED"}


class VideoStyle(str, Enum):
    """Supported preset styles for Qwen video-style-transform."""

    ANIME = "anime"
    US_COMIC = "us-comic"
    FRESH = "fresh"
    THREE_D_CARTOON = "3d-cartoon"
    CHINESE_CARTOON = "chinese-cartoon"
    PAPER_ART = "paper-art"
    ILLUSTRATION = "illustration"
    INK = "ink"

    @property
    def dashscope_style(self) -> int:
        return {
            VideoStyle.ANIME: 0,
            VideoStyle.US_COMIC: 1,
            VideoStyle.FRESH: 2,
            VideoStyle.THREE_D_CARTOON: 3,
            VideoStyle.CHINESE_CARTOON: 4,
            VideoStyle.PAPER_ART: 5,
            VideoStyle.ILLUSTRATION: 6,
            VideoStyle.INK: 7,
        }[self]


def generate_stylized_video_qwen(
    input_video: Path | str,
    output_path: Path,
    style: VideoStyle,
    api_key: str,
    resolution: int = 540,
    fps: int = 15,
) -> Path:
    """Generate a stylized video using Qwen video-style-transform."""
    video_url = _resolve_video_input(api_key, input_video)
    payload = {
        "model": QWEN_VIDEO_MODEL,
        "input": {"video_url": video_url},
        "parameters": {
            "style": style.dashscope_style,
            "video_fps": fps,
            "min_len": resolution,
        },
    }
    response = _dashscope_request_json(
        QWEN_VIDEO_ENDPOINT,
        api_key=api_key,
        payload=payload,
        extra_headers={"X-DashScope-OssResourceResolve": "enable"} if video_url.startswith("oss://") else None,
    )
    task_id = _extract_task_id(response)
    result = _poll_task(task_id, api_key=api_key)
    result_url = _extract_video_result_url(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(_download_binary(result_url))
    return output_path


def _resolve_video_input(api_key: str, input_video: Path | str) -> str:
    if isinstance(input_video, Path):
        return _upload_file_get_oss_url(api_key, QWEN_VIDEO_MODEL, input_video)
    if input_video.startswith(("http://", "https://", "oss://")):
        return input_video
    return _upload_file_get_oss_url(api_key, QWEN_VIDEO_MODEL, Path(input_video))


def _upload_file_get_oss_url(api_key: str, model_name: str, file_path: Path) -> str:
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError("Uploading local videos requires the 'requests' package to be installed.") from exc
    policy = _get_upload_policy(api_key, model_name)
    file_name = file_path.name
    key = f"{policy['upload_dir']}/{file_name}"
    with file_path.open("rb") as handle:
        files = {
            "OSSAccessKeyId": (None, policy["oss_access_key_id"]),
            "Signature": (None, policy["signature"]),
            "policy": (None, policy["policy"]),
            "x-oss-object-acl": (None, policy["x_oss_object_acl"]),
            "x-oss-forbid-overwrite": (None, policy["x_oss_forbid_overwrite"]),
            "key": (None, key),
            "success_action_status": (None, "200"),
            "file": (file_name, handle),
        }
        response = requests.post(policy["upload_host"], files=files, timeout=120)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to upload video to DashScope temporary storage: {response.text}")
    return f"oss://{key}"


def _get_upload_policy(api_key: str, model_name: str) -> dict:
    params = urlencode({"action": "getPolicy", "model": model_name})
    request = Request(
        f"{QWEN_UPLOAD_ENDPOINT}?{params}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["data"]
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Failed to get upload policy with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to get upload policy: {exc.reason}") from exc


def _dashscope_request_json(url: str, *, api_key: str, payload: dict | None, extra_headers: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "X-DashScope-Async": "enable",
    }
    if extra_headers:
        headers.update(extra_headers)
    data = None
    method = "GET"
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
        method = "POST"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Qwen video API request failed with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Qwen video API request failed: {exc.reason}") from exc


def _extract_task_id(response: dict) -> str:
    output = response.get("output", {})
    task_id = output.get("task_id")
    if not task_id:
        raise RuntimeError(f"Qwen video API did not return a task_id: {response}")
    return str(task_id)


def _poll_task(task_id: str, *, api_key: str, max_attempts: int = 90, poll_interval: float = 2.0) -> dict:
    task_url = QWEN_TASK_ENDPOINT.format(task_id=task_id)
    for attempt in range(max_attempts):
        response = _dashscope_request_json(task_url, api_key=api_key, payload=None)
        output = response.get("output", {})
        status = output.get("task_status")
        if status in QWEN_TERMINAL_STATES:
            if status != "SUCCEEDED":
                message = output.get("message") or response.get("message") or f"task status={status}"
                raise RuntimeError(f"Qwen video stylization failed: {message}")
            return response
        if attempt < max_attempts - 1:
            time.sleep(poll_interval)
    raise RuntimeError(f"Qwen video stylization timed out waiting for task {task_id}")


def _extract_video_result_url(response: dict) -> str:
    output = response.get("output", {})
    result_url = output.get("output_video_url")
    if result_url:
        return str(result_url)
    results = output.get("results") or []
    if results:
        first_result = results[0]
        candidate = first_result.get("url") or first_result.get("output_video_url")
        if candidate:
            return str(candidate)
    raise RuntimeError(f"Qwen video task result did not contain a video URL: {response}")


def _download_binary(url: str) -> bytes:
    request = Request(url, method="GET")
    try:
        with urlopen(request, timeout=120) as response:
            return response.read()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Failed to download generated video with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to download generated video: {exc.reason}") from exc
