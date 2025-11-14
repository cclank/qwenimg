"""
Text-to-video generation example.

This example shows how to generate videos directly from text prompts.
"""

from qwenimg import QwenImg

# Initialize client
client = QwenImg()

# Example 1: Basic text-to-video
print("Example 1: Basic text-to-video generation...")
video_url = client.text_to_video(
    prompt="一只可爱的柴犬在草地上奔跑，阳光明媚，春天，高品质",
    duration=10,
    resolution="1080P"
)
print(f"✅ Video generated!")
print(f"📹 Video URL: {video_url}")

# Example 2: Detailed cinematic prompt
print("\nExample 2: Cinematic video with detailed prompt...")
video_url = client.text_to_video(
    prompt="""一个充满动感的都市场景。
    夜晚，霓虹灯闪烁的街道上，一个穿着连帽衫的年轻人在奔跑。
    镜头跟随他的身影，展现城市的繁华与孤独。
    电影级光照，高能量，充满细节。""",
    negative_prompt="模糊、静止、低质量",
    resolution="1080P",
    duration=10,
    seed=12345
)
print(f"✅ Cinematic video generated!")
print(f"📹 Video URL: {video_url}")

# Example 3: Nature scene
print("\nExample 3: Beautiful nature scene...")
video_url = client.text_to_video(
    prompt="""美丽的日落场景，金色的阳光洒在平静的湖面上。
    微风吹过，湖面泛起涟漪。
    远处的山脉在晚霞中若隐若现。
    宁静、祥和的氛围，4K超清画质。""",
    resolution="1080P",
    duration=10
)
print(f"✅ Nature video generated!")
print(f"📹 Video URL: {video_url}")

# Example 4: Short 5-second video
print("\nExample 4: Quick 5-second video...")
video_url = client.text_to_video(
    prompt="烟花在夜空中绽放，五彩缤纷",
    duration=5,  # 5 seconds
    resolution="720P"
)
print(f"✅ Short video generated!")
print(f"📹 Video URL: {video_url}")

# Example 5: Different resolutions comparison
print("\nExample 5: Generate same video in different resolutions...")
prompt = "一朵玫瑰缓缓绽放，延时摄影效果"
for resolution in ["480P", "720P", "1080P"]:
    video_url = client.text_to_video(
        prompt=prompt,
        duration=5,
        resolution=resolution,
        seed=12345  # Same seed for comparison
    )
    print(f"  {resolution}: {video_url}")

print("\n✅ All examples completed!")
print("💡 Tip: You can download the videos using the URLs above")
