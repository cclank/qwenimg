"""
Image-to-video generation example.

This example shows how to generate videos from images.
"""

from qwenimg import QwenImg
import os

# Initialize client
client = QwenImg()

# First, let's generate an image to use
print("Step 1: Generating an image...")
image = client.text_to_image(
    prompt="一只可爱的橘猫坐在窗台上，背景是美丽的花园",
    output_dir="./outputs/for_video"
)
image_path = "./outputs/for_video"  # The image will be saved here

# Find the generated image file
image_files = [f for f in os.listdir(image_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
if not image_files:
    print("No image found! Please run text_to_image first.")
    exit(1)

image_file = os.path.join(image_path, image_files[-1])  # Use the latest image
print(f"Using image: {image_file}")

# Example 1: Basic image-to-video
print("\nStep 2: Generating video from image (basic)...")
video_url = client.image_to_video(
    image=image_file,
    prompt="橘猫缓缓转头看向窗外，微风吹动它的毛发",
    duration=10,
    resolution="1080P"
)
print(f"✅ Video generated!")
print(f"📹 Video URL: {video_url}")

# Example 2: With more detailed prompt
print("\nExample 2: Detailed prompt for better control...")
video_url = client.image_to_video(
    image=image_file,
    prompt="""([锚定设定]，严格依据图片生成10秒视频，保持橘猫的特征和花园背景。)
    ([动态分层]，橘猫的耳朵轻轻抖动，尾巴缓缓摆动；
    花园中的花朵随微风摇曳；远处的树叶沙沙作响。)
    ([时间轴分层]，0-3秒：橘猫静静坐着；4-7秒：缓缓转头；8-10秒：看向远方。)
    ([技术参数]，帧率60帧每秒，保证流畅度。)""",
    negative_prompt="模糊、抖动、失真、不自然的动作",
    resolution="1080P",
    duration=10,
    seed=12345
)
print(f"✅ Detailed video generated!")
print(f"📹 Video URL: {video_url}")

# Example 3: Different resolutions
print("\nExample 3: Generate videos in different resolutions...")
for resolution in ["480P", "720P", "1080P"]:
    video_url = client.image_to_video(
        image=image_file,
        prompt="橘猫眨眼睛",
        duration=5,
        resolution=resolution
    )
    print(f"  {resolution}: {video_url}")

# Example 4: Using online image URL
print("\nExample 4: Using image from URL...")
# If you have a public image URL, you can use it directly:
# video_url = client.image_to_video(
#     image="https://example.com/your-image.png",
#     prompt="描述视频内容",
#     duration=10
# )

# Example 5: Using base64 encoded image (for private images)
print("\nExample 5: Using base64 encoded image...")
video_url = client.image_to_video(
    image=image_file,
    prompt="橘猫慢慢站起来伸懒腰",
    use_base64=True,  # Encode image as base64
    duration=5
)
print(f"✅ Video with base64 image generated!")
print(f"📹 Video URL: {video_url}")

print("\n✅ All examples completed!")
print("💡 Tip: You can download the videos using the URLs above")
