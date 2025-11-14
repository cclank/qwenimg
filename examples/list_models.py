"""
List all supported models and their capabilities.
"""

from qwenimg import QwenImg
import json

client = QwenImg()

# List all models
print("=" * 60)
print("All Supported Models")
print("=" * 60)

all_models = QwenImg.list_models()
print(json.dumps(all_models, indent=2, ensure_ascii=False))

# List specific model types
print("\n" + "=" * 60)
print("Text-to-Image Models")
print("=" * 60)
t2i_models = QwenImg.list_models("t2i")
for model_id, info in t2i_models.items():
    print(f"\n📸 {model_id}")
    print(f"   Name: {info['name']}")
    print(f"   Supported sizes: {', '.join(info['supported_sizes'])}")
    print(f"   Max batch: {info['max_batch']}")

print("\n" + "=" * 60)
print("Image-to-Video Models")
print("=" * 60)
i2v_models = QwenImg.list_models("i2v")
for model_id, info in i2v_models.items():
    print(f"\n🎬 {model_id}")
    print(f"   Name: {info['name']}")
    print(f"   Supported resolutions: {', '.join(info['supported_resolutions'])}")
    print(f"   Supported durations: {info['supported_durations']} seconds")

print("\n" + "=" * 60)
print("Text-to-Video Models")
print("=" * 60)
t2v_models = QwenImg.list_models("t2v")
for model_id, info in t2v_models.items():
    print(f"\n🎥 {model_id}")
    print(f"   Name: {info['name']}")
    print(f"   Supported resolutions: {', '.join(info['supported_resolutions'])}")
    print(f"   Supported durations: {info['supported_durations']} seconds")
