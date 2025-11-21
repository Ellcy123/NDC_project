"""
直接使用ffmpeg命令行合并音频并添加停顿
"""

import json
import os
import subprocess

def load_config():
    config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    dialogues = load_config()
    ffmpeg_path = r"D:\Chrome_downloads\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

    print("Loop1 Opening - Merge with Pauses (Direct ffmpeg)")
    print("=" * 60)

    # 创建文件列表
    concat_list_path = r"D:\NDC_project\Audio\concat_list_with_silence.txt"

    with open(concat_list_path, 'w', encoding='utf-8') as f:
        for i, dialogue in enumerate(dialogues, 1):
            scene_path = dialogue['output_path'].replace('/', '\\')
            full_path = os.path.join(r"D:\NDC_project", scene_path)
            filename = dialogue['output_filename']
            audio_file = os.path.normpath(os.path.join(full_path, filename))

            if not os.path.exists(audio_file):
                print(f"[{i}] MISSING: {filename}")
                continue

            # 写入文件路径 (ffmpeg concat格式)
            f.write(f"file '{audio_file}'\n")

            # 在对话之间添加800ms停顿 (最后一个除外)
            if i < len(dialogues):
                f.write("file 'silence800ms.mp3'\n")

            print(f"[{i:2d}/{len(dialogues)}] Added: {filename}")

    # 创建800ms静音文件
    silence_path = r"D:\NDC_project\Audio\silence800ms.mp3"
    print(f"\nCreating 800ms silence file...")

    silence_cmd = [
        ffmpeg_path,
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', '0.8',
        '-q:a', '9',
        '-acodec', 'libmp3lame',
        '-y',
        silence_path
    ]

    try:
        subprocess.run(silence_cmd, check=True, capture_output=True)
        print(f"  [OK] Created: {silence_path}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed to create silence: {e}")
        return

    # 合并所有文件
    output_path = r"D:\NDC_project\Audio\Loop1_Opening_WithPauses.mp3"
    print(f"\nMerging all files...")

    merge_cmd = [
        ffmpeg_path,
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_list_path,
        '-c', 'copy',
        '-y',
        output_path
    ]

    try:
        result = subprocess.run(merge_cmd, check=True, capture_output=True, text=True)
        print(f"  [OK] Merged successfully!")
        print("=" * 60)
        print(f"[SUCCESS] Output: {output_path}")

        # 获取文件大小
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Size: {size_mb:.2f} MB")
        print(f"With 800ms pauses between all dialogues")

    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Merge failed: {e}")
        print(f"stderr: {e.stderr}")

if __name__ == "__main__":
    main()
