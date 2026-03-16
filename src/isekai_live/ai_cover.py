"""AI cover generation using Qwen and Gemini image generation APIs."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Protocol


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
    
    # TODO: Implement actual Qwen DashScope API call
    # This is a skeleton implementation - users should add their API integration
    # 
    # Example structure for Qwen API:
    # import dashscope
    # from dashscope import ImageSynthesis
    # 
    # dashscope.api_key = api_key
    # response = ImageSynthesis.call(
    #     model='wanx-v1',
    #     prompt=prompt,
    #     image=input_image.as_posix(),
    #     n=1,
    #     size='1024*1024'
    # )
    # 
    # if response.status_code == 200:
    #     result_url = response.output.results[0].url
    #     # Download and save the image
    #     import requests
    #     img_data = requests.get(result_url).content
    #     with open(output_path, 'wb') as f:
    #         f.write(img_data)
    # else:
    #     raise RuntimeError(f"Qwen API error: {response.message}")
    
    raise NotImplementedError(
        "Qwen API integration is a skeleton. "
        "Please implement the DashScope API call in ai_cover.py. "
        "See the TODO comments in the source code for guidance."
    )


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
    
    # TODO: Implement actual Gemini API call
    # This is a skeleton implementation - users should add their API integration
    #
    # Example structure for Gemini API:
    # import google.generativeai as genai
    # from PIL import Image
    # 
    # genai.configure(api_key=api_key)
    # model = genai.GenerativeModel('gemini-pro-vision')
    # 
    # input_img = Image.open(input_image)
    # response = model.generate_content([
    #     prompt,
    #     input_img
    # ])
    # 
    # # Note: Gemini may return image data differently depending on the model
    # # You may need to use Imagen API or handle the response appropriately
    # 
    # # Save the generated image
    # generated_img.save(output_path)
    
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
