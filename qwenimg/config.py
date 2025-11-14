"""
Configuration and constants for QwenImg.
"""

# API endpoints
BEIJING_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1"
SINGAPORE_ENDPOINT = "https://dashscope-intl.aliyuncs.com/api/v1"

# Supported models
T2I_MODELS = {
    "wan2.5-t2i-preview": {
        "name": "万相2.5文生图预览版",
        "supported_sizes": ["1024*1024", "720*1280", "1280*720"],
        "max_batch": 4,
    },
    "wanx-v1": {
        "name": "通义万相V1",
        "supported_sizes": ["1024*1024", "720*1280", "1280*720"],
        "max_batch": 4,
    },
}

I2V_MODELS = {
    "wan2.5-i2v-preview": {
        "name": "万相2.5图生视频预览版",
        "supported_resolutions": ["480P", "720P", "1080P"],
        "supported_durations": [5, 10],
    },
}

T2V_MODELS = {
    "wan2.5-t2v-preview": {
        "name": "万相2.5文生视频预览版",
        "supported_resolutions": ["480P", "720P", "1080P"],
        "supported_durations": [5, 10],
    },
}

# Default parameters
DEFAULT_T2I_MODEL = "wan2.5-t2i-preview"
DEFAULT_I2V_MODEL = "wan2.5-i2v-preview"
DEFAULT_T2V_MODEL = "wan2.5-t2v-preview"

DEFAULT_SIZE = "1024*1024"
DEFAULT_RESOLUTION = "1080P"
DEFAULT_DURATION = 10
DEFAULT_OUTPUT_DIR = "./outputs"
