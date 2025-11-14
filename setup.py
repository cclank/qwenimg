"""
Setup script for QwenImg.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="qwenimg",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Simple and elegant Python client for Alibaba Cloud Qwen Image and Video Generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/qwenimg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "dashscope>=1.14.0",
        "Pillow>=9.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    keywords="qwen alibaba aliyun image video generation ai ml dashscope",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/qwenimg/issues",
        "Source": "https://github.com/yourusername/qwenimg",
        "Documentation": "https://github.com/yourusername/qwenimg#readme",
    },
)
