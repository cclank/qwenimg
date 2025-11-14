"""
Advanced text-to-image generation example.

This example demonstrates all available parameters and customization options.
"""

from qwenimg import QwenImg

# Initialize client
client = QwenImg()

# Example 1: Generate high-quality image with custom parameters
print("Example 1: Detailed prompt with custom settings")
image = client.text_to_image(
    prompt="""一张高精度的数字插画，呈现了一个中心对称的构图。
    画面的核心是一个身穿白色长袍的男性角色，他拥有白皙的皮肤，五官清秀，
    眉心有一点红色朱砂痣。他蓄着及腰的黑色长发，上半部分用一个精致的银色发冠束在脑后。
    整个画面的色调以高明度的白色、浅灰色和温暖的金色为主，营造出一种神圣、空灵的氛围。
    杰作，最高品质，4K，8K，仙侠，古风，数字插画。""",
    negative_prompt="模糊、粗糙、色彩暗淡、风格杂乱",
    model="wan2.5-t2i-preview",
    size="1024*1024",
    seed=12345,  # For reproducibility
    prompt_extend=True,  # Auto-expand prompt
    watermark=False,
    n=1,
    output_dir="./outputs/advanced"
)
print(f"Image 1 saved! Size: {image.size}")

# Example 2: Generate multiple variations
print("\nExample 2: Generate 4 variations")
images = client.text_to_image(
    prompt="一只可爱的柴犬在樱花树下玩耍，春天，阳光明媚，高品质",
    n=4,  # Generate 4 images
    size="1280*720",  # Landscape
    output_dir="./outputs/variations"
)
print(f"Generated {len(images)} images!")
for i, img in enumerate(images, 1):
    print(f"  Image {i}: {img.size}")

# Example 3: Portrait mode
print("\nExample 3: Portrait orientation")
portrait = client.text_to_image(
    prompt="一位优雅的女性肖像，古典油画风格，细腻的光影",
    size="720*1280",  # Portrait
    output_dir="./outputs/portrait"
)
print(f"Portrait image saved! Size: {portrait.size}")

# Example 4: Get file paths instead of PIL images
print("\nExample 4: Return file paths instead of PIL Image objects")
file_paths = client.text_to_image(
    prompt="未来城市，赛博朋克风格，霓虹灯",
    return_pil=False,  # Return file paths
    output_dir="./outputs/cyberpunk"
)
print(f"Saved to: {file_paths}")

# Example 5: Don't save to disk, just return PIL Image for further processing
print("\nExample 5: No saving, just return PIL Image")
img = client.text_to_image(
    prompt="一朵盛开的红玫瑰",
    save=False,  # Don't save to disk
    return_pil=True
)
# Now you can process the image in memory
# img.resize(...), img.filter(...), etc.
print(f"Image object: {type(img)}, size: {img.size}")

print("\n✅ All examples completed!")
