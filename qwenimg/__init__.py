"""
QwenImg - Simple and elegant Python client for Alibaba Cloud Qwen Image and Video Generation.

Examples:
    Basic usage (3 lines):

    >>> from qwenimg import QwenImg
    >>> client = QwenImg()
    >>> image = client.text_to_image("一只可爱的猫")

    Generate multiple images:

    >>> images = client.text_to_image("美丽的风景", n=4)

    Generate video from image:

    >>> video_url = client.image_to_video("cat.png", prompt="猫在奔跑", duration=10)

    Generate video from text:

    >>> video_url = client.text_to_video("一只猫在草地上奔跑")
"""

from .client import QwenImg
from .config import T2I_MODELS, I2V_MODELS, T2V_MODELS

__version__ = "0.1.0"
__all__ = ["QwenImg", "T2I_MODELS", "I2V_MODELS", "T2V_MODELS"]
