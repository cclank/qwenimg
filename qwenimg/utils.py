"""
Utility functions for QwenImg.
"""

import os
import base64
import mimetypes
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests


def get_api_key(api_key: Optional[str] = None) -> str:
    """
    Get API key from parameter, environment variable, or .env file.

    Args:
        api_key: API key passed as parameter

    Returns:
        API key string

    Raises:
        ValueError: If API key is not found
    """
    if api_key:
        return api_key

    # Try environment variable
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if api_key:
        return api_key

    # Try .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DASHSCOPE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    raise ValueError(
        "API key not found. Please set DASHSCOPE_API_KEY environment variable, "
        "create a .env file with DASHSCOPE_API_KEY, or pass api_key parameter.\n"
        "Get your API key at: https://help.aliyun.com/zh/model-studio/get-api-key"
    )


def encode_image_to_base64(file_path: str) -> str:
    """
    Encode image file to base64 data URI.

    Args:
        file_path: Path to image file

    Returns:
        Base64 encoded data URI (data:{mime_type};base64,{data})

    Raises:
        ValueError: If file is not a supported image format
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported or unrecognized image format: {file_path}")

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')

    return f"data:{mime_type};base64,{encoded}"


def prepare_image_url(image: str, use_base64: bool = False) -> str:
    """
    Prepare image URL from various input formats.

    Args:
        image: Image path (local file, URL, or base64 data URI)
        use_base64: If True, convert local files to base64

    Returns:
        Prepared image URL/URI
    """
    # Already a data URI
    if image.startswith("data:"):
        return image

    # Already a URL
    if image.startswith(("http://", "https://")):
        return image

    # File path
    path = Path(image)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image}")

    if use_base64:
        return encode_image_to_base64(str(path))
    else:
        # Use file:// protocol
        return f"file://{path.resolve()}"


def download_image(url: str, output_dir: str = "./outputs") -> str:
    """
    Download image from URL.

    Args:
        url: Image URL
        output_dir: Directory to save image

    Returns:
        Path to saved image
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Extract filename from URL
    filename = PurePosixPath(unquote(urlparse(url).path)).parts[-1]
    filepath = Path(output_dir) / filename

    # Download and save
    response = requests.get(url)
    response.raise_for_status()

    with open(filepath, 'wb') as f:
        f.write(response.content)

    return str(filepath)


def format_size(size: str) -> str:
    """
    Format and validate size parameter.

    Args:
        size: Size string like "1024*1024" or "1024x1024"

    Returns:
        Formatted size string with * separator
    """
    size = size.replace("x", "*").replace("X", "*")

    # Validate format
    parts = size.split("*")
    if len(parts) != 2:
        raise ValueError(f"Invalid size format: {size}. Expected format: 1024*1024")

    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError:
        raise ValueError(f"Invalid size format: {size}. Width and height must be integers")

    return f"{width}*{height}"
