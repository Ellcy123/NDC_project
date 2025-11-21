"""
使用pydub合并音频并添加停顿
需要先安装ffmpeg
"""

import json
import os
from pydub import AudioSegment
from pydub.utils import which

# 设置ffmpeg路径
AudioSegment.converter = r"D:\Chrome_downloads\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"D:\Chrome_downloads\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe"

def load_config():
    config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    dialogues = load_config()

    print("Loop1 Opening - Merge with Pauses")
    print("=" * 60)
    print("This script requires ffmpeg to be installed.")
    print("Download from: https://www.gyan.dev/ffmpeg/builds/")
    print("=" * 60)

    # 创建空音频
    combined = AudioSegment.empty()
    pause_duration = 800  # 800ms停顿

    missing_files = []
    success_count = 0

    for i, dialogue in enumerate(dialogues, 1):
        scene_path = dialogue['output_path'].replace('/', '\\')
        full_path = os.path.join(r"D:\NDC_project", scene_path)
        filename = dialogue['output_filename']
        audio_file = os.path.normpath(os.path.join(full_path, filename))

        scene = dialogue['scene']

        print(f"[{i:2d}/{len(dialogues)}] [{scene:7s}] {filename:20s}", end=" ")

        if not os.path.exists(audio_file):
            print(f"[MISSING] Path: {audio_file}")
            missing_files.append(filename)
            continue

        try:
            # 加载音频片段
            segment = AudioSegment.from_mp3(audio_file)

            # 添加到合并音频
            combined += segment

            # 在对话之间添加停顿(最后一段除外)
            if i < len(dialogues):
                combined += AudioSegment.silent(duration=pause_duration)

            duration_sec = len(segment) / 1000
            print(f"[OK] {duration_sec:.1f}s")
            success_count += 1

        except Exception as e:
            print(f"[ERROR] {e}")
            missing_files.append(filename)

    if success_count == 0:
        print("\n" + "=" * 60)
        print("ERROR: No audio files were loaded successfully.")
        print("This usually means ffmpeg is not installed or not in PATH.")
        print("\nPlease install ffmpeg first:")
        print("1. Download from: https://www.gyan.dev/ffmpeg/builds/")
        print("2. Extract to C:\\ffmpeg\\")
        print("3. Add C:\\ffmpeg\\bin to System PATH")
        print("4. Restart terminal and try again")
        return

    # 导出最终音频
    output_path = r"D:\NDC_project\Audio\Loop1_Opening_WithPauses.mp3"
    print(f"\nExporting to: {output_path}")

    try:
        combined.export(output_path, format="mp3", bitrate="128k")

        print("=" * 60)
        print("[SUCCESS] Audio with pauses created!")
        print(f"Output: {output_path}")
        print(f"Duration: {len(combined) / 1000:.2f}s ({len(combined) / 60000:.2f} min)")
        print(f"Segments: {success_count}/{len(dialogues)}")
        print(f"Pause between dialogues: {pause_duration}ms")

        if missing_files:
            print(f"\nMissing files: {len(missing_files)}")
            for f in missing_files:
                print(f"  - {f}")

    except Exception as e:
        print(f"\n[ERROR] Failed to export: {e}")
        print("\nMake sure ffmpeg is installed correctly.")

if __name__ == "__main__":
    main()
