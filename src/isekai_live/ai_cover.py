"""AI cover generation using Qwen and Gemini image generation APIs."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import time
from enum import Enum
from pathlib import Path
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


QWEN_IMAGE_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
QWEN_TASK_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
QWEN_MODEL = "wanx2.1-imageedit"
QWEN_FUNCTION = "stylization_all"
QWEN_TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELED"}


class AIProvider(str, Enum):
    """Supported AI image generation providers."""
    QWEN = "qwen"
    GEMINI = "gemini"


class AICoverGenerator(Protocol):
    """Protocol for AI cover generators."""
    
    def generate_cover(self, input_image: Path, prompt: str, output_path: Path) -> Path:
        """Generate a new cover image from an input image and prompt.
        
        Args:
            input_image: Path to the input image.
            prompt: Text prompt describing the desired style/transformation.
            output_path: Path where the generated image should be saved.
            
        Returns:
            Path to the generated cover image.
        """
        ...


def get_api_key(provider: AIProvider, cli_key: str | None = None) -> str:
    """Get API key from CLI argument or environment variable.
    
    Args:
        provider: The AI provider (qwen or gemini).
        cli_key: API key provided via CLI argument (optional).
        
    Returns:
        The API key string.
        
    Raises:
        RuntimeError: If no API key is provided.
    """
    if cli_key:
        return cli_key
    
    env_var = f"{provider.value.upper()}_API_KEY"
    api_key = os.environ.get(env_var)
    
    if not api_key:
        raise RuntimeError(
            f"No API key provided for {provider.value.upper()}. "
            f"Use --{provider.value}-key flag or set {env_var} environment variable."
        )
    
    return api_key


def generate_cover_qwen(
    input_image: Path,
    prompt: str,
    output_path: Path,
    api_key: str | None = None,
) -> Path:
    """Generate a new cover using Qwen (Alibaba DashScope) API.
    
    Args:
        input_image: Path to the input image.
        prompt: Text prompt describing the desired style.
        output_path: Path where the generated image should be saved.
        api_key: Qwen API key (optional, will use env var if not provided).
        
    Returns:
        Path to the generated cover image.
        
    Raises:
        RuntimeError: If API key is missing or generation fails.
        NotImplementedError: If the API implementation is not yet complete.
    """
    api_key = api_key or get_api_key(AIProvider.QWEN)
    create_payload = {
        "model": QWEN_MODEL,
        "input": {
            "function": QWEN_FUNCTION,
            "prompt": prompt,
            "base_image_url": _encode_image_as_data_url(input_image),
        },
        "parameters": {},
    }
    response = _dashscope_post_json(QWEN_IMAGE_ENDPOINT, api_key=api_key, payload=create_payload)
    task_id = _extract_qwen_task_id(response)
    result = _poll_qwen_task(task_id, api_key=api_key)
    result_url = _extract_qwen_result_url(result)
    output_path.write_bytes(_download_binary(result_url))
    return output_path


def generate_cover_gemini(
    input_image: Path,
    prompt: str,
    output_path: Path,
    api_key: str | None = None,
) -> Path:
    """Generate a new cover using Gemini (Google Generative AI) API.
    
    Args:
        input_image: Path to the input image.
        prompt: Text prompt describing the desired style.
        output_path: Path where the generated image should be saved.
        api_key: Gemini API key (optional, will use env var if not provided).
        
    Returns:
        Path to the generated cover image.
        
    Raises:
        RuntimeError: If API key is missing or generation fails.
        NotImplementedError: If the API implementation is not yet complete.
    """
    api_key = api_key or get_api_key(AIProvider.GEMINI)
    
    raise NotImplementedError(
        "Gemini API integration is a skeleton. "
        "Please implement the Google Generative AI API call in ai_cover.py. "
        "See the TODO comments in the source code for guidance."
    )


def generate_cover(
    input_image: Path,
    prompt: str,
    output_path: Path,
    provider: AIProvider,
    qwen_key: str | None = None,
    gemini_key: str | None = None,
) -> Path:
    """Generate a new cover image using the specified AI provider.
    
    Args:
        input_image: Path to the input image.
        prompt: Text prompt describing the desired style/transformation.
        output_path: Path where the generated image should be saved.
        provider: AI provider to use (qwen or gemini).
        qwen_key: Qwen API key (optional).
        gemini_key: Gemini API key (optional).
        
    Returns:
        Path to the generated cover image.
        
    Raises:
        RuntimeError: If generation fails.
        ValueError: If unsupported provider is specified.
    """
    if not input_image.is_file():
        raise RuntimeError(f"Input image not found: {input_image}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if provider == AIProvider.QWEN:
        return generate_cover_qwen(
            input_image=input_image,
            prompt=prompt,
            output_path=output_path,
            api_key=qwen_key,
        )
    elif provider == AIProvider.GEMINI:
        return generate_cover_gemini(
            input_image=input_image,
            prompt=prompt,
            output_path=output_path,
            api_key=gemini_key,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'qwen' or 'gemini'.")


def _encode_image_as_data_url(input_image: Path) -> str:
    mime_type, _ = mimetypes.guess_type(input_image.name)
    if not mime_type:
        mime_type = "application/octet-stream"
    encoded = base64.b64encode(input_image.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _dashscope_post_json(url: str, *, api_key: str, payload: dict | None) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "X-DashScope-Async": "enable",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Qwen API request failed with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Qwen API request failed: {exc.reason}") from exc


def _extract_qwen_task_id(response: dict) -> str:
    output = response.get("output", {})
    task_id = output.get("task_id")
    if not task_id:
        raise RuntimeError(f"Qwen API did not return a task_id: {response}")
    return str(task_id)


def _poll_qwen_task(task_id: str, *, api_key: str, max_attempts: int = 60, poll_interval: float = 2.0) -> dict:
    task_url = QWEN_TASK_ENDPOINT.format(task_id=task_id)
    for attempt in range(max_attempts):
        response = _dashscope_post_json(task_url, api_key=api_key, payload=None)
        output = response.get("output", {})
        status = output.get("task_status")
        if status in QWEN_TERMINAL_STATES:
            if status != "SUCCEEDED":
                message = output.get("message") or response.get("message") or f"task status={status}"
                raise RuntimeError(f"Qwen image generation failed: {message}")
            return response
        if attempt < max_attempts - 1:
            time.sleep(poll_interval)
    raise RuntimeError(f"Qwen image generation timed out waiting for task {task_id}")


def _extract_qwen_result_url(response: dict) -> str:
    output = response.get("output", {})
    results = output.get("results") or []
    if not results:
        raise RuntimeError(f"Qwen task completed without image results: {response}")
    first_result = results[0]
    result_url = first_result.get("url") or first_result.get("output_image_url")
    if not result_url:
        raise RuntimeError(f"Qwen task result did not contain an image URL: {response}")
    return str(result_url)


def _download_binary(url: str) -> bytes:
    request = Request(url, method="GET")
    try:
        with urlopen(request, timeout=120) as response:
            return response.read()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Failed to download generated image with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to download generated image: {exc.reason}") from exc
