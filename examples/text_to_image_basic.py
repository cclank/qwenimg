"""
Basic text-to-image generation example.

This example shows the simplest way to generate images using QwenImg.
Only 3 lines of code needed!
"""

from qwenimg import QwenImg

# Initialize client (automatically reads API key from environment)
client = QwenImg()

# Generate a single image - 3 lines total!
image = client.text_to_image("一只可爱的橘猫")

print(f"Image generated and saved! Type: {type(image)}")
print(f"Image size: {image.size}")
print("Check the ./outputs directory for the saved image!")
