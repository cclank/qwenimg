"""
Main client class for QwenImg.
"""

import os
from typing import Optional, Union, List
from pathlib import Path
from http import HTTPStatus
import dashscope
from dashscope import ImageSynthesis, VideoSynthesis
from PIL import Image
import requests
from io import BytesIO

from .config import (
    BEIJING_ENDPOINT,
    DEFAULT_T2I_MODEL,
    DEFAULT_I2V_MODEL,
    DEFAULT_T2V_MODEL,
    DEFAULT_SIZE,
    DEFAULT_RESOLUTION,
    DEFAULT_DURATION,
    DEFAULT_OUTPUT_DIR,
    T2I_MODELS,
    I2V_MODELS,
    T2V_MODELS,
)
from .utils import (
    get_api_key,
    prepare_image_url,
    download_image,
    format_size,
)


class QwenImg:
    """
    Simple and elegant client for Alibaba Cloud Qwen Image and Video Generation.

    Examples:
        Basic usage (3 lines):

        >>> from qwenimg import QwenImg
        >>> client = QwenImg()
        >>> image = client.text_to_image("一只可爱的猫")

        Advanced usage:

        >>> image = client.text_to_image(
        ...     prompt="一只可爱的猫",
        ...     model="wan2.5-t2i-preview",
        ...     size="1024*1024",
        ...     n=4,
        ...     seed=12345
        ... )

        >>> video_url = client.image_to_video(
        ...     image="cat.png",
        ...     prompt="猫在奔跑",
        ...     duration=10
        ... )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = BEIJING_ENDPOINT,
        region: str = "beijing",
    ):
        """
        Initialize QwenImg client.

        Args:
            api_key: DashScope API key. If not provided, will try to get from
                    DASHSCOPE_API_KEY environment variable or .env file.
            endpoint: API endpoint URL. Default is Beijing endpoint.
            region: Region ("beijing" or "singapore"). Default is "beijing".
        """
        self.api_key = get_api_key(api_key)

        # Set endpoint based on region
        if region.lower() == "singapore":
            dashscope.base_http_api_url = SINGAPORE_ENDPOINT
        else:
            dashscope.base_http_api_url = endpoint

    def text_to_image(
        self,
        prompt: str,
        model: str = DEFAULT_T2I_MODEL,
        negative_prompt: str = "",
        n: int = 1,
        size: str = DEFAULT_SIZE,
        seed: Optional[int] = None,
        prompt_extend: bool = True,
        watermark: bool = False,
        save: bool = True,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        return_pil: bool = True,
    ) -> Union[Image.Image, List[Image.Image], List[str]]:
        """
        Generate images from text prompt.

        Args:
            prompt: Text description of the image to generate
            model: Model to use (default: wan2.5-t2i-preview)
            negative_prompt: What to avoid in the image
            n: Number of images to generate (1-4)
            size: Image size like "1024*1024", "720*1280", "1280*720"
            seed: Random seed for reproducibility
            prompt_extend: Whether to automatically expand prompt
            watermark: Whether to add watermark
            save: Whether to save images to disk
            output_dir: Directory to save images
            return_pil: Whether to return PIL.Image objects (True) or file paths (False)

        Returns:
            If n=1 and return_pil=True: Single PIL.Image object
            If n>1 and return_pil=True: List of PIL.Image objects
            If return_pil=False: List of saved file paths

        Examples:
            >>> client = QwenImg()
            >>> image = client.text_to_image("一只可爱的猫")
            >>> images = client.text_to_image("美丽的风景", n=4)
        """
        # Validate model
        if model not in T2I_MODELS:
            raise ValueError(f"Unsupported model: {model}. Supported models: {list(T2I_MODELS.keys())}")

        # Format size
        size = format_size(size)

        # Validate batch size
        max_batch = T2I_MODELS[model]["max_batch"]
        if n < 1 or n > max_batch:
            raise ValueError(f"n must be between 1 and {max_batch}")

        # Prepare parameters
        params = {
            "api_key": self.api_key,
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "n": n,
            "size": size,
            "prompt_extend": prompt_extend,
            "watermark": watermark,
        }

        if seed is not None:
            params["seed"] = seed

        # Call API
        response = ImageSynthesis.call(**params)

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(
                f"Failed to generate image. Status: {response.status_code}, "
                f"Code: {response.code}, Message: {response.message}"
            )

        # Process results
        results = []
        saved_paths = []

        for result in response.output.results:
            image_url = result.url

            # Download image
            image_data = requests.get(image_url).content

            # Convert to PIL Image
            if return_pil:
                pil_image = Image.open(BytesIO(image_data))
                results.append(pil_image)

            # Save to disk
            if save:
                saved_path = download_image(image_url, output_dir)
                saved_paths.append(saved_path)
                if not return_pil:
                    results.append(saved_path)

        # Return results
        if return_pil:
            return results[0] if n == 1 else results
        else:
            return results

    def image_to_video(
        self,
        image: str,
        model: str = DEFAULT_I2V_MODEL,
        prompt: str = "",
        negative_prompt: str = "",
        audio: Optional[str] = None,
        resolution: str = DEFAULT_RESOLUTION,
        duration: int = DEFAULT_DURATION,
        seed: Optional[int] = None,
        watermark: bool = False,
        use_base64: bool = False,
    ) -> str:
        """
        Generate video from image.

        Args:
            image: Path to image file, URL, or base64 data URI
            model: Model to use (default: wan2.5-i2v-preview)
            prompt: Text description to guide video generation
            negative_prompt: What to avoid in the video
            audio: Path to audio file or URL (optional)
            resolution: Video resolution ("480P", "720P", "1080P")
            duration: Video duration in seconds (5 or 10)
            seed: Random seed for reproducibility
            watermark: Whether to add watermark
            use_base64: Whether to encode local images as base64

        Returns:
            URL of the generated video

        Examples:
            >>> client = QwenImg()
            >>> video_url = client.image_to_video("cat.png", prompt="猫在奔跑")
            >>> video_url = client.image_to_video("cat.png", duration=10, resolution="1080P")
        """
        # Validate model
        if model not in I2V_MODELS:
            raise ValueError(f"Unsupported model: {model}. Supported models: {list(I2V_MODELS.keys())}")

        # Validate resolution
        supported_resolutions = I2V_MODELS[model]["supported_resolutions"]
        if resolution not in supported_resolutions:
            raise ValueError(f"Unsupported resolution: {resolution}. Supported: {supported_resolutions}")

        # Validate duration
        supported_durations = I2V_MODELS[model]["supported_durations"]
        if duration not in supported_durations:
            raise ValueError(f"Unsupported duration: {duration}. Supported: {supported_durations}")

        # Prepare image URL
        img_url = prepare_image_url(image, use_base64)

        # Prepare parameters
        params = {
            "api_key": self.api_key,
            "model": model,
            "img_url": img_url,
            "resolution": resolution,
            "duration": duration,
            "watermark": watermark,
        }

        if prompt:
            params["prompt"] = prompt

        if negative_prompt:
            params["negative_prompt"] = negative_prompt

        if audio:
            params["audio_url"] = prepare_image_url(audio, use_base64)

        if seed is not None:
            params["seed"] = seed

        # Call API
        response = VideoSynthesis.call(**params)

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(
                f"Failed to generate video. Status: {response.status_code}, "
                f"Code: {response.code}, Message: {response.message}"
            )

        return response.output.video_url

    def text_to_video(
        self,
        prompt: str,
        model: str = DEFAULT_T2V_MODEL,
        negative_prompt: str = "",
        resolution: str = DEFAULT_RESOLUTION,
        duration: int = DEFAULT_DURATION,
        seed: Optional[int] = None,
        watermark: bool = False,
    ) -> str:
        """
        Generate video from text prompt.

        Args:
            prompt: Text description of the video to generate
            model: Model to use (default: wan2.5-t2v-preview)
            negative_prompt: What to avoid in the video
            resolution: Video resolution ("480P", "720P", "1080P")
            duration: Video duration in seconds (5 or 10)
            seed: Random seed for reproducibility
            watermark: Whether to add watermark

        Returns:
            URL of the generated video

        Examples:
            >>> client = QwenImg()
            >>> video_url = client.text_to_video("一只猫在草地上奔跑")
            >>> video_url = client.text_to_video("美丽的日落", duration=10, resolution="1080P")
        """
        # Validate model
        if model not in T2V_MODELS:
            raise ValueError(f"Unsupported model: {model}. Supported models: {list(T2V_MODELS.keys())}")

        # Validate resolution
        supported_resolutions = T2V_MODELS[model]["supported_resolutions"]
        if resolution not in supported_resolutions:
            raise ValueError(f"Unsupported resolution: {resolution}. Supported: {supported_resolutions}")

        # Validate duration
        supported_durations = T2V_MODELS[model]["supported_durations"]
        if duration not in supported_durations:
            raise ValueError(f"Unsupported duration: {duration}. Supported: {supported_durations}")

        # Prepare parameters
        params = {
            "api_key": self.api_key,
            "model": model,
            "prompt": prompt,
            "resolution": resolution,
            "duration": duration,
            "watermark": watermark,
        }

        if negative_prompt:
            params["negative_prompt"] = negative_prompt

        if seed is not None:
            params["seed"] = seed

        # Call API
        response = VideoSynthesis.call(**params)

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(
                f"Failed to generate video. Status: {response.status_code}, "
                f"Code: {response.code}, Message: {response.message}"
            )

        return response.output.video_url

    @staticmethod
    def list_models(model_type: str = "all") -> dict:
        """
        List all supported models.

        Args:
            model_type: Type of models to list ("t2i", "i2v", "t2v", or "all")

        Returns:
            Dictionary of supported models
        """
        if model_type == "t2i":
            return T2I_MODELS
        elif model_type == "i2v":
            return I2V_MODELS
        elif model_type == "t2v":
            return T2V_MODELS
        else:
            return {
                "text_to_image": T2I_MODELS,
                "image_to_video": I2V_MODELS,
                "text_to_video": T2V_MODELS,
            }
