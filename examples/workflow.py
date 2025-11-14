"""
Complete workflow example: Text -> Image -> Video

This example demonstrates a complete workflow:
1. Generate an image from text
2. Use that image to generate a video
3. Optionally add audio to the video
"""

from qwenimg import QwenImg
import os

# Initialize client
client = QwenImg()

print("🎨 Starting complete workflow: Text -> Image -> Video")
print("=" * 60)

# Step 1: Generate image from text
print("\n📝 Step 1: Generating image from text prompt...")
prompt_image = """一位身穿白色长袍的古风男子，
眉心有朱砂痣，长发飘逸，
站在云雾缭绕的山间平台上，
背景是金色的圆形光晕，
古风仙侠风格，高品质4K"""

image = client.text_to_image(
    prompt=prompt_image,
    negative_prompt="模糊、粗糙、色彩暗淡",
    size="1024*1024",
    seed=12345,
    output_dir="./outputs/workflow"
)
print("✅ Image generated successfully!")

# Find the generated image file
image_dir = "./outputs/workflow"
image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
image_path = os.path.join(image_dir, image_files[-1])
print(f"📁 Image saved at: {image_path}")

# Step 2: Generate video from the image
print("\n🎬 Step 2: Generating video from the image...")
prompt_video = """严格依据图片生成10秒视频，保持角色特征和场景风格。
([动态分层]，前景的云雾缓缓流动，角色的长发和衣袍随风轻轻摆动。
远景的山峰和金色光晕保持稳定，营造神圣氛围。)
([时间轴分层]，0-3秒：展现整体场景；4-7秒：镜头微微推进，聚焦角色；
8-10秒：镜头缓缓上移，展现天空和光晕。)
([技术参数]，60帧每秒，4K超清画质，保证流畅度。)"""

video_url = client.image_to_video(
    image=image_path,
    prompt=prompt_video,
    negative_prompt="模糊、抖动、失真",
    resolution="1080P",
    duration=10,
    seed=12345
)
print("✅ Video generated successfully!")
print(f"📹 Video URL: {video_url}")

# Step 3: Show summary
print("\n" + "=" * 60)
print("🎉 Workflow completed successfully!")
print("=" * 60)
print(f"\n📸 Image: {image_path}")
print(f"   Size: {image.size}")
print(f"   Format: {image.format}")
print(f"\n📹 Video: {video_url}")
print(f"   Resolution: 1080P")
print(f"   Duration: 10 seconds")

print("\n💡 Next steps:")
print("   1. Download the video from the URL above")
print("   2. View the generated image in the outputs/workflow directory")
print("   3. Use the image for further processing or video generation")

# Optional: Generate another video with different style
print("\n🔄 Bonus: Generating alternative video style...")
video_url_2 = client.image_to_video(
    image=image_path,
    prompt="角色缓缓转身，眼神望向远方，云雾翻涌，充满仙气",
    duration=5,
    resolution="720P"
)
print(f"✅ Alternative video: {video_url_2}")

print("\n✨ All done!")
